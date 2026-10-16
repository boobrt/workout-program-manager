"""Consistency checks across Annie's synthetic files. Exits non-zero on any failure.

Run: python3 capstone/tools/validate_annie_data.py
"""
import csv
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from generate_annie import PLAN, PLAN_WEEK1, week_start

ROOT = Path(__file__).resolve().parent.parent
ANNIE = ROOT / "personas" / "annie"
failures = []


def check(ok, msg):
    print(("PASS  " if ok else "FAIL  ") + msg)
    if not ok:
        failures.append(msg)


def load(name):
    with (ANNIE / name).open() as f:
        return list(csv.DictReader(f))


def parse(ts):
    return datetime.strptime(ts, "%Y-%m-%d %H:%M")


# 1. Plan markdown table matches the PLAN constants and its own totals
plan_md = (ANNIE / "workout-plan.md").read_text()
rows = re.findall(r"^\| \**(\d+)\** \| \**(\w+ \d+)\** \| .*? \| \**(\d+)\** \| \**(\d+)\** \| \**(\d+)\** \| \**(\d+)\** \| \**(\d+)\** \|$",
                  plan_md, re.M)
check(len(rows) == 17, f"plan table has 17 numeric weeks (found {len(rows)})")
for wk, starts, i, e, t, l, total in rows:
    wk = int(wk)
    vals = tuple(int(x) for x in (i, e, t, l))
    check(vals == PLAN[wk], f"week {wk} sessions in plan.md match generator {PLAN[wk]}")
    check(sum(vals) == int(total), f"week {wk} total {total} = sum of sessions")
    expected_start = week_start(wk).strftime("%b %-d")
    check(starts == expected_start, f"week {wk} start date '{starts}' is a Monday ({expected_start})")
check(PLAN_WEEK1 + timedelta(weeks=17, days=6) == date(2026, 12, 6), "race day Dec 6, 2026 is the Sunday of week 18")

# 2. Calendar: dates, workouts vs plan, and conflicts
cal = load("calendar.csv")
for r in cal:
    check(parse(r["Start"]) < parse(r["End"]), f"{r['Name']} {r['Start']} ends after it starts")
workouts = [r for r in cal if r["Type"] == "Workout"]
check(len(workouts) == 8, f"8 planned runs in weeks 10-11 (found {len(workouts)})")
expected_days = {"Intervals": 1, "Easy": 2, "Tempo": 3, "Long": 5}
key_index = {"Intervals": 0, "Easy": 1, "Tempo": 2, "Long": 3}
for w in workouts:
    kind = w["Name"].split()[1]
    start = parse(w["Start"])
    week = (start.date() - PLAN_WEEK1).days // 7 + 1
    miles = int(re.search(r"(\d+) mi", w["Name"]).group(1))
    check(start.weekday() == expected_days[kind], f"{w['Name']} on {start:%a %b %d} is the planned weekday")
    check(miles == PLAN[week][key_index[kind]], f"{w['Name']} matches week {week} plan distance")

conflicts = []
others = [r for r in cal if r["Type"] != "Workout"]
for w in workouts:
    for o in others:
        if parse(w["Start"]) < parse(o["End"]) and parse(o["Start"]) < parse(w["End"]):
            conflicts.append((w["Name"], w["Start"][:10], o["Name"]))
check(sorted(conflicts) == [("Run: Easy 6 mi", "2026-10-07", "Pick up Maya from soccer"),
                            ("Run: Easy 6 mi", "2026-10-14", "Pick up Maya from soccer")],
      f"only the intended conflicts exist: {conflicts}")
for o1 in others:
    for o2 in others:
        if o1 is not o2 and parse(o1["Start"]) < parse(o2["End"]) and parse(o2["Start"]) < parse(o1["End"]):
            check(False, f"non-workout events overlap: {o1['Name']} / {o2['Name']} {o1['Start']}")

# 3. Garmin activities match weeks 6-9 of the plan
acts = load("garmin-activities.csv")
check(len(acts) == 16, f"16 activities for weeks 6-9 (found {len(acts)})")
by_week = {}
for a in acts:
    dt = datetime.strptime(a["Date"], "%Y-%m-%d %H:%M:%S")
    week = (dt.date() - PLAN_WEEK1).days // 7 + 1
    by_week.setdefault(week, []).append(a)
    h, m, s = (int(x) for x in a["Time"].split(":"))
    pm, ps = (int(x) for x in a["Avg Pace"].split(":"))
    implied = (h * 3600 + m * 60 + s) / float(a["Distance"])
    check(abs(implied - (pm * 60 + ps)) <= 2, f"{a['Date']} time / distance matches avg pace {a['Avg Pace']}")
    check(dt.weekday() in (1, 2, 3, 5), f"{a['Date']} falls on a planned run day")
for week in (6, 7, 8, 9):
    actual = sum(float(a["Distance"]) for a in by_week[week])
    planned = sum(PLAN[week])
    expected_gap = -1 if week == 7 else 0  # week 7 easy run was cut short on purpose
    check(abs(actual - planned - expected_gap) <= 0.25,
          f"week {week}: {actual:.2f} mi done vs {planned} planned (gap {expected_gap})")
check(abs(sum(float(a["Distance"]) for a in by_week[9]) - 34.1) <= 0.05, "week 9 total is 34.1 mi, as stated in plan.md")

# 4. Wellness covers Sep 21 to Oct 5 with plausible values
well = load("garmin-daily-wellness.csv")
check(well[0]["Date"] == "2026-09-21" and well[-1]["Date"] == "2026-10-05" and len(well) == 15,
      "wellness covers Sep 21 to Oct 5 (15 days)")
check(all(45 <= int(r["Resting HR"]) <= 60 and 10 <= int(r["Training Readiness"]) <= 100 for r in well),
      "wellness values are in plausible ranges")

print(f"\n{len(failures)} failure(s)")
sys.exit(1 if failures else 0)
