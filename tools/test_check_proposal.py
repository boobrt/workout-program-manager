"""Tests the graders themselves: good answers must pass, known-bad answers must fail the right check.

Run: python3 capstone/tools/test_check_proposal.py
"""
import copy
import json
import sys
from pathlib import Path

from check_proposal import grade, report

ANNIE = Path(__file__).resolve().parent.parent / "personas" / "annie"

UNCHANGED_QUALITY = [
    {"session": "intervals", "date": "2026-10-06", "start": "17:45", "end": "19:00", "miles": 7, "intensity": "quality"},
    {"session": "tempo", "date": "2026-10-08", "start": "06:00", "end": "07:10", "miles": 8, "intensity": "quality"},
    {"session": "long", "date": "2026-10-10", "start": "07:00", "end": "09:40", "miles": 16, "intensity": "quality"},
    {"session": "intervals", "date": "2026-10-13", "start": "17:45", "end": "19:00", "miles": 8, "intensity": "quality"},
    {"session": "tempo", "date": "2026-10-15", "start": "06:00", "end": "07:10", "miles": 8, "intensity": "quality"},
    {"session": "long", "date": "2026-10-17", "start": "07:00", "end": "09:50", "miles": 17, "intensity": "quality"},
]


def proposal(easy_runs, quality=None):
    return {"sessions": copy.deepcopy(quality or UNCHANGED_QUALITY) + easy_runs}


def easy(date, start, end, miles=6, intensity="easy"):
    return {"session": "easy", "date": date, "start": start, "end": end, "miles": miles, "intensity": intensity}


REFERENCE = proposal([easy("2026-10-07", "06:00", "07:00"), easy("2026-10-14", "06:00", "07:00")])

GOOD = {
    "A: Wed 6 am (reference)": REFERENCE,
    "B: Wed after pickup": proposal([easy("2026-10-07", "18:20", "19:20"), easy("2026-10-14", "18:20", "19:20")]),
    "C: Fri morning, shortened": proposal([easy("2026-10-09", "06:00", "06:45", 4.5), easy("2026-10-16", "06:00", "06:45", 4.5)]),
    "D: Sun recovery run": proposal([easy("2026-10-11", "07:30", "08:30"), easy("2026-10-18", "07:30", "08:30")]),
}

tempo_to_wed = copy.deepcopy(UNCHANGED_QUALITY)
tempo_to_wed[1].update(date="2026-10-07", start="06:00", end="07:10")
BAD = {  # name: (proposal, check that must fail)
    "Unchanged (overlaps pickup)": (proposal([easy("2026-10-07", "17:45", "18:45"), easy("2026-10-14", "17:45", "18:45")]), "A1 no calendar conflicts"),
    "Runs during bedtime routine": (proposal([easy("2026-10-07", "19:00", "20:00"), easy("2026-10-14", "19:00", "20:00")]), "A1 no calendar conflicts"),
    "Moved to Monday": (proposal([easy("2026-10-05", "06:00", "07:00"), easy("2026-10-12", "06:00", "07:00")]), "A2 Monday stays rest"),
    "Tempo moved to Wed": (proposal([easy("2026-10-08", "18:00", "19:00"), easy("2026-10-14", "06:00", "07:00")], tempo_to_wed), "A3 quality sessions protected"),
    "Easy upgraded to tempo": (proposal([easy("2026-10-07", "06:00", "07:00", intensity="quality"), easy("2026-10-14", "06:00", "07:00")]), "A6 easy stays easy"),
    "Extra miles added": (proposal([easy("2026-10-07", "06:00", "07:20", 8), easy("2026-10-14", "06:00", "07:00")]), "A5 weekly volume preserved"),
    "Easy run dropped, week cut too far": (proposal([easy("2026-10-14", "06:00", "07:00")]), "A5 weekly volume preserved"),
}

failures = 0
for name, prop in GOOD.items():
    if not report(name, prop):
        failures += 1
        print("  ^ expected PASS")
for name, (prop, must_fail) in BAD.items():
    results = grade(prop)
    caught = not results[must_fail][0]
    report(name, prop)
    if not caught:
        failures += 1
        print(f"  ^ expected '{must_fail}' to FAIL")

(ANNIE / "reference-proposal.json").write_text(json.dumps(REFERENCE, indent=2) + "\n")
print(f"\nGrader self-test: {len(GOOD) + len(BAD) - failures}/{len(GOOD) + len(BAD)} behaved as expected")
sys.exit(1 if failures else 0)
