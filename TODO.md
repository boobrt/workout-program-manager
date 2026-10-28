# Capstone tracker: Workout Program Manager

## North-star goal (what this whole project is for)
> **Draft. Confirm or edit in Session 1.**
> Show, through a capstone-quality AI PRD, spec, working prototype, and 4-minute video, that an AI agent can keep a busy, frequently traveling athlete progressing toward their training goal when life disrupts the plan. It does this by proposing safe, evidence-informed plan changes that the athlete reviews and approves, instead of the athlete rebuilding the plan by hand or skipping workouts.

## Course deliverables (Product Faculty AIPM capstone)
- [ ] **AI PRD**, submitted in the course's Google Doc template (shared with assignments@productfaculty.com)
- [ ] **4-minute video**: problem → demo → evaluation set → results. Skip prompt syntax.
- [ ] Confirm submission deadlines on the course portal

---

## Session log
| # | Date | Session goal | Outcome |
|---|---|---|---|
| 1 | 2026-10-07 | Interview → draft the PRD | In progress |
| 2 | 2026-10-13 | Build the LMS prototype from the Product Faculty build kit | `prototype.zip` built and passes the upload check; sample mode tested; real-AI eval runs still to do |

---

## To-do

### Phase 2 · Design (current)
- [x] **PRD**: written in the Product Faculty Capstone Studio; latest export filed as `docs/capstone-prd.xlsx` (Oct 28, 2026). The earlier plan for `docs/PRD.md` by interview was replaced by this.
  - [ ] Overview and problem (with evidence)
  - [ ] Goals and non-goals
  - [ ] Users and personas
  - [ ] Scope and phases (v1 / v2 / later)
  - [ ] Stakeholders
  - [ ] Functional requirements
  - [ ] Non-functional requirements (latency, cost, reliability, privacy)
  - [ ] Success metrics: business + AI + guardrails
  - [ ] Dependencies, assumptions, risks
  - [ ] Timeline / milestones
  - [ ] Open questions and decision log
- [ ] **Spec** (`docs/SPEC.md`), after the PRD is approved
  - [ ] Architecture and agent flow (from the workflow diagram)
  - [ ] Agent behaviors and decision rules
  - [ ] Tool contracts and data schemas
  - [ ] Prompt specs and versioning
  - [ ] Memory and state
  - [ ] Error handling and fallbacks
  - [ ] Evaluation plan and acceptance criteria
- [ ] **Wireframes** for the pop-up: report a change → questions → proposal → Accept / Edit / Reject
- [ ] Resolve open design decisions (below)

### Phase 3 · Develop (paused 2026-10-07)
- [x] Annie data kit, answer key, and graders
- [x] Annie agent loop (offline tests pass)
- [x] API key saved in `.env`
- [ ] First live Annie run, then grade it
- [ ] Update the agent and data to match any Design changes
- [x] Data for Greg, Dora, Marcus, and Leo (`personas/<name>/`, 2026-10-13)
- [x] LMS prototype: `prototype/` (source) → `prototype.zip` (upload file), 2026-10-13
- [ ] Run the five Evals in the prototype with a real key, pick verdicts, fix the worst, rerun, Copy results
- [ ] Python agent (`agent/`): add case.json for Greg, Dora, Marcus, and Leo
- [ ] Evals across all cases (Arize tracing optional)
- [ ] Connect to Notion (calendar + plan)

### Phase 4 · Deploy
- [ ] Launch plan, guardrails, monitoring, and rollback
- [ ] Final metrics and results write-up

### Deliverables
- [ ] Submit the PRD (`docs/capstone-prd.xlsx`, the course's Agentic AI PRD template) the way the course asks
- [ ] Script and record the 4-minute video

---

## Open design decisions
| # | Question | Status |
|---|---|---|
| D1 | Minor illness (Greg): may the agent reschedule around it, or must it leave the plan unchanged? | Prototype: leaves it unchanged; records rest only if Greg asks, as his choice (per kit PRD) |
| D2 | Button label: Approve or Accept | Prototype uses Approve |
| D3 | Edit flow: conversation or form | Leaning conversation |
| D4 | How far ahead the agent shows changes: next 1–2 weeks + standing rule, or every remaining week | Open |
| D5 | When a disruption needs a re-planned block instead of moved sessions (Dora, long illness) | Open |
| D6 | What the agent remembers vs. asks again each time | Partly decided |
