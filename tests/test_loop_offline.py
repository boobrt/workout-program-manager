"""Offline tests of the agent loop's plumbing, using a scripted stand-in for Claude (no API key, no cost).

They prove the harness handles every path correctly. They do NOT test the model's judgment; that's
what live runs + tools/check_proposal.py + the judge checklist are for.

Run: .venv/bin/python tests/test_loop_offline.py
"""
import csv
import json
import shutil
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from agent import verify  # noqa: E402
from agent.loop import ScriptedUI, run  # noqa: E402
from agent.state import Case, RunState  # noqa: E402
from check_proposal import grade  # noqa: E402

QUALITY = [
    ("intervals", "2026-10-06", "17:45", "19:00", 7), ("tempo", "2026-10-08", "06:00", "07:10", 8),
    ("long", "2026-10-10", "07:00", "09:40", 16), ("intervals", "2026-10-13", "17:45", "19:00", 8),
    ("tempo", "2026-10-15", "06:00", "07:10", 8), ("long", "2026-10-17", "07:00", "09:50", 17),
]


def proposal(easy_date_1="2026-10-07", easy_date_2="2026-10-14", start="06:00", end="07:00", rule_ids=("R6",)):
    sessions = [{"session": s, "date": d, "start": a, "end": b, "miles": m, "intensity": "quality"} for s, d, a, b, m in QUALITY]
    sessions += [{"session": "easy", "date": d, "start": start, "end": end, "miles": 6, "intensity": "easy"}
                 for d in (easy_date_1, easy_date_2)]
    return {
        "summary": "Move Wednesday easy runs to 6:00 am, every week through race week.",
        "changes": [{"week": "Week 10", "original": "Wed Oct 7, 5:45 pm, Easy 6 mi", "proposed": f"{easy_date_1} {start}, Easy 6 mi", "change_type": "move"},
                    {"week": "Weeks 11-18", "original": "Wed evening easy runs", "proposed": "Wed 6:00 am", "change_type": "standing_rule"}],
        "reasons": [{"text": "A standing if-then rule for a recurring conflict.", "rule_ids": list(rule_ids)},
                    {"text": "Quality days stay separated by easy days.", "rule_ids": ["B1"]}],
        "tradeoffs": ["Two early mornings in a row (Wed and Thu)."],
        "standing_rule": "If it's Wednesday, run easy at 6:00 am.",
        "assumptions": [],
        "sessions": sessions,
    }


GOOD = proposal()
MONDAY = proposal("2026-10-05", "2026-10-12")          # breaks memory preference (verifier catches)
CLASH = proposal(start="17:45", end="18:45")            # overlaps the pickup (code check catches)
BAD_RULE = proposal(rule_ids=("R9",))                   # cites a rule that doesn't exist


def tool(name, **inp):
    return SimpleNamespace(type="tool_use", id=f"tu_{name}_{id(inp)}", name=name, input=inp)


def turn(*blocks):
    return SimpleNamespace(content=list(blocks), stop_reason="tool_use" if any(b.type == "tool_use" for b in blocks) else "end_turn")


READS = turn(*[tool("read_source", source=s) for s in ("workout_plan", "calendar", "memory", "rules_library", "garmin_wellness")])


class FakeClient:
    """Plays the main agent from a script; plays the verifier by passing only drafts with no code failures and no Monday runs."""

    def __init__(self, main_turns):
        self.main_turns = list(main_turns)
        self.requests = []
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self.create))

    def create(self, **kw):
        self.requests.append({**kw, "messages": list(kw["messages"])})  # snapshot: the loop keeps appending
        if kw["system"] == verify.VERIFIER_SYSTEM:
            payload = json.loads(kw["messages"][0]["content"])
            fails = [c for c in payload["code_check_results"] if c["severity"] == "fail"]
            monday = any(s["date"] in ("2026-10-05", "2026-10-12") for s in payload["draft_proposal"]["sessions"])
            issues = [{"check": "fit", "problem": "Runs on Monday, her protected rest day", "fix": "Use Wed 6 am"}] if monday else []
            verdict = {"verdict": "fail" if (fails or monday) else "pass", "issues": issues, "summary": "fake"}
            return SimpleNamespace(content=[SimpleNamespace(type="text", text=json.dumps(verdict))], stop_reason="end_turn")
        return self.main_turns.pop(0)


def run_case(main_turns, answers=(), decisions=()):
    tmp = Path(tempfile.mkdtemp())
    state = RunState(Case.load("annie"), runs_dir=tmp)
    client = FakeClient(main_turns)
    outcome = run(client, state, ScriptedUI(answers, decisions))
    return outcome, state, client


