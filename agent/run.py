"""Run the Workout Program Manager on a test case.

Interactive (you answer the agent's questions and choose Accept / Edit / Reject):
    .venv/bin/python -m agent.run annie

Scripted (answers and decisions come from the case file, for repeatable eval runs):
    .venv/bin/python -m agent.run annie --scripted

Add --thinking to print summaries of the agent's reasoning.
"""
import argparse
import os
import sys

import anthropic

from .loop import ConsoleUI, ScriptedUI, run
from .state import ROOT, Case, RunState


def load_env_file():
    """Read ANTHROPIC_API_KEY from capstone/.env if it isn't already set in the shell."""
    env = ROOT / ".env"
    if "ANTHROPIC_API_KEY" in os.environ or not env.exists():
        return
    for line in env.read_text().splitlines():
        key, _, value = line.partition("=")
        if key.strip() and not key.startswith("#") and value.strip():
            os.environ.setdefault(key.strip(), value.strip().strip('"'))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("persona", help="folder name under personas/, e.g. annie")
    parser.add_argument("--scripted", action="store_true", help="use the answers and decisions in case.json")
    parser.add_argument("--thinking", action="store_true", help="show summaries of the agent's reasoning")
    args = parser.parse_args()

    load_env_file()
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
        sys.exit("No API key found. Copy .env.example to .env and paste your key after ANTHROPIC_API_KEY=")
    case = Case.load(args.persona)
    state = RunState(case)
    ui = (ScriptedUI(case.scripted_answers, case.scripted_decisions, args.thinking)
          if args.scripted else ConsoleUI(args.thinking))

    print(f"\nCase {case.case_id} · {case.now}\nUser: {case.message}\n")
    try:
        outcome = run(anthropic.Anthropic(), state, ui)
    except anthropic.AuthenticationError:
        sys.exit("No valid API key. Put ANTHROPIC_API_KEY=... in capstone/.env (see .env.example).")
    except anthropic.APIConnectionError:
        sys.exit("Couldn't reach the Claude API. Check your internet connection.")
    except anthropic.RateLimitError:
        sys.exit("Rate limited by the Claude API. Wait a minute and try again.")
    except anthropic.APIStatusError as e:
        sys.exit(f"Claude API error {e.status_code}: {e.message}")

    print(f"\nOutcome: {outcome}\nRun saved to: {state.dir.relative_to(ROOT)}")
    if (state.dir / "proposal.json").exists():
        print(f"Grade it:    .venv/bin/python tools/check_proposal.py {(state.dir / 'proposal.json').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
