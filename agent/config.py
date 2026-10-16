"""Model settings for the Workout Program Manager prototype."""

MODEL = "claude-opus-5-5"
MAIN_EFFORT = "high"        # main agent: triage, questions, drafting
VERIFIER_EFFORT = "medium"  # verification sub-agent
FALLBACK_BETA = "server-side-fallback-2026-07-01"  # re-runs a safety-declined request on a recommended fallback model
MAX_REDRAFTS = 2            # after 2 failed redrafts, the proposal goes to the user with open issues flagged
MAX_TURNS = 30              # safety stop for the agent loop
