# Workout Program Manager

An AI agent that keeps your training plan on track when life gets in the way. The athlete says what changed; the agent proposes how to move, shorten, replace or skip sessions, and nothing changes until the athlete approves.

**[Try the live prototype →](https://boobrt.github.io/workout-program-manager/)** · [PRD](docs/PRD.md) · [Eval results](docs/eval-final-2026-10-25.md) · [How it's built](docs/repo-guide.md)

Bob Girardi · capstone for Product Faculty's AI Product Management course, October 2026 · built on Claude · every athlete, calendar and record here is made up

## Problem

**Who it's for:** people who train 3 to 6 days a week toward a goal, such as a marathon, a gran fondo or a competition, while their schedules keep changing.

**What hurts:** when a busy week, a trip or an illness hits, re-planning lands at the worst moment, so people skip workouts instead of adapting them. 63% of gym members quit within three months ([Sperandei et al., 2016](https://doi.org/10.1016/j.jsams.2015.12.522)), and elite athletes who completed more than 80% of their planned weeks were 7 times more likely to reach their goal ([Raysmith & Drew, 2016](https://doi.org/10.1016/j.jsams.2015.12.515)). The job isn't a better plan; it's keeping the benefits of the one you have.

## Decision

One loop, end to end: the athlete types what changed; the agent reads their calendar, plan, Garmin-style training data and preferences; then it asks one question, proposes changes, or refuses.

- **It refuses medical calls.** For illness or injury it gives no training advice and points to a clinician. It offers only rest, a pause, or scheduling around the clinician's guidance, as the athlete's choice.
- **It cites only verified rules.** Each change names its rule from a small, citation-checked library, and coaching practice is labelled as practice, not research.
- **The page checks the agent.** Before the athlete decides, code checks every proposal for calendar clashes, time limits and invented sources, and holds plans that break a hard limit. Edit re-plans; only Approve writes to the calendar.
- **What I cut:** live Notion, Google Calendar and Garmin connections, voice input, and using biometrics to judge recovery.

## Proof

- **[Live prototype](https://boobrt.github.io/workout-program-manager/)** with five made-up athletes: a recurring school-pickup clash, food poisoning, a 14-day trip with no gym, a swollen ankle, and a week with 40 free minutes. It runs in sample mode; paste your own Claude API key for real AI.
- **Metric:** planned sessions kept, shown on every proposal (Annie's keeps 2 of 2).
- **Evals:** I judged every real-AI run myself against expectations written beforehand, over three rounds. Round 1 looked like 5 of 5 until review found the injury refusal offering upper-body workouts. Round 2 caught a suggestion loop, and a plan showing 60 minutes against a 40-minute limit that could still be approved (the page, not the agent, counted one combined session twice). After the fixes, round 3 passed 5 of 5. [Final results](docs/eval-final-2026-10-25.md) · [round 2](docs/eval-round2-2026-10-25.md) · [round 1](docs/eval-baseline-2026-10-24.md)

## Next

- **What I learned:** the hard part wasn't generating a plan; it was knowing when not to. Most of the work went into questions, refusals and checks, and into not trusting the model's own arithmetic.
- **Before a pilot:** ask one focused question at a time with clickable answers (including morning or evening preference) instead of assuming, and pass repeated runs, not one per case.
- **Then:** a small volunteer pilot measuring first-proposal edit rate and approve, edit, reject and revert rates; live calendar and wearable connections after that.

**In this repo:** [PRD](docs/PRD.md) · [prototype source](prototype/studio/index.html) · [rules library](rules/training-rules-library.md) · [test athletes](personas/) · [Python agent](agent/) · [video script](docs/video-script.md) · [developer guide](docs/repo-guide.md)
