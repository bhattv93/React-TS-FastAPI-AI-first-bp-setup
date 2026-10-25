Babysit the current branch's pull request. Work through this in order and stop when nothing is pending.

1. If CI is red, read the failing job log, diagnose the cause, and make the smallest fix on this branch.
   Run `just check` locally before pushing. Never weaken a gate, lower a coverage threshold or edit a
   generated file to make it pass.
2. If new review comments arrived, address each one with a code or answer. Do not resolve threads you
   did not address.
3. If the branch is behind `main`, rebase only when it is clean; otherwise report the conflict.
4. If everything is green and quiet, reply with one line saying so and stop.

Rules: never push to `main`, never force-push, never merge. Report what you changed in two lines.
