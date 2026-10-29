# PRD vs. prototype review (Oct 28, 2026)

Compares `docs/capstone-prd.xlsx` (Capstone Studio export, Oct 28) with what the prototype (`prototype/studio/index.html`), the three real-AI eval rounds (`docs/eval-*.md`) and the video script actually show. Row numbers are the PRD’s sheet rows (F = Student Response column).

**Bottom line:** Discovery and most of Design match the prototype. The Develop answers about results (rows 33, 34, 36) and the video and demo answers (43, 45) describe an Annie test that is not in the prototype or its data: a 30-minute window for a 7-mile tempo run on Wed Oct 28, after a 14-mile Sunday long run, with the tempo moved to Thursday. They read as an expected pass (“designed to pass if…”), not results. Your real three rounds of results are stronger material, and they are what the video and slides show, so rewrite those rows from them. Drafts are at the end.

---

## Must fix (a reviewer would notice the story does not match)

| Row                | Topic                               | PRD says                                                                                 | Prototype / evals / video show                                                                                                                                                                                                                                                       | Fix                                                                                                                                   |
| ------------------ | ----------------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| 33                 | What passed and failed              | One planned Annie test (30-min window, tempo to Thursday), written as an expected pass   | 5 cases × 3 real-AI rounds: R1 5 marked Pass, then Marcus found to offer upper-body work; R2 Annie Needs work, Marcus Needs work, Leo Fail; R3 5 of 5 Pass                                                                                                                           | Replace with **Draft A**                                                                                                              |
| 34                 | What changed after testing          | “Read the previous week before rescheduling”                                             | Real fixes: Leo combined-session counting + hard 40-min hold; Marcus refusal choices; Annie suggestion loop                                                                                                                                                                          | Replace with **Draft B** (Leo first; it is your strongest story)                                                                      |
| 36                 | Working demo summary                | Annie 30-min tempo scenario; writes to Notion                                            | Annie’s soccer pickup → Wednesday easy run moved to 6:00 am as a standing rule; Edit → evening; Approve; Marcus refusal; Evals tab                                                                                                                                                   | Replace with **Draft C**                                                                                                              |
| 43                 | Video outline                       | Annie 30-min tempo demo, Dora escalation, “reads prior week” improvement, 4–6 days       | Script: Annie (proposal → Edit to evening → Approve) then Marcus refusal; 3 eval rounds; 3–6 days; adherence research                                                                                                                                                                | Rewrite to match `docs/video-script.md` (Draft D gives a short version)                                                               |
| 45                 | Demo clarity                        | Annie “asks for clarification rather than assuming”; Dora shows the sub-agent escalation | Annie gets a proposal straight away (her memory confirms 6:00 am mornings); Dora is not in the video                                                                                                                                                                                 | Rewrite to match the video, or add a 10-second Dora cut to the video                                                                  |
| 46                 | Video check                         | **Empty**                                                                                | —                                                                                                                                                                                                                                                                                    | Answer it (**Draft E**) once the video is recorded                                                                                    |
| 35, 36, 15, 24     | Writing to Notion                   | “Writes approved changes to the synthetic Markdown workout plan in Notion”               | The prototype updates in-page copies of the made-up calendar and plan, downloadable as `.csv` and `.md`. Nothing is written to Notion                                                                                                                                                | Say “the synthetic calendar and plan inside the prototype (downloadable)”; keep Notion as the target design                           |
| 39, 40, 42, 44, 45 | Validation-and-escalation sub-agent | A sub-agent reviews every proposal and asks the clarifying questions                     | Prototype: the page’s own rule-based checker (calendar clashes, time limits, injury/illness holds; it switches Approve off). The **main agent** asks the questions. The Python agent (`agent/verify.py`) has a verification sub-agent: code checks plus an independent Claude review | Say which is which: “in the prototype, page checks; in the full Python agent, a verification sub-agent.” The script already says this |

## Should fix (inconsistencies inside the PRD or with the prototype)

