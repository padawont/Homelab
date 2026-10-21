"""Recording harness and scoring layer for the Homelab PKM agent roster.

See ``tests/README.md`` for how to run it, and ``./.opencode/WORKFLOW.md`` for the
handoff contracts these tests assert against.

The pipeline is deliberately split in two:

1. **Record** (``run_agent``, ``workspace``) -- invoke one agent with one prompt in a
   throwaway repository clone and persist the raw event stream verbatim.
2. **Score** (``catalog``, ``prompts``, ``evaluators``, ``datasets``) -- read those
   responses back and grade them with Pydantic Evals.

The raw response is always written before any evaluator sees it.
"""
