# Agent instructions (Codex and other agents)

Read these first, in order:

1. `HANDOFF.md`: current state, how to run the best recipe, open problems, and the
   shared-workspace rules. Claude and Codex both keep it up to date.
2. `CLAUDE.md`: the full project instructions and research log (the same rules apply
   to every agent; "Claude" there means whichever agent is working).

Shared workspace rule: keep all work inside this project directory. Public code and
docs go in tracked folders. Private research, run outputs and scratch tools go in the
ignored `.local/` tree:
- `.local/re`
- `.local/runs`
- `.local/claude-scratch`
- `.local/codex-scratch`

Never keep results only in an agent-private temp folder. Before you stop, update
`HANDOFF.md` (state, what you tried, what to do next) and push to `main`.
