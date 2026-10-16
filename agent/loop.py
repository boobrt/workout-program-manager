"""Main agent loop for the Workout Program Manager (single agent with a verification sub-agent)."""
import json

from . import verify
from .config import FALLBACK_BETA, MAIN_EFFORT, MAX_REDRAFTS, MAX_TURNS, MODEL
from .state import load_rules

SYSTEM = """You are the Workout Program Manager, an agent that helps one person keep their training on track when life disrupts their schedule. You adapt their existing plan. You never replace their program or change their goal.

## How a request flows
1. The user describes a schedule change. Read the sources you need before deciding anything. The workout plan, calendar, memory, and rules library are almost always relevant. The Garmin files show how training is actually going (adherence, fatigue).
2. Do safety triage before any planning. If the user reports an injury, pain, medical symptoms, or a chronic condition, or asks whether it's safe to train, call stop_and_refer and don't draft a plan. Scheduling around a minor illness the user reports is fine, but never tell anyone to train while unwell; they decide.
3. When a preference or fact you need is missing (for example, whether they'll train in the morning, who watches the kids, or whether a recurring conflict should change every week), call ask_user. Ask one focused question at a time, and only questions whose answer would change the plan. Don't ask what the data already answers.
4. Draft the revised schedule and call submit_proposal. A verification sub-agent checks it. If it reports issues, fix them and resubmit. If the user chooses Edit, treat their feedback as new constraints and resubmit.

## Planning principles
- Preserve the program's intent. Protect quality sessions (intervals, tempo, long run); move them only if the disruption forces it.
- Prefer the smallest change that works: same day at another time, then another day in the same week, then shortening, then skipping.
- Keep easy sessions easy. Never add intensity or volume to make up for a change.
- Respect every busy block on the calendar and every preference in memory.
- If the conflict recurs, handle the remaining weeks with a standing rule, not just this week.
- State the trade-offs plainly.

## Sources and honesty
Cite only rules from the rules library, by ID: R1-R6 are research, B1-B4 are coaching practice, C1-C6 are product policies. Attach an ID only when that rule genuinely supports the reason. The app shows R rules as research citations and B rules as coaching practice, so a wrong ID misleads the user. If no rule supports a reason, give the reason without an ID.

## Proposal format (submit_proposal)
- sessions: the complete set of runs for every week shown on the calendar after your changes, including unchanged runs. Dates YYYY-MM-DD, times HH:MM (24-hour). intensity is "quality" for intervals, tempo, and long runs, otherwise "easy".
- changes: one row per changed session, plus a "standing_rule" row if you set one. Keep cells short, like "Wed Oct 7, 5:45 pm, Easy 6 mi".
- reasons: one short sentence per change, with rule IDs only where they apply.
- Write for a busy person: short sentences, plain language.

You can't write to the calendar or the plan yourself. The app writes your proposal only after the user selects Accept."""

TOOLS = [
    {
        "name": "read_source",
        "description": "Read one of the user's data sources: the Notion workout plan (Markdown), the Notion calendar (CSV), the Garmin activity export, the Garmin daily wellness export, the agent's memory of this user, or the training rules library.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {"source": {"type": "string", "enum": ["workout_plan", "calendar", "garmin_activities", "garmin_wellness", "memory", "rules_library"]}},
            "required": ["source"],
            "additionalProperties": False,
        },
    },
    {
        "name": "ask_user",
        "description": "Ask the user one focused question when a preference or fact that would change the plan is missing. Returns their answer.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {"question": {"type": "string"}},
            "required": ["question"],
            "additionalProperties": False,
        },
    },
    {
        "name": "stop_and_refer",
        "description": "Stop without drafting a plan because the request involves injury, pain, medical symptoms, a chronic condition, or a question about whether it's safe to train. The plan stays unchanged.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {"type": "string", "description": "Internal note: why this is a medical red flag"},
                "message_to_user": {"type": "string", "description": "Kind, short message recommending a doctor or qualified clinician and offering to pause or reschedule if they choose"},
            },
            "required": ["reason", "message_to_user"],
            "additionalProperties": False,
        },
    },
    {
        "name": "submit_proposal",
        "description": "Submit a drafted schedule change. It's checked by the verification sub-agent, then shown to the user with Accept / Edit / Reject. Returns the verifier's issues, or the user's decision.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {"type": "string", "description": "One sentence describing the change"},
                "changes": {"type": "array", "items": {
                    "type": "object",
                    "properties": {
                        "week": {"type": "string", "description": "e.g. 'Week 10' or 'Weeks 12-18'"},
                        "original": {"type": "string"},
                        "proposed": {"type": "string"},
                        "change_type": {"type": "string", "enum": ["move", "shorten", "replace", "skip", "rest", "standing_rule"]},
                    },
                    "required": ["week", "original", "proposed", "change_type"],
                    "additionalProperties": False}},
                "reasons": {"type": "array", "items": {
                    "type": "object",
                    "properties": {"text": {"type": "string"}, "rule_ids": {"type": "array", "items": {"type": "string"}}},
                    "required": ["text", "rule_ids"],
                    "additionalProperties": False}},
                "tradeoffs": {"type": "array", "items": {"type": "string"}},
                "standing_rule": {"type": "string", "description": "Empty string if none"},
                "assumptions": {"type": "array", "items": {"type": "string"}},
                "sessions": {"type": "array", "items": {
                    "type": "object",
                    "properties": {
                        "session": {"type": "string", "enum": ["intervals", "easy", "tempo", "long"]},
                        "date": {"type": "string"},
                        "start": {"type": "string"},
                        "end": {"type": "string"},
                        "miles": {"type": "number"},
                        "intensity": {"type": "string", "enum": ["easy", "quality"]},
                    },
                    "required": ["session", "date", "start", "end", "miles", "intensity"],
                    "additionalProperties": False}},
            },
            "required": ["summary", "changes", "reasons", "tradeoffs", "standing_rule", "assumptions", "sessions"],
            "additionalProperties": False,
        },
    },
]


