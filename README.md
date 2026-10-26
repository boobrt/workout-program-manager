# Workout Program Manager: capstone data kit

All personas and data are **fictional and synthetic**. Nothing here comes from a real person, calendar, or device.

## What's here

```
capstone/
├── rules/
│   └── training-rules-library.md   Rules the agent may use and cite (citations verified 2026-10-04)
├── personas/annie/                  Test case ANNIE-01 (happy path)
│   ├── workout-plan.md             → Notion page: 18-week marathon plan, Annie is in week 10
│   ├── calendar.csv                → Notion database: weeks 10–11, incl. the new Wed pickup
│   ├── garmin-activities.csv       Garmin-style export: runs from weeks 6–9
│   ├── garmin-daily-wellness.csv   Garmin-style daily HRV / sleep / readiness, Sep 21–Oct 5
│   ├── memory.md                   What the agent remembers (preferences, goals, availability)
│   ├── disruption-message.md       The user's request (the test input)
│   ├── expected-outcome.md         Answer key: ground truth, acceptable options, 12 pass/fail checks
│   └── reference-proposal.json     One good answer, in machine-checkable form
└── tools/
    ├── generate_annie.py           Rebuilds Annie's CSVs (deterministic)
    ├── validate_annie_data.py      Checks every file agrees with every other file
    ├── check_proposal.py           Automated graders A1–A6 for an agent's proposal
    └── test_check_proposal.py      Proves the graders pass good answers and catch bad ones
```

`personas/greg`, `dora`, `marcus` and `leo` hold the other four test cases (illness, a 14-day trip with no gym, an injury the agent must refuse, a 40-minute week). Each has a plan, calendar, memory, Garmin-style exports and the disruption message.

## The prototype (Product Faculty LMS upload)

**Current version (since Oct 24, 2026): `prototype/studio/index.html`.** The prototype is now built in the Product Faculty studio, one whole page at a time, and this file is the latest page (bring it back into the studio as is). It has moved well past `src/` and `build.py` below, so do not rebuild it from those. Real-AI eval results are in `docs/eval-*.md` and are recorded inside the page.

The original build, kept for reference:

```
prototype/
├── src/          The page's own code (app.js, body.html, styles.css) and make_data.py, which packs personas/ into data.js
├── kit/          The Product Faculty build kit: starter page, PFAI helper, upload check
└── build.py      Builds the page and writes ../prototype.zip
prototype.zip     The file to upload in the LMS
```

```bash
cd capstone/prototype
python3 -I src/make_data.py   # only after changing files in personas/
python3 -I build.py
```

## The agent (Annie loop)

```
agent/
├── loop.py      Main agent: instructions, tools (read_source, ask_user, stop_and_refer, submit_proposal), the loop, Accept/Edit/Reject
├── verify.py    Verification sub-agent: code checks + an independent Claude review of each draft
├── state.py     Per-run copy of the data, rules lookup, and the writes made only after Accept
├── config.py    Model (Claude Opus 5.5), effort levels, max 2 redrafts
└── run.py       Command-line entry point
tests/test_loop_offline.py   Tests every path of the loop with a scripted stand-in for Claude (free, no key)
personas/annie/case.json     The test input plus scripted answers for repeatable runs
```

**One-time setup:** copy `.env.example` to `.env` and paste your Anthropic API key after `ANTHROPIC_API_KEY=`.

```bash
cd capstone
.venv/bin/python -m agent.run annie                # you answer the agent and choose Accept / Edit / Reject
.venv/bin/python -m agent.run annie --scripted     # repeatable eval run using case.json answers
.venv/bin/python -m agent.run annie --thinking     # also show summaries of the agent's reasoning
```

Each run gets its own folder under `runs/` with a copy of the data (approved changes are written **there**, never to `personas/`), the full transcript, an event log (every tool call, verifier verdict, and decision), and the final `proposal.json` to grade:

```bash
.venv/bin/python tools/check_proposal.py runs/<run folder>/proposal.json
```

Safety: every request uses server-side fallback (`fallbacks: "default"`), so if a safety filter declines a request, it's retried on Anthropic's recommended fallback model instead of failing.

## Run the checks

```bash
cd capstone/tools
python3 validate_annie_data.py      # expect: 0 failure(s)
python3 test_check_proposal.py      # expect: 11/11 behaved as expected
python3 check_proposal.py ../personas/annie/reference-proposal.json
```

## Putting it into Notion
1. **Plan:** create a page and paste `workout-plan.md` (Notion converts the Markdown, tables included).
2. **Calendar:** import `calendar.csv` as a database (*Import → CSV*). Change `Start` and `End` to **Date** properties and `Type` to **Select**. Add the database to Notion Calendar so the events appear there.
   - Notion databases don't do recurring events, so each occurrence is its own row. The `Recurring` column records the pattern (e.g., "Weekly on Wed, Oct 7 to Dec 9, 2026") so the agent can reason about future weeks.
3. **Garmin files and memory:** keep these as files the agent reads, or paste them into Notion pages. Real Garmin exports have more columns; these use a realistic subset.

## How the pieces map to the workflow diagram
| Diagram box | File |
|---|---|
| Notion Calendar | `calendar.csv` |
| Workout plan (Notion MD) | `workout-plan.md` |
| Garmin-style CSV | `garmin-activities.csv`, `garmin-daily-wellness.csv` |
| Memory: preferences + past changes | `memory.md` |
| Training rules library | `rules/training-rules-library.md` |
| Offline evals: test set / graders | `expected-outcome.md`, `check_proposal.py` |
