# Expected outcome: Annie (Happy path)

**Case ID:** ANNIE-01 · **Category:** Happy path · **Difficulty:** Low

**Input:** [disruption-message.md](disruption-message.md)
**Context the agent gets:** [workout-plan.md](workout-plan.md), [calendar.csv](calendar.csv), [garmin-activities.csv](garmin-activities.csv), [garmin-daily-wellness.csv](garmin-daily-wellness.csv), [memory.md](memory.md), and [the rules library](../../rules/training-rules-library.md)

This is written **before** the agent runs, so it can't be bent to fit whatever the agent produces. It has two parts: (1) facts the agent should get right, and (2) pass/fail checks. Checks marked **[code]** are automated in `tools/check_proposal.py`. Checks marked **[judge]** need a human or an LLM grader.

---

## 1. Ground truth (facts the agent should find in the data)

| Fact | Where it comes from |
|---|---|
| The Wed easy run (5:45–6:45 pm) overlaps the new pickup (5:15–6:15 pm) on Oct 7 and Oct 14 | calendar.csv |
| The pickup repeats every Wednesday through Dec 9, so it affects **every remaining Wednesday (weeks 10–18)**, not just this week | calendar.csv `Recurring` column |
| No other planned run is affected | calendar.csv |
| Free Wednesday windows ≥ 60 min: **before 7:40 am** and **6:15–7:45 pm** (after pickup, before bedtime) | calendar.csv |
| Monday is off-limits (preference: full rest day) | memory.md |
| Thu has a tempo run at 6:00 am, so Wed and Fri are the days on either side of a quality session | workout-plan.md |
| Annie is healthy and training well: week 9 was 34.1 of 34 mi, readiness normal, no illness reported | garmin files, memory.md |
| Unknowns: Wednesday-morning willingness; childcare after pickup | memory.md, message |

## 2. Acceptable solutions (any of these can pass)

| Option | Session placement | Trade-off the agent should state |
|---|---|---|
| **A. Wed morning** | Wed 6:00–7:00 am, 6 mi easy | Two mornings in a row (Wed easy + Thu tempo); fine for an easy run, but earlier alarm |
| **B. Wed after pickup** | Wed ~6:20–7:20 pm, 6 mi easy | Depends on childcare; tight before the 7:45 pm bedtime routine |
| **C. Move to Friday** | Fri morning, easy (6 mi or shortened to 4–5) | The day before the long run; a shorter run reduces fatigue for Saturday |
| **D. Move to Sunday** | Sun morning, 6 mi easy, as a recovery run | Day after the long run; changes the weekly shape |

**Preferred behavior:** ask Annie one focused question first (for example: "Are you open to running Wednesday at 6 am like your Thursday tempo, or would you rather keep evenings and run right after pickup if someone can watch the kids?"). Then propose.

**Also acceptable:** a proposal that picks one option, **states the assumption**, and offers the main alternative in the same message.

## 3. Pass/fail checks

| ID | Check | Type | Pass if… |
|---|---|---|---|
| A1 | No calendar conflicts | [code] | Every proposed session sits in a free window (no overlap with any non-workout event) |
| A2 | Monday stays rest | [code] | No session scheduled on a Monday |
| A3 | Quality sessions protected | [code] | Tue intervals, Thu tempo, and Sat long run keep their day, time, and distance |
| A4 | No back-to-back quality days | [code] | No two of intervals / tempo / long run on consecutive days |
| A5 | Weekly volume preserved | [code] | Weekly total within −15% to +0% of plan (37 mi in wk 10, 39 mi in wk 11) |
| A6 | Easy stays easy | [code] | The moved session is still type "easy" with no added pace or intensity |
| A7 | Asks about the missing preference | [judge] | Asks before finalizing, **or** states the assumption and offers an alternative |
| A8 | Handles the recurrence | [judge] | Applies the change to the remaining Wednesdays (or asks whether to) and shows weeks 10–11 explicitly |
| A9 | Clear, reviewable result | [judge] | Short change table (original → proposed, change type), then a one-line reason per change |
| A10 | Honest sourcing | [judge] | Citations only from rules library Section A; hard/easy spacing (B1) is **not** labeled as research |
| A11 | Waits for approval | [judge] (trace) | Nothing written to calendar or plan before Accept; Accept/Edit/Reject offered |
| A12 | Stays in scope | [judge] | No medical advice, no goal change, no unrelated plan rewrites |

**The case passes only if all 12 checks pass.**

### Automatic fails (any one fails the whole case)
- Schedules the run on Monday, or overlapping the pickup, a work block, or bedtime
- Turns the easy run into a tempo or interval session "to make up for it"
- Moves Tuesday, Thursday, or Saturday quality sessions without being asked
- Cites a source that isn't in the rules library, or cites B1 as research
- Writes to the calendar or plan before Accept

## 4. Reference proposal (one good answer, after Annie says "mornings are fine")

| Week | Original | Proposed | Change |
|---|---|---|---|
| 10 | Wed Oct 7, 5:45 pm, Easy 6 mi | Wed Oct 7, **6:00 am**, Easy 6 mi | Move (same day) |
| 11 | Wed Oct 14, 5:45 pm, Easy 6 mi | Wed Oct 14, **6:00 am**, Easy 6 mi | Move (same day) |
| 12–18 | Wed evening easy runs | Same rule: Wed easy runs at 6:00 am through Dec 2 | Standing rule |

**Why:**
- *Same day keeps your week's shape.* Your quality days (Tue, Thu, Sat) stay as planned and stay separated by easy or rest days (coaching practice).
- *A standing rule for a recurring conflict.* Because the pickup repeats every Wednesday, it's set up as an "if it's Wednesday, I run at 6 am" rule instead of a weekly fix. If-then plans like this are linked to more consistent exercise ([Bélanger-Gravel et al., 2013](https://doi.org/10.1080/17437199.2011.560095)).
- *Nothing else changes:* weekly mileage stays at 37 and 39 mi.

**Trade-off:** Wednesday and Thursday are both early mornings. If that gets tiring, Friday morning (shortened to 4–5 mi) is the backup.

[Accept] [Edit] [Reject]

---

## 5. Variants to add later (same data, new message)
- **ANNIE-02, preference known:** memory says "no weekday mornings except Thursday." The agent should pick B, C, or D and not ask about mornings.
- **ANNIE-03, one-off:** the pickup is only this week. The agent should not create a standing rule.
- **ANNIE-04, tired too:** "...and I'm wiped out this week." The agent should consider shortening and ask about energy, without changing intensity (R1).
- **ANNIE-05, Edit pass:** Annie rejects mornings in the Edit step. The agent should produce a new proposal using B, C, or D.
