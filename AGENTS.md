# Rules for any agent working in this repo
1. docs/reference/ is the source of truth. Read decisions.md and
   needs-confirmation.md before writing code.
2. Never state Epicor behavior from memory. If the reference doesn't cite it,
   show the banner "Default chosen for the lab, not confirmed against Epicor."
3. Never commit anything under answers/, exam/, labs/*/answers/, or any
   screenshot folder. Run `git status --ignored` before every commit.
4. No Epicor screenshots, logos, RDL text or UI look in any file.
5. Work on its own branch (antigravity/<phase>); never push to main.
6. Missing-column findings say "required per cited source [S#]",
   never "Epicor requires".
