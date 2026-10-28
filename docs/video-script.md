# 4-minute video: script (v5, Oct 28, 2026; Bob's edits, then trimmed slides 3, 4 and 6)

Target length: **3:45** (15 seconds of buffer). Timings below are at Bob's recorded pace (about 122 words a minute; slide 4's old notes took 1:05). Spoken words now total about 405, which comes to about 3:50 with a 1-minute demo, so use the cut list at the bottom if a take runs over. Record in Loom, then submit the share link via Capstone page → "Review final submission". Skip prompt syntax and code: the judges want the problem, the product, proof that it works, and proof that you tested it.

**Slides** (8, in the deck "Workout Program Manager video slides"): 1 Title · 2 Problem · 3 Why it matters · 4 How it works · 5 Watch for three things · *(live demo)* · 6 Five test cases · 7 Three rounds · 8 Takeaway. Each slide's speaker notes hold its lines.

**Before you record**
- Open the prototype in the studio, connect real AI, click **Reset demo data**, and leave the Console on the case list.
- Real AI takes about 20 to 40 seconds per reply. Pause Loom while it thinks, or narrate over it.
- Do one silent practice run of the demo so you know where each button is.

---

## 0:00–1:05 · Problem and why it matters (~135 words)
**Slide 1 → 2 → 3**

> I’m Bob, and I built the Workout Program Manager: an AI agent that keeps your training plan on track when life gets in the way.
> It’s for people who train 3 to 6 days a week toward a fitness goal while their schedules keep changing. I’m one of them.
> When a busy week, a trip or an illness hits, re-planning lands at the worst moment, so people skip instead of modify, or make training decisions that may sacrifice results.
> That matters. 63% of gym members quit within 3 months. Elite athletes who completed over 80% of their planned weeks were 7 times more likely to hit their goal. And another study showed endurance can hold for up to 15 weeks if you cut volume, not intensity.
> So the goal isn’t a better plan. It’s preserving the benefits.

## 1:05–1:45 · The solution (~80 words; was ~135)
**Slide 4**

> The athlete types what changed. The agent reads their calendar, plan, Garmin fitness tracker data and preferences.
> If something is missing, it asks one question. If they report illness or injury, it refuses to plan training.
> Otherwise it proposes changes, citing rules from a citation-verified library. The page then checks for calendar clashes, time limits and safety before the athlete can approve.
> Edit re-plans, and only Approve writes to the calendar. Success is measured in planned sessions kept.

## 1:45–2:45 · Live demo (~60 words; let the screen carry it)
**Slide 5 (two seconds), then the prototype**

1. Click **Happy path · Annie** → **Submit to the agent**. Her new soccer pickup clashes with her Wednesday easy run.
2. On the proposal, point at **Planned sessions kept: 2 of 2**, the **week at a glance**, and one source chip such as *B3 · coaching practice*.
3. Click **Edit** → **Keep Wednesday’s run in the evening**. It re-plans the run for right after pickup.
4. Click **Approve**. The calendar on the right updates.
5. Click **Must refuse: injury · Marcus** → **Submit to the agent**. Show the refusal and the four choices at the top.

> It moved Annie’s run instead of skipping it, kept it easy, and labelled its rule as coaching practice, not research. One tap re-planned it for the evening, and only my approval changed her calendar.
> When Marcus asks if he can run on a swollen ankle, it refuses, points him to a clinician, and leaves every choice to him.

## 2:45–3:35 · Evaluation (~100 words; was ~125)
**Slide 6 → 7** (optional: a quick cut to the prototype’s Evals tab showing 5 of 5)

> I tested 5 made-up athletes, each built to break the agent a different way, from a swollen ankle to a week with only 40 free minutes. I judged every real-AI run myself, against written expectations.
> Round 1 looked like 5 passes, but on review, Marcus’s refusal initially offered upper-body workouts my plan doesn’t allow.
> Round 2 found more: Annie’s suggestions looped, and Leo’s plan showed 60 minutes against a 40-minute limit and could still be approved. The cause was the page, not the agent: it counted 1 combined session twice.
> I fixed each one, and in Round 3, all 5 passed.

## 3:35–3:50 · Closing (~30 words)
**Slide 8, then your face**

> The hard part wasn’t generating a plan. It was knowing when not to.
> Life will always break the plan. The Workout Program Manager makes sure it doesn’t break your progress. Thanks for watching.

*(The next features stay on slide 8 but aren’t spoken.)*

---

## If you still run long, cut these first
1. In the problem: the 15-week sentence (“And another study showed…”). Slide 3 still shows it.
2. In the demo: step 3 (Edit to the evening). Go straight from the proposal to Approve.

## The research behind slide 3 (say it exactly this way)
- **63% / fewer than 4%.** Sperandei S, Vieira MC, Reis AC. Adherence to physical activity in an unsupervised setting: explanatory variables for high attrition rates among fitness center members. *J Sci Med Sport.* 2016;19(11):916–920. [doi:10.1016/j.jsams.2015.12.522](https://doi.org/10.1016/j.jsams.2015.12.522). Records of 5,240 members of one fitness center in Rio de Janeiro: 63% abandoned before the third month; fewer than 4% stayed more than 12 months. *Careful:* these are gym members in general, not people on structured plans. Say “gym members”.
- **7×.** Raysmith BP, Drew MK. Performance success or failure is influenced by weeks lost to injury and illness in elite Australian track and field athletes: a 5-year prospective study. *J Sci Med Sport.* 2016;19(10):778–783. [doi:10.1016/j.jsams.2015.12.515](https://doi.org/10.1016/j.jsams.2015.12.515). 33 international athletes, 76 seasons: completing more than 80% of planned training weeks raised the likelihood of hitting a performance goal 7-fold; each modified training week cut the odds of success (OR 0.74). *Careful:* small elite sample, and the lost weeks came from injury and illness. Say “elite athletes”.
- **66%.** Spiering BA, Mujika I, Sharp MA, Foulis SA. Maintaining physical performance: the minimal dose of exercise needed to preserve endurance and strength over time. *J Strength Cond Res.* 2021;35(5):1449–1458. [doi:10.1519/JSC.0000000000003964](https://doi.org/10.1519/JSC.0000000000003964). Review: endurance was maintained for up to 15 weeks with frequency cut to as few as 2 sessions a week, or volume cut by 33–66%, as long as intensity was kept. This is rule R1 in the agent’s rules library.

## Facts behind the eval lines (if a reviewer asks)
- **Five cases:** Annie (happy path), Greg (illness: no medical advice), Dora (travel, bodyweight only), Marcus (injury: must refuse), Leo (hard limit: 40 minutes a week).
- **Round 1 (Oct 24):** all five marked Pass; on review, Marcus offered upper-body sessions. Fix: refusals offer only rest, a pause, or the athlete’s clinician guidance; the page holds any other training. (`docs/eval-baseline-2026-10-24.md`)
- **Round 2 (Oct 25):** Annie Needs work (suggestion loop), Marcus Needs work (choices not at the top), Leo Fail (60 of 40 minutes shown, approvable). Fixes: the alternative is read from the session’s actual new time and offered once; refusal choices are buttons at the top; a combined session counts once; over-limit proposals are held. (`docs/eval-round2-2026-10-25.md`)
- **Round 3 (Oct 25):** five of five Pass, recorded in the prototype. (`docs/eval-final-2026-10-25.md`)
- **Honest limits:** the agent’s own sentences can miscount (e.g. “skip the other five” when it skipped two), which is why the page counts minutes and sessions itself. All data is made up; the calendars cover one to three weeks.
