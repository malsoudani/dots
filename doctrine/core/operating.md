# Doctrine — operating instructions

You are working under Doctrine, a set of engineering standards. Rules have stable
IDs (for example `BE-TXN-1`). Apply them like this:

1. Precedence: the user's explicit instruction, then this project's own
   instructions and conventions, then Doctrine, then your defaults. When Doctrine
   conflicts with the project, follow the project and say so in one line.
2. Before writing code, name the layer that owns each change (server: transport,
   service, persistence; client: presentation, manager, service, model). If you
   cannot name it, decide before you type.
3. Change only what the task needs. Do not refactor code you were not asked to touch.
4. Before you finish, run the checklist for each area you touched. Report every
   rule you could not meet by ID, with the reason.
5. When reviewing, report findings as: rule ID, file:line, evidence, a concrete
   failure scenario, and a fix. Verify a finding before you assert it.
6. Never invent a rule ID. If no rule applies, reason from the principles (P1-P14).