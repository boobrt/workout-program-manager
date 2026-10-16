"""Case loading, the per-run working copy of the data, rules lookup, and approved writes."""
import csv
import json
import re
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES_PATH = ROOT / "rules" / "training-rules-library.md"

# read_source name -> file name in the persona folder (rules library lives in /rules)
SOURCES = {
    "workout_plan": "workout-plan.md",
    "calendar": "calendar.csv",
    "garmin_activities": "garmin-activities.csv",
    "garmin_wellness": "garmin-daily-wellness.csv",
    "memory": "memory.md",
}
WORKOUT_NAME = re.compile(r"^Run: (\w+) ([\d.]+) mi$")


@dataclass
class Case:
    case_id: str
    persona: str
    now: str
    message: str
    scripted_answers: list = field(default_factory=list)
    scripted_decisions: list = field(default_factory=list)

    @classmethod
    def load(cls, persona):
        data = json.loads((ROOT / "personas" / persona / "case.json").read_text())
        return cls(persona=persona, **data)


class RunState:
    """A throwaway copy of the persona's data. The agent reads it; approved changes are written to it."""

    def __init__(self, case, runs_dir=ROOT / "runs"):
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.dir = runs_dir / f"{case.case_id}_{stamp}"
        self.data_dir = self.dir / "state"
        shutil.copytree(ROOT / "personas" / case.persona, self.data_dir)
        shutil.copy(RULES_PATH, self.data_dir / "training-rules-library.md")
        self.case = case
        self.events = []

    def read(self, source):
        if source == "rules_library":
            return (self.data_dir / "training-rules-library.md").read_text()
        return (self.data_dir / SOURCES[source]).read_text()

    def log(self, kind, **data):
        self.events.append({"time": datetime.now().isoformat(timespec="seconds"), "kind": kind, **data})

    # ---------- calendar ----------
    def calendar_rows(self):
        with (self.data_dir / "calendar.csv").open() as f:
            return list(csv.DictReader(f))

    def busy_blocks(self):
        return [(_ts(r["Start"]), _ts(r["End"]), r["Name"]) for r in self.calendar_rows() if r["Type"] != "Workout"]

    def planned_runs(self):
        runs = []
        for r in self.calendar_rows():
            m = WORKOUT_NAME.match(r["Name"])
            if r["Type"] == "Workout" and m:
                runs.append({"session": m.group(1).lower(), "start": _ts(r["Start"]), "end": _ts(r["End"]),
                             "miles": float(m.group(2))})
        return runs

    # ---------- approved writes (only called after the user selects Accept) ----------
    def apply_approved(self, proposal, qa_pairs):
        now = self.case.now[:10]
        sessions = proposal["sessions"]
        dates = sorted(s["date"] for s in sessions)
        window = (min(r["start"] for r in self.planned_runs()).date().isoformat(),
                  max(r["start"] for r in self.planned_runs()).date().isoformat())
        rows = [r for r in self.calendar_rows()
                if not (r["Type"] == "Workout" and window[0] <= r["Start"][:10] <= window[1])]
        for s in sessions:
            rows.append({"Name": f"Run: {s['session'].capitalize()} {_miles(s['miles'])} mi",
                         "Start": f"{s['date']} {s['start']}", "End": f"{s['date']} {s['end']}",
                         "Type": "Workout", "Recurring": "Plan",
                         "Notes": f"Approved by user via agent on {now}"})
        rows.sort(key=lambda r: (r["Start"], r["End"]))
        with (self.data_dir / "calendar.csv").open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["Name", "Start", "End", "Type", "Recurring", "Notes"])
            writer.writeheader()
            writer.writerows(rows)

        table = "\n".join(f"| {c['week']} | {c['original']} | {c['proposed']} | {c['change_type']} |"
                          for c in proposal["changes"])
        rule = f"\n**Standing rule:** {proposal['standing_rule']}\n" if proposal["standing_rule"] else ""
        with (self.data_dir / "workout-plan.md").open("a") as f:
            f.write(f"\n## Approved schedule changes ({now})\n{proposal['summary']}\n\n"
                    f"| Week | Original | Proposed | Change |\n|---|---|---|---|\n{table}\n{rule}")

        memory = (self.data_dir / "memory.md").read_text()
        memory = re.sub(r"^- None\. This is .*first request\.\n", "", memory, flags=re.M)
        memory += f"- {now}: {proposal['summary']}" + (f" Standing rule: {proposal['standing_rule']}" if proposal["standing_rule"] else "") + "\n"
        if qa_pairs:
            memory += f"\n## Preferences learned in conversation ({now})\n"
            memory += "".join(f"- Q: {q}\n  A: {a}\n" for q, a in qa_pairs)
        (self.data_dir / "memory.md").write_text(memory)
        (self.dir / "written.json").write_text(json.dumps({"written_at": now, "dates": dates}, indent=2))

    def save(self, messages, outcome, final_proposal):
        (self.dir / "events.json").write_text(json.dumps(self.events, indent=2, default=str))
        (self.dir / "transcript.json").write_text(json.dumps([_jsonable(m) for m in messages], indent=2, default=str))
        (self.dir / "outcome.json").write_text(json.dumps(outcome, indent=2))
        if final_proposal:
            (self.dir / "proposal.json").write_text(json.dumps(final_proposal, indent=2))


# ---------- rules library ----------
def load_rules():
    """Rule ID -> {title, section, label, url}. Used to render citations honestly."""
    text = RULES_PATH.read_text()
    rules = {}
    for m in re.finditer(r"^### (R\d+): (.+)$", text, re.M):
        block = text[m.end(): text.find("\n### ", m.end()) if "\n### " in text[m.end():] else len(text)]
        cite = re.search(r"\*\*Citation:\*\* ([^,]+?)\s.*?(\d{4});.*?(https://doi\.org/\S+)", block)
        label = f"{cite.group(1)} et al., {cite.group(2)}" if cite else m.group(1)
        rules[m.group(1)] = {"title": m.group(2), "section": "A", "label": label, "url": cite.group(3) if cite else ""}
    for m in re.finditer(r"^- \*\*(B\d+|C\d+), ([^:]+):\*\*", text, re.M):
        rules[m.group(1)] = {"title": m.group(2), "section": m.group(1)[0], "label": "", "url": ""}
    return rules


def _ts(value):
    return datetime.strptime(value, "%Y-%m-%d %H:%M")


def _miles(value):
    return int(value) if float(value).is_integer() else value


def _jsonable(message):
    content = message["content"]
    if isinstance(content, list):
        content = [b.to_dict() if hasattr(b, "to_dict") else b for b in content]
    return {**message, "content": content}
