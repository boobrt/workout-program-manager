"""Generate Annie's synthetic calendar and Garmin-style files.

Fictional persona. Deterministic (fixed random seed), so reruns give identical files.
Run: python3 capstone/tools/generate_annie.py
"""
import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "personas" / "annie"
PLAN_WEEK1 = date(2026, 8, 3)  # Monday of week 1
random.seed(42)

# Planned miles per week: (Tue intervals, Wed easy, Thu tempo, Sat long). Must match workout-plan.md.
PLAN = {
    1: (5, 4, 5, 8), 2: (5, 4, 5, 9), 3: (6, 5, 6, 10), 4: (5, 4, 5, 8),
    5: (6, 5, 6, 11), 6: (6, 5, 7, 12), 7: (7, 5, 7, 13), 8: (6, 4, 6, 10),
    9: (7, 6, 7, 14), 10: (7, 6, 8, 16), 11: (8, 6, 8, 17), 12: (6, 5, 6, 12),
    13: (8, 6, 8, 18), 14: (8, 6, 9, 16), 15: (8, 6, 9, 20), 16: (7, 5, 7, 14),
    17: (6, 5, 6, 10),
}


def week_start(week):
    return PLAN_WEEK1 + timedelta(weeks=week - 1)


def fmt_dt(d, hhmm):
    return f"{d.isoformat()} {hhmm}"


# ---------- Calendar (weeks 10-11) ----------
def calendar_rows():
    rows = []

    def add(name, d, start, end, typ, recurring="", notes=""):
        rows.append({"Name": name, "Start": fmt_dt(d, start), "End": fmt_dt(d, end),
                     "Type": typ, "Recurring": recurring, "Notes": notes})

    for week in (10, 11):
        mon = week_start(week)
        miles = PLAN[week]
        for offset in range(7):
            d = mon + timedelta(days=offset)
            dow = d.weekday()  # 0 = Mon
            if dow < 5:
                add("School drop-off", d, "07:40", "08:10", "Family", "Weekdays")
                add("Work (office)", d, "08:15", "17:00", "Work", "Weekdays", "Includes commute")
            if dow in (0, 3):
                add("Cook dinner", d, "17:30", "18:45", "Family", "Mon, Thu")
            add("Kids' bedtime routine", d, "19:45", "20:30", "Family", "Daily")
            if dow == 1:
                add(f"Run: Intervals {miles[0]} mi", d, "17:45", "19:00", "Workout", "Plan",
                    "School track. See plan for reps.")
            if dow == 2:
                add("Pick up Maya from soccer", d, "17:15", "18:15", "Family",
                    "Weekly on Wed, Oct 7 to Dec 9, 2026",
                    "New this season. Pickup at 5:30 pm; time includes driving.")
                add(f"Run: Easy {miles[1]} mi", d, "17:45", "18:45", "Workout", "Plan",
                    "Conversational pace 9:45-10:15/mi")
            if dow == 3:
                add(f"Run: Tempo {miles[2]} mi", d, "06:00", "07:10", "Workout", "Plan",
                    "From home. See plan for tempo pace.")
            if dow == 4:
                add("Family movie night", d, "18:00", "19:45", "Family", "Fridays")
            if dow == 5:
                long_minutes = miles[3] * 10
                end = (datetime.combine(d, datetime.strptime("07:00", "%H:%M").time())
                       + timedelta(minutes=long_minutes)).strftime("%H:%M")
                add(f"Run: Long {miles[3]} mi", d, "07:00", end, "Workout", "Plan",
                    "Keep on Saturday morning")
                add("Kids' soccer game", d, "10:30", "12:00", "Family", "Saturdays")
            if dow == 6:
                add("Groceries", d, "10:00", "11:00", "Family", "Sundays")
    rows.sort(key=lambda r: (r["Start"], r["End"]))
    return rows


# ---------- Garmin-style activities (weeks 6-9, already completed) ----------
SESSION = {
    # name: (weekday, start time, activity type, avg pace sec/mi, avg HR, max HR, aerobic TE)
    "intervals": (1, "17:47", "Track Running", 530, 152, 176, 3.6),
    "easy": (2, "17:50", "Running", 600, 141, 152, 2.8),
    "tempo": (3, "06:02", "Running", 525, 158, 171, 3.8),
    "long": (5, "07:03", "Running", 598, 146, 163, 4.0),
}
TITLES = {"intervals": "Maplewood - Intervals", "easy": "Maplewood Running",
          "tempo": "Maplewood - Tempo", "long": "Maplewood - Long Run"}


def hms(seconds):
    seconds = int(round(seconds))
    return f"{seconds // 3600:02d}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"


def mmss(seconds):
    seconds = int(round(seconds))
    return f"{seconds // 60}:{seconds % 60:02d}"


def activity_rows():
    rows = []
    for week in (6, 7, 8, 9):
        mon = week_start(week)
        for key, planned in zip(("intervals", "easy", "tempo", "long"), PLAN[week]):
            dow, start, typ, pace, hr, maxhr, te = SESSION[key]
            dist = planned + random.choice((0.0, 0.01, 0.02, 0.03, 0.05))
            note = ""
            if week == 7 and key == "easy":
                dist = 4.02  # cut short: planned 5 mi
                note = "cut short, planned 5 mi"
            pace_actual = pace + random.randint(-8, 8)
            rows.append({
                "Activity Type": typ,
                "Date": f"{(mon + timedelta(days=dow)).isoformat()} {start}:00",
                "Title": TITLES[key] + (f" - {note}" if note else ""),
                "Distance": f"{dist:.2f}",
                "Calories": int(dist * 102),
                "Time": hms(dist * pace_actual),
                "Avg HR": hr + random.randint(-2, 2),
                "Max HR": maxhr + random.randint(-2, 2),
                "Aerobic TE": f"{te + random.choice((-0.1, 0.0, 0.1)):.1f}",
                "Avg Run Cadence": 172 + random.randint(-3, 3),
                "Avg Pace": mmss(pace_actual),
                "Total Ascent": int(dist * 38 + random.randint(-15, 15)),
            })
    rows.sort(key=lambda r: r["Date"], reverse=True)  # Garmin exports newest first
    return rows


# ---------- Garmin-style daily wellness (Sep 21 to Oct 5) ----------
def wellness_rows():
    rows = []
    d = date(2026, 9, 21)
    while d <= date(2026, 10, 5):
        after_long = d.weekday() == 6  # Sunday, the morning after the long run
        rows.append({
            "Date": d.isoformat(),
            "Resting HR": random.randint(50, 53) + (2 if after_long else 0),
            "Overnight HRV (ms)": random.randint(60, 68) - (6 if after_long else 0),
            "HRV Status": "Balanced",
            "Sleep (h)": f"{random.uniform(6.7, 7.6):.1f}",
            "Sleep Score": random.randint(72, 86),
            "Body Battery at Wake": random.randint(74, 90) - (10 if after_long else 0),
            "Training Readiness": random.randint(62, 82) - (18 if after_long else 0),
            "Avg Stress": random.randint(24, 34),
        })
        d += timedelta(days=1)
    return rows


def write(name, rows):
    path = OUT / name
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {path.relative_to(OUT.parent.parent)} ({len(rows)} rows)")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    write("calendar.csv", calendar_rows())
    write("garmin-activities.csv", activity_rows())
    write("garmin-daily-wellness.csv", wellness_rows())
