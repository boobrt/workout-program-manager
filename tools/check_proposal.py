"""Code graders A1-A6 for ANNIE-01 (see personas/annie/expected-outcome.md).

A proposal is JSON: {"sessions": [{"session": "intervals|easy|tempo|long", "date": "YYYY-MM-DD",
"start": "HH:MM", "end": "HH:MM", "miles": 6, "intensity": "easy|quality"}, ...]}
covering every run in weeks 10-11. Checks A7-A12 need a human or LLM judge.

Run: python3 capstone/tools/check_proposal.py path/to/proposal.json
"""
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

from generate_annie import PLAN_WEEK1

ANNIE = Path(__file__).resolve().parent.parent / "personas" / "annie"
QUALITY = ("intervals", "tempo", "long")
PLAN_TOTALS = {10: 37, 11: 39}


def plan_week(dt):
    return (dt.date() - PLAN_WEEK1).days // 7 + 1


def parse(d, t):
    return datetime.strptime(f"{d} {t}", "%Y-%m-%d %H:%M")


def load_calendar():
    with (ANNIE / "calendar.csv").open() as f:
        rows = list(csv.DictReader(f))
    busy = [(datetime.strptime(r["Start"], "%Y-%m-%d %H:%M"), datetime.strptime(r["End"], "%Y-%m-%d %H:%M"), r["Name"])
            for r in rows if r["Type"] != "Workout"]
    original = {}
    for r in rows:
        if r["Type"] == "Workout":
            kind = r["Name"].split()[1].lower()
            start = datetime.strptime(r["Start"], "%Y-%m-%d %H:%M")
            original[(kind, plan_week(start))] = (r["Start"], r["End"], int(r["Name"].split()[2]))
    return busy, original


def grade(proposal):
    busy, original = load_calendar()
    sessions = proposal["sessions"]
    results = {}

    clashes = [f"{s['session']} {s['date']} {s['start']} vs {name}"
               for s in sessions for b0, b1, name in busy
               if parse(s["date"], s["start"]) < b1 and b0 < parse(s["date"], s["end"])]
    clashes += [f"{a['session']} {a['date']} {a['start']} vs {b['session']} {b['start']}"
                for i, a in enumerate(sessions) for b in sessions[i + 1:]
                if parse(a["date"], a["start"]) < parse(b["date"], b["end"])
                and parse(b["date"], b["start"]) < parse(a["date"], a["end"])]
    results["A1 no calendar conflicts"] = (not clashes, clashes)

    mondays = [s["date"] for s in sessions if parse(s["date"], s["start"]).weekday() == 0]
    results["A2 Monday stays rest"] = (not mondays, mondays)

    moved_quality = []
    for s in sessions:
        if s["session"] in QUALITY:
            key = (s["session"], plan_week(parse(s["date"], s["start"])))
            o_start, o_end, o_miles = original[key]
            if (f"{s['date']} {s['start']}", f"{s['date']} {s['end']}", s["miles"]) != (o_start, o_end, o_miles):
                moved_quality.append(f"{s['session']} {s['date']} {s['start']} {s['miles']} mi (was {o_start} {o_miles} mi)")
    expected_quality = {k for k in original if k[0] in QUALITY}
    present_quality = {(s["session"], plan_week(parse(s["date"], s["start"]))) for s in sessions if s["session"] in QUALITY}
    missing = sorted(expected_quality - present_quality)
    results["A3 quality sessions protected"] = (not moved_quality and not missing, moved_quality + [f"missing {m}" for m in missing])

    q_days = sorted(parse(s["date"], s["start"]).date() for s in sessions if s["session"] in QUALITY)
    back_to_back = [f"{a} & {b}" for a, b in zip(q_days, q_days[1:]) if (b - a).days == 1]
    results["A4 no back-to-back quality days"] = (not back_to_back, back_to_back)

    volume = []
    for week, planned in PLAN_TOTALS.items():
        total = sum(s["miles"] for s in sessions if plan_week(parse(s["date"], s["start"])) == week)
        if not (planned * 0.85 <= total <= planned):
            volume.append(f"week {week}: {total} mi vs plan {planned} (allowed {planned * 0.85:.1f}-{planned})")
    results["A5 weekly volume preserved"] = (not volume, volume)

    easy = [s for s in sessions if s["session"] == "easy"]
    upgraded = [f"{s['date']} intensity={s['intensity']}" for s in easy if s["intensity"] != "easy"]
    results["A6 easy stays easy"] = (len(easy) >= 1 and not upgraded, upgraded or ([] if easy else ["no easy run left"]))
    return results


def report(name, proposal):
    results = grade(proposal)
    passed = all(ok for ok, _ in results.values())
    print(f"\n{name}: {'PASS' if passed else 'FAIL'}")
    for check_name, (ok, detail) in results.items():
        print(f"  {'pass' if ok else 'FAIL'}  {check_name}" + ("" if ok else f"  -> {detail}"))
    return passed


if __name__ == "__main__":
    path = Path(sys.argv[1])
    sys.exit(0 if report(path.name, json.loads(path.read_text())) else 1)
