"""Verification sub-agent: deterministic checks plus an independent Claude review of each draft."""
import json
from collections import defaultdict
from datetime import datetime, timedelta

from .config import FALLBACK_BETA, MODEL, VERIFIER_EFFORT

VERIFIER_SYSTEM = """You are the verification sub-agent for the Workout Program Manager. You review a drafted schedule change before the user sees it. You don't rewrite it; you report problems precisely so the main agent can fix them.

Check the draft for:
1. Code check results. You're given the output of deterministic checks (calendar overlaps, back-to-back quality days, weekly volume, coverage, rule IDs). Any "fail" is a problem. A "warn" is a problem only if the proposal doesn't explain it.
2. Fit to the person. It respects the availability and preferences in memory and everything the user said in this conversation (their answers override older memory).
3. Safety policies C1-C6 in the rules library.
4. Honest sourcing. Each rule ID attached to a reason actually supports that reason. B rules are coaching practice, not research. No claim is presented as research-backed without an R rule.
5. Program intent. Quality sessions are protected unless the disruption forces a change, easy sessions stay easy, and no intensity or volume is added to make up for the change.
6. Recurrence. If the conflict repeats, the proposal handles future weeks, unless the user said it's a one-off.
7. Clarity. Trade-offs are stated, and the change table matches the sessions.

Pass the draft only if nothing is left that a careful coach would fix before showing it to the athlete. Don't fail it for wording or style preferences."""

VERDICT_SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["pass", "fail"]},
        "issues": {"type": "array", "items": {
            "type": "object",
            "properties": {"check": {"type": "string"}, "problem": {"type": "string"}, "fix": {"type": "string"}},
            "required": ["check", "problem", "fix"], "additionalProperties": False}},
        "summary": {"type": "string"},
    },
    "required": ["verdict", "issues", "summary"],
    "additionalProperties": False,
}


def deterministic_checks(proposal, state, rules):
    """General checks that don't depend on any one test case. Returns [{check, severity, detail}]."""
    results = []

    def add(check, severity, detail):
        results.append({"check": check, "severity": severity, "detail": detail})

    sessions = []
    for s in proposal["sessions"]:
        try:
            start = datetime.strptime(f"{s['date']} {s['start']}", "%Y-%m-%d %H:%M")
            end = datetime.strptime(f"{s['date']} {s['end']}", "%Y-%m-%d %H:%M")
        except ValueError:
            add("format", "fail", f"Bad date/time in session {s}")
            continue
        if end <= start:
            add("format", "fail", f"{s['session']} on {s['date']} ends before it starts")
        sessions.append({**s, "start_dt": start, "end_dt": end})

    for s in sessions:
        for b0, b1, name in state.busy_blocks():
            if s["start_dt"] < b1 and b0 < s["end_dt"]:
                add("calendar overlap", "fail", f"{s['session']} {s['date']} {s['start']}-{s['end']} overlaps '{name}' ({b0:%H:%M}-{b1:%H:%M})")
    for i, a in enumerate(sessions):
        for b in sessions[i + 1:]:
            if a["start_dt"] < b["end_dt"] and b["start_dt"] < a["end_dt"]:
                add("session overlap", "fail", f"{a['session']} and {b['session']} overlap on {a['date']}")

    quality_days = sorted({s["start_dt"].date() for s in sessions if s["intensity"] == "quality"})
    for a, b in zip(quality_days, quality_days[1:]):
        if (b - a).days == 1:
            add("back-to-back quality", "fail", f"Quality sessions on consecutive days: {a} and {b} (B1)")

    def week_of(dt):
        return (dt.date() - timedelta(days=dt.weekday())).isoformat()

    planned = state.planned_runs()
    before, after = defaultdict(float), defaultdict(float)
    for r in planned:
        before[week_of(r["start"])] += r["miles"]
    for s in sessions:
        after[week_of(s["start_dt"])] += s["miles"]
    for week in sorted(set(before) | set(after)):
        if before[week] and after[week] > before[week] * 1.10:
            add("weekly volume", "fail", f"Week of {week}: {after[week]:g} mi vs {before[week]:g} planned (>10% increase, R2)")
        elif before[week] and after[week] < before[week] * 0.75:
            add("weekly volume", "warn", f"Week of {week}: {after[week]:g} mi vs {before[week]:g} planned (>25% cut; must be explained)")

    proposed_keys = {(s["session"], week_of(s["start_dt"])) for s in sessions}
    for r in planned:
        if (r["session"], week_of(r["start"])) not in proposed_keys:
            add("coverage", "warn", f"Planned {r['session']} run in week of {week_of(r['start'])} is missing; if it's skipped on purpose, the changes table must say so")

    for reason in proposal["reasons"]:
        for rid in reason["rule_ids"]:
            if rid not in rules:
                add("rule ids", "fail", f"Unknown rule ID '{rid}' (not in the rules library)")
    if not results:
        add("all code checks", "pass", "No problems found")
    return results


def review(client, proposal, checks, state, conversation_notes):
    """Ask the verifier sub-agent for an independent verdict. Returns the parsed verdict dict."""
    payload = {
        "user_request": state.case.message,
        "what_the_user_said_in_this_conversation": conversation_notes,
        "draft_proposal": proposal,
        "code_check_results": checks,
        "memory": state.read("memory"),
        "rules_library": state.read("rules_library"),
        "calendar_csv": state.read("calendar"),
    }
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=16000,
        betas=[FALLBACK_BETA],
        fallbacks="default",
        system=VERIFIER_SYSTEM,
        output_config={"effort": VERIFIER_EFFORT, "format": {"type": "json_schema", "schema": VERDICT_SCHEMA}},
        messages=[{"role": "user", "content": json.dumps(payload, indent=2)}],
    )
    if response.stop_reason == "refusal":
        return {"verdict": "fail", "issues": [{"check": "verifier", "problem": "Verifier declined to review", "fix": "Show the user with this flagged"}], "summary": "Verifier unavailable"}
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)