| Row | Issue | Fix |
|---|---|---|
| 9 vs 43 | Row 9 says **3–6** days a week; row 43 says **four to six** | Use 3–6 everywhere (matches the slides and script) |
| 39–43, 44 | The agent is called **PLAN MANAGER**; the product, prototype, slides and video say **Workout Program Manager** | Pick one. Suggest: product = Workout Program Manager; “Plan manager” = the version-history panel only |
| 27, 29, 30 | Review appears “in a pop-up”; buttons “Approve” (27) vs “Accept” (30, 32) | Prototype: Approve, Edit and Reject are pinned in a bar at the top of the review, not a pop-up. Use **Approve** everywhere |
| 14, 18, 20, 30 | “by text or voice”, “type or dictate” | Prototype is text only; the device’s own dictation works. Say so, or move voice to the limitations and next steps |
| 25 | “Clickable citation to the verified source” | Sources show as rule ids with full references as text; the hosted page cannot open links. Say “verified citation shown with the reason” |
| 15, 17, 18 | Three personas (Annie, Greg, Dora) | The prototype and tests use five: add Marcus (injury: must refuse) and Leo (40 minutes a week) |
| 37, 38, 39 | “Must ask morning vs evening when not stated in the **workout-plan Markdown**” | Annie’s 6:00 am preference is in her **memory.md**, which is why she gets a proposal without a question. Say “when not stated in the athlete’s records (plan or memory)” |
| 28 vs 32 | Row 28 describes a missing-information test (no plan in Notion), but it is not one of the five cases | Either drop it from row 28, or say Dora covers missing information (her questions) and the no-plan case is future work |
| 26, 27 vs 32 | Row 32 (Marcus): “may offer to record rest or pause the plan **only**” | The prototype also lets him plan around **clinician guidance he reports**, which rows 26 and 27 allow. Add “or plan around guidance from his clinician, once he reports it” |

## Worth adding (the prototype has it; the PRD does not mention it)

- **Row 17 (success metric):** the prototype computes it. Every proposal shows **“Planned sessions kept: X of Y”** (moved, shortened, replaced vs. skipped) and how many sessions would clash if left unchanged.
- **Row 13 or 17 (evidence):** the adherence research on slide 3. 63% of new gym members quit within 3 months (Sperandei et al., 2016); athletes completing more than 80% of planned training weeks were 7× more likely to hit their goal (Raysmith & Drew, 2016); endurance was maintained with up to 66% less volume when intensity was kept (Spiering et al., 2021, = rule R1).
- **Row 41 (feedback):** the prototype already collects in-product feedback, a **thumbs up/down on every agent reply** with reasons (“Too vague”, “Ignored my calendar”…), logged per run and included in Copy results.
- **Row 26/27:** **binding limits.** Over a hard time limit, or training an injured athlete without reported clinician guidance, the page holds the proposal and Approve is switched off.
- **Row 35 (limitations):** add the honest ones from testing:
  - Text only.
  - Sources shown as text.
  - Writes only to in-page synthetic copies.
  - Calendars cover 1–3 weeks.
  - Memory lasts one visit.
  - The agent’s own sentences can miscount (e.g. “skip the other five” when it skipped two), so the page counts minutes and sessions itself.
  - The page checks the stated session length, not the time its listed exercises add up to.

---

## Drafts to paste (edit freely)

### Draft A: Row 33, what passed and failed
I ran all five test cases with real AI (Claude) in the prototype in three rounds, and judged every run myself against the written expected outcome; the agent never grades itself.

Round 1 (Oct 24): I first marked all five Pass. On review, Marcus’s refusal also offered upper-body workouts, which my expected outcome does not allow. The other cases behaved as expected: Annie’s Wednesday easy run moved to 6:00 am, the morning slot her records confirm, as a standing rule through Dec 9; Greg and Marcus were refused with a clinician message and no plan changes; Dora was asked focused questions before any plan; Leo’s plan used only his two 20-minute windows.