def calendar_easy_runs(state):
    with (state.data_dir / "calendar.csv").open() as f:
        return sorted((r["Start"], r["Name"]) for r in csv.DictReader(f) if "Easy" in r["Name"])


failures = []


def expect(ok, msg):
    print(("  ok    " if ok else "  FAIL  ") + msg)
    if not ok:
        failures.append(msg)


print("\n1. Happy path: reads, asks 2 questions, first draft fails, redraft passes, user accepts")
outcome, state, client = run_case(
    [READS, turn(tool("ask_user", question="Are Wednesday mornings OK?")),
     turn(tool("ask_user", question="Every Wednesday?")),
     turn(tool("submit_proposal", **MONDAY)), turn(tool("submit_proposal", **GOOD))],
    answers=["Mornings are fine.", "Yes, every week."], decisions=[{"decision": "accept", "feedback": ""}])
expect(outcome == {"status": "accepted", "verified": True, "drafts": 2}, f"outcome {outcome}")
expect(calendar_easy_runs(state) == [("2026-10-07 06:00", "Run: Easy 6 mi"), ("2026-10-14 06:00", "Run: Easy 6 mi")],
       f"calendar now has Wed 6:00 easy runs: {calendar_easy_runs(state)}")
expect("## Approved schedule changes" in (state.data_dir / "workout-plan.md").read_text(), "plan page gets an approved-changes section")
mem = (state.data_dir / "memory.md").read_text()
expect("Mornings are fine." in mem and "first request" not in mem, "memory records the change and her answers")
saved = json.loads((state.dir / "proposal.json").read_text())
expect(all(ok for ok, _ in grade(saved).values()), "saved proposal passes eval graders A1-A6")
original = Path(__file__).resolve().parent.parent / "personas" / "annie" / "calendar.csv"
expect("2026-10-07 06:00" not in original.read_text(), "original persona data is untouched (writes go to the run copy)")
main_reqs = [r for r in client.requests if r["system"] != verify.VERIFIER_SYSTEM]
expect(all(r["model"] == "claude-opus-5-5" and r["fallbacks"] == "default" for r in client.requests), "every request uses Opus 5.5 with fallbacks on")
expect(sum(1 for r in client.requests if r["system"] == verify.VERIFIER_SYSTEM) == 2, "verifier sub-agent ran once per draft")
tool_result = main_reqs[-1]["messages"][-1]["content"][0]["content"]
expect("Monday" in tool_result and "Verification failed (draft 1" in tool_result, "main agent received the verifier's issues for redrafting")

print("\n2. Redraft cap: 3 failing drafts; 3rd goes to the user flagged; user rejects")
outcome, state, client = run_case(
    [READS, turn(tool("submit_proposal", **CLASH)), turn(tool("submit_proposal", **CLASH)), turn(tool("submit_proposal", **CLASH))],
    decisions=[{"decision": "reject", "feedback": ""}])
expect(outcome == {"status": "rejected", "verified": False, "drafts": 3}, f"outcome {outcome}")
expect(calendar_easy_runs(state)[0][0] == "2026-10-07 17:45", "reject leaves the calendar unchanged")
events = json.loads((state.dir / "events.json").read_text())
expect(sum(e["kind"] == "verification" for e in events) == 3, "exactly 3 verifications (1 draft + 2 redrafts)")

print("\n3. Edit: user edits the first proposal, agent resubmits, user accepts")
outcome, state, _ = run_case(
    [READS, turn(tool("submit_proposal", **GOOD)), turn(tool("submit_proposal", **proposal(start="06:15", end="07:15")))],
    decisions=[{"decision": "edit", "feedback": "Make it 6:15, I need a few more minutes."}, {"decision": "accept", "feedback": ""}])
expect(outcome["status"] == "accepted", f"outcome {outcome}")
expect(calendar_easy_runs(state)[0][0] == "2026-10-07 06:15", "edited time was written")

print("\n4. Unknown rule ID is caught by code checks")
checks = verify.deterministic_checks(BAD_RULE, state, __import__("agent.state", fromlist=["load_rules"]).load_rules())
expect(any(c["check"] == "rule ids" and c["severity"] == "fail" for c in checks), "citing R9 fails")

print("\n5. Medical red flag: stop and refer, nothing drafted or written")
outcome, state, _ = run_case([READS, turn(tool("stop_and_refer", reason="swollen ankle", message_to_user="Please see a clinician."))])
expect(outcome == {"status": "referred", "reason": "swollen ankle"}, f"outcome {outcome}")
expect(not (state.dir / "proposal.json").exists() and not (state.dir / "written.json").exists(), "no proposal, no writes")

print(f"\n{'All offline tests passed' if not failures else f'{len(failures)} FAILED'}")
sys.exit(1 if failures else 0)