def render_proposal(proposal, rules, open_issues=None):
    lines = [f"\n{'=' * 72}", "PROPOSED CHANGES", f"{'=' * 72}", proposal["summary"], ""]
    rows = [("Week", "Original", "Proposed", "Change")] + [
        (c["week"], c["original"], c["proposed"], c["change_type"]) for c in proposal["changes"]]
    widths = [max(len(r[i]) for r in rows) for i in range(4)]
    for n, r in enumerate(rows):
        lines.append(" | ".join(cell.ljust(widths[i]) for i, cell in enumerate(r)))
        if n == 0:
            lines.append("-+-".join("-" * w for w in widths))
    lines += ["", "Why:"]
    for reason in proposal["reasons"]:
        tags = []
        for rid in reason["rule_ids"]:
            rule = rules.get(rid)
            if rule and rule["section"] == "A":
                tags.append(f"[{rule['label']}]({rule['url']})")
            elif rule and rule["section"] == "B":
                tags.append("(coaching practice)")
            elif rule and rule["section"] == "C":
                tags.append("(safety policy)")
        lines.append(f"  - {reason['text']}" + (f"  {' '.join(tags)}" if tags else ""))
    if proposal["standing_rule"]:
        lines.append(f"\nStanding rule: {proposal['standing_rule']}")
    if proposal["tradeoffs"]:
        lines.append("\nTrade-offs:")
        lines += [f"  - {t}" for t in proposal["tradeoffs"]]
    if proposal["assumptions"]:
        lines.append("\nAssumptions:")
        lines += [f"  - {a}" for a in proposal["assumptions"]]
    if open_issues:
        lines.append("\n!! Not fully verified. Open issues the agent couldn't resolve:")
        lines += [f"  - {i}" for i in open_issues]
    lines.append(f"\n[A]ccept   [E]dit   [R]eject\n{'=' * 72}")
    return "\n".join(lines)


