# 4-minute video: script (v4, Oct 28, 2026; edited by Bob)

Target length: **3:45** (15 seconds of buffer), about 550 spoken words. Record in Loom, then submit the share link via Capstone page → "Review final submission". Skip prompt syntax and code: the judges want the problem, the product, proof that it works, and proof that you tested it.

**Slides** (8, in the deck "Workout Program Manager video slides"): 1 Title · 2 Problem · 3 Why it matters · 4 How it works · 5 Watch for three things · *(live demo)* · 6 Five test cases · 7 Three rounds · 8 Takeaway. Each slide's speaker notes hold its lines.

**Before you record**
- Open the prototype in the studio, connect real AI, click **Reset demo data**, and leave the Console on the case list.
- Real AI takes about 20 to 40 seconds per reply. Pause Loom while it thinks, or narrate over it.
- Do one silent practice run of the demo so you know where each button is.

---

## 0:00–0:50 · Problem and why it matters (~120 words)
**Slide 1 → 2 → 3**

> I’m Bob, and I built the Workout Program Manager: an AI agent that keeps your training plan on track when life gets in the way.
> It’s for people who train 3 to 6 days a week toward a fitness goal while their schedules keep changing. I’m one of them.
> When a busy week, a trip or an illness hits, re-planning lands at the worst moment, so people skip instead of modify, or make training decisions that may sacrifice results.
> That matters. In a study of over 5,000 gym members, 63% quit within 3 months. And elite athletes who completed over 80% of their planned training weeks were 7 times more likely to hit their goal.
> So the goal isn’t a better plan. It’s keeping more of the plan.

## 0:50–1:35 · The solution (~120 words)
**Slide 4**

> The athlete types what changed, in plain words. The agent reads 4 records: their calendar, their plan, their recent Garmin training, and what it remembers about their preferences.
> Then it decides. If something it needs is missing, it asks, one question at a time. It never guesses. If the athlete reports illness or injury, it refuses to plan training and offers their own choices instead.
> Otherwise it proposes which sessions to move, shorten, replace or skip, with its reasons and the training rules it used, each from a citation-verified library.
> Before the athlete sees it, the page checks the proposal itself: a calendar clash, a blown time limit, or training through an injury switches Approve off. The full Python version also has a separate reviewer Agent.
> The athlete approves, edits or rejects. Edit sends it back to re-plan. Only Approve writes to the calendar, and success is measured as planned sessions kept.

## 1:35–2:35 · Live demo (~60 words; let the screen carry it)
**Slide 5 (two seconds), then the prototype**

1. Click **Happy path · Annie** → **Submit to the agent**. Her new soccer pickup clashes with her Wednesday easy run.
2. On the proposal, point at **Planned sessions kept: 2 of 2**, the **week at a glance**, and one source chip such as *B3 · coaching practice*.
3. Click **Edit** → **Keep Wednesday’s run in the evening**. It re-plans the run for right after pickup.
4. Click **Approve**. The calendar on the right updates.
5. Click **Must refuse: injury · Marcus** → **Submit to the agent**. Show the refusal and the four choices at the top.

> It moved Annie’s run instead of skipping it, kept it easy, and labelled its rule as coaching practice, not research. One tap re-planned it for the evening, and only my approval changed her calendar.
> When Marcus asks if he can run on a swollen ankle, it refuses, points him to a clinician, and leaves every choice to him.

## 2:35–3:30 · Evaluation (~115 words)
**Slide 6 → 7** (optional: a quick cut to the prototype’s Evals tab showing 5 of 5)

> I tested 5 made-up athletes, each built to break the agent a different way: a happy path, food poisoning, 2 weeks abroad with 1 resistance band, a swollen ankle, and a week with only 40 minutes free. Each has written expectations from my plan, and I judged every real-AI run myself.
> Round 1 looked like 5 passes, but on review, Marcus’s refusal initially offered upper-body workouts my plan doesn’t allow.
> Round 2 found more: Annie’s suggestions looped, and Leo’s plan showed 60 minutes against a 40-minute limit and could still be approved. The cause was the page, not the agent: it counted 1 combined session twice.
> I fixed each one, and in Round 3, all 5 passed.

## 3:30–3:45 · Closing (~45 words)
**Slide 8, then your face**

> The hard part wasn’t generating a plan. It was knowing when not to, and checking the agent’s numbers with my own.
> Next: real Notion and Garmin data, voice input, and a research agent that proposes new rules for my approval.

---

## If you run long, cut these first
1. In the problem: the gym-member sentence (“In a study of over 5,000 gym members…”). Slide 3 still shows the 63%.
2. In the solution: “The full Python version also has a separate reviewer Agent.”
3. In the demo: step 3 (Edit to the evening). Go straight from the proposal to Approve.
4. In the closing: the “Next” sentence. Slide 8 still shows it.

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
