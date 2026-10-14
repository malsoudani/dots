# Delivery rules

Delivery is the part of engineering where mistakes are public. The rules here make
each step small, checked, and reversible.

## Continuous integration

### D-1 · CI gates every change: lint, types, tests, deploy checks
<!-- doctrine: severity=RED tier=micro principles=P7,P12 -->

**Rule.** Every change runs lint, type checking or build, the test suite, the production configuration check, the pending-migration check and workflow lint before it can merge.
**Why.** Whatever CI does not run is unprotected. A unit-test runner that exists but is not in CI is a suggestion.
**How.** One workflow on pull requests and on the main branch. A red main stays visible; do not cancel main-branch runs.
**Check.** Does CI run every check the project relies on, including the newly added one?

### D-2 · CI has least privilege and pinned dependencies
<!-- doctrine: severity=ORANGE tier=compact principles=P13 -->

**Rule.** Workflows default to read-only permissions and grant more per job. Third-party actions are pinned to a commit. Check jobs need no cloud credentials.
**Why.** A check job that can assume a cloud role is a deploy credential handed to every pull request.
**How.** Top-level `permissions: contents: read`; identity tokens only on the deploy job; offline plans and tests.
**Check.** Do check jobs run without cloud credentials and are all actions pinned to a commit?

## Deploy

### D-3 · A deploy workflow re-tests before it ships
<!-- doctrine: severity=ORANGE tier=compact principles=P12 -->

**Rule.** The deploy workflow runs the tests itself before packaging, including on a rollback.
**Why.** Separate workflows run in parallel; "CI was green" is not something the deploy workflow can know.
**How.** A test job the package job depends on, checking out the exact revision being shipped.
**Check.** Does the deploy workflow run the test suite on the revision it ships?

### D-4 · Gate deploys with an explicit switch checked before credentials
<!-- doctrine: severity=ORANGE tier=compact principles=P12 -->

**Rule.** Deploy jobs run only when an explicit enable flag is set, evaluated at the job level before any credential step. When off, the workflow prints why.
**Why.** A half-configured environment must not reach the credential step with empty values.
**How.** `if: vars.DEPLOY_ENABLED == 'true'` on the job; a notice job for the off state; enable the flag last.
**Check.** Is the gate a job-level condition that runs before credentials are requested?

### D-5 · Know what triggers a deploy; baked configuration needs a rebuild
<!-- doctrine: severity=ORANGE tier=compact principles=P12 -->

**Rule.** The team knows which paths trigger each deploy. Configuration inlined at build time changes only through a rebuild; configuration read at start changes only through a redeploy.
**Why.** A merge that touches only infrastructure or only a variable deploys nothing, and everyone assumes it did.
**How.** Document path filters; changing a variable or a secret is followed by a manual run of the right workflow.
**Check.** After this change merges, is a manual deploy or rebuild needed, and is that written in the change description?

### D-6 · Releases are additive until an atomic swap, then health-gated
<!-- doctrine: severity=RED tier=compact principles=P12,P5 -->

**Rule.** A release is fetched, installed, migrated and prepared beside the running one. Traffic moves in one atomic step. A health check follows; failure swaps back automatically.
**Why.** A failure before the swap leaves the old release serving. A failure after it degrades to "pipeline red, site up".
**How.** Versioned release directories, a symlink or pointer swap, a retrying health check, keep the last few releases. Rollback is the same pipeline with an older revision.
**Check.** Can every step before the swap fail without affecting traffic, and does a failed health check restore the previous release?

### D-7 · Assert the safety net before any irreversible step
<!-- doctrine: severity=RED tier=compact principles=P12 -->

**Rule.** Before a step that cannot be undone (a deleting sync, a schema migration), the pipeline verifies its safety net exists (versioning enabled, snapshot taken) and refuses to continue otherwise.
**Why.** The safety net is usually owned by a different system and configured at a different time. Assuming it is there is how data is lost.
**How.** A pre-flight step that asserts and exits non-zero with an explicit message. Assert only; never create the safety net from the deploy job.
**Check.** Is each irreversible step preceded by an assertion of its safety net?

### D-8 · Publish hashed assets first, the entry document last and uncached
<!-- doctrine: severity=ORANGE tier=compact principles=P12 -->

**Rule.** Content-addressed assets are uploaded first with a long immutable cache lifetime. The entry document is uploaded last with no caching and never the immutable header.
**Why.** Uploading the entry document first serves a page whose assets do not exist yet. Caching it immutably pins every user to a stale shell.
**How.** Two sync steps in that order, then an invalidation, then a smoke check.
**Check.** Is the entry document uploaded after its assets and served uncached?

### D-9 · Verify a deploy by observing new behavior at the public edge
<!-- doctrine: severity=ORANGE tier=micro principles=P12 -->

**Rule.** After a deploy, request the public endpoint and confirm behaviour that only the new revision has.
**Why.** A green pipeline says the steps ran. It does not say the new code is what users reach.
**How.** Fetch the new asset name or a response the old revision could not produce; check a deep link, the API health and a cross-origin preflight.
**Check.** Does the change description record evidence taken from the public endpoint after deploy?

## Source control

### D-10 · Work in a fresh branch from current main, never in a dirty checkout
<!-- doctrine: severity=ORANGE tier=compact principles=P12 -->

**Rule.** Each task starts in its own branch and working copy created from the current remote main. Uncommitted files in someone's checkout are not staged, stashed, reverted or cleaned.
**Why.** A dirty checkout holds someone's work in progress. Mixing a task into it loses one or the other.
**How.** One worktree per task; one clean commit per logical change; delete the branch after merge.
**Check.** Was the work done in a task-specific branch from current main with no unrelated files touched?

### D-11 · Re-fetch and compare before squashing; check for silent removals
<!-- doctrine: severity=RED tier=micro principles=P12 -->

**Rule.** Before squashing, rebasing or opening a change, fetch the remote and confirm the base has not moved. Read the list of files the change touches against the current base and look for removals you did not make.
**Why.** Squashing a branch onto a base that moved underneath it re-applies the old tree and silently reverts whatever landed in between. One such squash nearly removed a feature merged hours earlier, and every check was green.
**How.** `git fetch`; compare the branch point with the remote head; `git diff <base> --name-only` and `--stat`; merge the base in and re-run the checks if it moved.
**Check.** Does the diff against the current base contain only changes this task intended?

### D-12 · Infrastructure applies are deliberate, never automatic from defaults
<!-- doctrine: severity=ORANGE tier=compact principles=P12 -->

**Rule.** Infrastructure changes are applied by an explicit, authenticated action with real variables. CI plans and tests offline and never applies example values.
**Why.** An automatic apply of placeholder variables against live state is a time bomb held back only by a permissions error.
**How.** CI: format, validate, offline plan and tests. Apply: a human or a protected workflow with real inputs.
**Check.** Can CI apply infrastructure without a deliberate human or protected step?

### D-13 · A pull request states what, why, contract changes, evidence, and rollback
<!-- doctrine: severity=YELLOW tier=compact principles=P7 -->

**Rule.** The change description has: a summary and reason, contract changes, verification evidence (commands and results), deploy notes and rollback, and follow-ups not done.
**Why.** The description is the record the next person reads when this change is suspected. Evidence written at the time is worth more than recollection.
**How.** Use those five headings. Paste counts and outcomes, not adjectives.
**Check.** Does the description contain all five parts with concrete evidence?