def run(client, state, ui):
    """Run one disruption request end to end. Returns the outcome dict."""
    rules = load_rules()
    case = state.case
    messages = [{"role": "user", "content": f"Current date and time: {case.now}.\n\nMessage from the user:\n{case.message}"}]
    qa_pairs, attempts, final_proposal = [], 0, None
    outcome = {"status": "unfinished"}
    state.log("user_request", message=case.message)

    for _ in range(MAX_TURNS):
        response = client.beta.messages.create(
            model=MODEL,
            max_tokens=16000,
            betas=[FALLBACK_BETA],
            fallbacks="default",
            thinking={"type": "adaptive", "display": "summarized"},
            output_config={"effort": MAIN_EFFORT},
            cache_control={"type": "ephemeral"},
            system=SYSTEM,
            tools=TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})
        for block in response.content:
            if block.type == "thinking" and block.thinking:
                ui.thinking(block.thinking)
            elif block.type == "text" and block.text.strip():
                ui.agent_says(block.text)

        if response.stop_reason == "refusal":
            outcome = {"status": "refused", "detail": str(getattr(response, "stop_details", ""))}
            break
        if response.stop_reason == "max_tokens":
            outcome = {"status": "error", "detail": "Hit max_tokens"}
            break
        tool_uses = [b for b in response.content if b.type == "tool_use"]
        if not tool_uses:
            # The agent replied in plain text; pass the user's reply back as a normal turn.
            reply = ui.ask(None)
            qa_pairs.append(("(agent message)", reply))
            messages.append({"role": "user", "content": reply})
            continue

        results, finished = [], False
        for tool in tool_uses:
            state.log("tool_call", tool=tool.name, input=tool.input)
            if tool.name == "read_source":
                ui.status(f"reading {tool.input['source']}")
                content = state.read(tool.input["source"])

            elif tool.name == "ask_user":
                answer = ui.ask(tool.input["question"])
                qa_pairs.append((tool.input["question"], answer))
                state.log("user_answer", question=tool.input["question"], answer=answer)
                content = answer

            elif tool.name == "stop_and_refer":
                ui.agent_says(tool.input["message_to_user"])
                outcome = {"status": "referred", "reason": tool.input["reason"]}
                content, finished = "Stopped and referred. No plan changes were made.", True

            elif tool.name == "submit_proposal":
                proposal = tool.input
                attempts += 1
                ui.status(f"verification sub-agent checking draft {attempts}")
                checks = verify.deterministic_checks(proposal, state, rules)
                verdict = verify.review(client, proposal, checks, state, [{"question": q, "answer": a} for q, a in qa_pairs])
                code_fails = [c for c in checks if c["severity"] == "fail"]
                passed = verdict["verdict"] == "pass" and not code_fails
                state.log("verification", attempt=attempts, passed=passed, code_checks=checks, verdict=verdict)
                issues = [f"{c['check']}: {c['detail']}" for c in code_fails] + \
                         [f"{i['check']}: {i['problem']} (fix: {i['fix']})" for i in verdict["issues"]]

                if not passed and attempts <= MAX_REDRAFTS:
                    ui.status(f"draft {attempts} failed verification; redrafting")
                    content = (f"Verification failed (draft {attempts} of {MAX_REDRAFTS + 1}). Fix these issues and call "
                               "submit_proposal again:\n- " + "\n- ".join(issues))
                else:
                    final_proposal = proposal
                    ui.show(render_proposal(proposal, rules, None if passed else issues))
                    decision, feedback = ui.decide()
                    state.log("user_decision", decision=decision, feedback=feedback, verified=passed)
                    if decision == "accept":
                        state.apply_approved(proposal, qa_pairs)
                        ui.status("changes written to the calendar and workout plan")
                        outcome = {"status": "accepted", "verified": passed, "drafts": attempts}
                        content, finished = "The user accepted. The app wrote the changes.", True
                    elif decision == "reject":
                        outcome = {"status": "rejected", "verified": passed, "drafts": attempts}
                        content, finished = "The user rejected the proposal. Nothing was changed.", True
                    else:
                        qa_pairs.append(("Edit feedback on the proposal", feedback))
                        attempts = 0
                        content = (f"The user chose Edit. Their feedback: {feedback}\n"
                                   "Revise the proposal to fit this and call submit_proposal again. Ask a question first only if the feedback leaves something essential unclear.")
            else:
                content = f"Unknown tool {tool.name}"
            results.append({"type": "tool_result", "tool_use_id": tool.id, "content": content})

        messages.append({"role": "user", "content": results})
        if finished:
            break
    else:
        outcome = {"status": "error", "detail": f"No result after {MAX_TURNS} turns"}

    state.log("outcome", **outcome)
    state.save(messages, outcome, final_proposal)
    return outcome


class ConsoleUI:
    """Terminal stand-in for the app's pop-up."""

    def __init__(self, show_thinking=False):
        self.show_thinking = show_thinking

    def status(self, text):
        print(f"  · {text}")

    def thinking(self, text):
        if self.show_thinking:
            print(f"  (thinking) {text.strip()[:600]}")

    def agent_says(self, text):
        print(f"\nAgent: {text.strip()}\n")

    def show(self, text):
        print(text)

    def ask(self, question):
        if question:
            print(f"\nAgent asks: {question}")
        return input("You: ").strip()

    def decide(self):
        while True:
            choice = input("Your choice (A/E/R): ").strip().lower()[:1]
            if choice == "a":
                return "accept", ""
            if choice == "r":
                return "reject", ""
            if choice == "e":
                return "edit", input("What should change? ").strip()


class ScriptedUI(ConsoleUI):
    """Answers questions and decisions from the case file, so eval runs are repeatable."""

    def __init__(self, answers, decisions, show_thinking=False):
        super().__init__(show_thinking)
        self.answers, self.decisions = list(answers), list(decisions)

    def ask(self, question):
        if question:
            print(f"\nAgent asks: {question}")
        answer = self.answers.pop(0) if self.answers else "No preference. Use your best judgment."
        print(f"You (scripted): {answer}")
        return answer

    def decide(self):
        decision = self.decisions.pop(0) if self.decisions else {"decision": "accept", "feedback": ""}
        print(f"Your choice (scripted): {decision['decision']} {decision.get('feedback', '')}")
        return decision["decision"], decision.get("feedback", "")
