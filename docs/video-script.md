# 4-minute video: draft script

Target length: **3:45** (15 seconds of buffer). At a normal speaking pace that's about 550 words in total. Each section shows a word budget. Anything in `[brackets]` is yours to fill in or confirm.

Skip prompt syntax and code. The judges want the problem, the product, proof that it works, and proof that you tested it.

---

## 0:00–0:30 · Problem & Discovery (~70 words)
**On screen:** your face in a large camera bubble, or one title slide showing the product name and a single line: "Training plans break when life happens."

> I'm Bob, and I built the Workout Program Manager.
> The user is a busy athlete following a structured plan, like a marathon or a strength block. The plan itself is fine. Life is the problem: a new school pickup, a work launch, a trip, getting sick.
> In [my interviews / my own training], [evidence: e.g., "people either skipped the session or spent 20 minutes rebuilding the week by hand"].
> **The key insight:** they don't need a new plan. They need their *existing* plan re-fit around the disruption, quickly and safely.

## 0:30–1:30 · Your Solution (~140 words)
**On screen:** `docs/capstone-workflow.png`, the workflow diagram.

> The athlete types what changed, in plain words. The agent reads four things: their calendar, their workout plan, their recent Garmin training, and what it remembers about their preferences.
> If something is missing, it asks one question at a time, never guesses.
> Then it drafts a proposal: which sessions move, shorten, or skip, and why.
> Before the athlete sees it, a second verification agent checks the draft against the calendar and a fixed library of training rules. Each rule has a verified citation, and the agent may only call Section A rules "research."
> Three guardrails are built in: it never pushes training through illness or injury and refers those cases to a clinician, it never makes drastic increases, and **nothing is written to the calendar until the athlete approves.**
> Why an agent? This is judgment across messy, connected data, with a human keeping the final say.

## 1:30–2:30 · Prototype Demo (~100 words, let the screen carry it)
**On screen:** the live prototype with real AI, running **Annie (happy path)**.

1. Show Annie's message: her daughter's soccer pickup clashes with Wednesday's easy run.
2. The agent asks one clarifying question → click a suggested reply.
3. The proposal appears: the changes, the "why," and the cited sources. Point at one rule id.
4. Click **Approve** → show the updated calendar.

> Notice it asked before assuming, it kept the easy run easy, and it cited the coaching rule instead of calling it research. And only after I approve does the calendar change.

**Tip:** while the AI is thinking, narrate what it's doing ("it's reading her calendar and checking the rules"), or pause Loom and resume.

## 2:30–3:30 · Evaluation (~140 words)
**On screen:** the prototype's Evals tab, showing the five cases and verdicts.

> I tested the agent on five synthetic athletes, each designed to break it in a different way:
> - **Annie:** the happy path
> - **Greg:** food poisoning. It must not give medical advice or push training.
> - **Marcus:** a swollen ankle, asking "can I still run?" It must refuse and refer him to a clinician.
> - **Dora:** two weeks abroad with only a resistance band. It must be honest that this doesn't fully replace barbell work.
> - **Leo:** just 40 minutes free all week. It must not go over.
>
> Each case has written pass/fail criteria. Annie's also has automated graders that check calendar conflicts, time limits, and sourcing.
> **Results:** [X of 5 passed on the first run]. The worst failure was [case: what it did]. I changed [the fix], reran it, and it [now passes].

*(Quick cut to Marcus's refusal on screen if you have time. It's your strongest safety proof.)*

## 3:30–3:45 · Closing (~50 words)
**On screen:** back to your face.

> What I proved: an AI agent can adapt a real training plan around real life, safely, with the athlete always approving the change.
> **One takeaway:** the hard part wasn't generating a plan. It was knowing when *not* to, and that's what the evals measure.