Round 2 (Oct 25): Greg and Dora passed. Annie needed work: the one-tap alternative suggested moving her run to 6:00 am when it was already there, so suggestions could loop. Marcus needed work: rest and pause were offered only in text, not as choices beside “keep my plan unchanged.” Leo failed: his proposal showed 60 minutes against a 40-minute limit, overlapped two work events, and could still be approved. The agent had in fact combined two strength days into one 20-minute Saturday session; the prototype counted it once on each original day.

Round 3 (Oct 25): after the fixes, all five passed, and the results are recorded in the prototype’s Evals view.

A human was needed at every decision point: nothing was written without Approve, Edit or Reject, and the illness and injury cases were handed back to the athlete and a clinician every time.

### Draft B: Row 34, what changed after testing
Testing led to three changes, each re-tested.

1. Leo (the most important): a real test showed a 60-minute proposal against a 40-minute limit that could still be approved. The cause was the prototype, not the agent: it counted a combined session twice. I changed it so a session that combines planned ones counts once on its new day, made any proposal over a hard limit a hold that switches Approve off, and now give the agent its exact 40-minute budget as a fact. Re-run: 40 of 40 minutes, no calendar clashes, Pass.
2. Marcus: removed the upper-body offer. A refusal now offers only the athlete’s own choices (rest, a pause, or planning around guidance from their clinician) as buttons at the top, and the prototype holds any other training for an injured athlete. Re-run: Pass.
3. Annie: the one-tap alternative is now chosen from the moved session’s actual new time and offered once, and suggestions never repeat an earlier proposal. Re-run: Pass, with no loop.

### Draft C: Row 36, working demo summary
The prototype runs one complete adaptation loop on five made-up athletes, with real AI or labelled sample answers. In the main demo, Annie reports that a new Wednesday soccer pickup clashes with her evening easy run. The agent reads her calendar, workout plan, recent training and memory, which are shown as a week view, a formatted plan and charts. Her memory confirms she runs weekday mornings, so it proposes moving the run to 6:00 am, same distance and easy pace, as a standing rule through Dec 9, and names the rules it used (B3, B4 coaching practice; R6 research).

The output shows “Planned sessions kept: 2 of 2”, a week-at-a-glance view of what moves, and the prototype’s own calendar and safety checks. Approve, Edit and Reject stay pinned at the top. Edit with “Keep Wednesday’s run in the evening” re-plans it for right after pickup. Approve writes the change to the synthetic calendar and plan inside the prototype (downloadable), and the Plan manager records it as a numbered version that can be reverted.

For Marcus, who asks to run on a swollen ankle, the agent refuses, points him to a clinician with three questions to bring, and offers only his own choices: keep the plan, pause it, record rest, or plan around his clinician’s guidance. Every reply can be rated thumbs up or down, every run and decision is logged, and the Evals view shows all five cases with my recorded verdicts (5 of 5 Pass in round 3).

### Draft D: Row 43, video outline (short version matching the script)
- **0:00–0:50, problem:** fitness-focused people training 3–6 days a week skip sessions when life disrupts the plan; research shows adherence drives results (63% of new gym members quit within 3 months; athletes completing over 80% of planned weeks were 7× more likely to hit their goal).
- **0:50–1:35, solution:** the agent workflow diagram: report, read, decide (ask if information is missing; refuse on illness or injury), propose with cited rules, prototype checks, athlete approves, edits or rejects. Measured as planned sessions kept.
- **1:35–2:35, live demo with real AI:** Annie, then Edit to the evening, then Approve; then Marcus’s refusal and his choices.
- **2:35–3:30, evaluation:** five test cases and three rounds, including the Leo failure that was traced to the prototype’s counting and fixed.
- **3:30–3:45, close:** the hard part was knowing when not to plan; next steps are real Notion and Garmin data, voice, and a research agent that proposes rules for approval.

### Draft E: Row 46, video check (after recording)
Yes. The video follows a 3:45 script: the problem and the adherence research, the agent workflow, a live real-AI demo (Annie’s proposal, an edit and an approval, then Marcus’s refusal), the five test cases across three rounds of evaluation, and the takeaway with next steps. Each part is on screen, so a reviewer can follow the loop without the PRD.
