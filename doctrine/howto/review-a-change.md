# Review a change against Doctrine

A review is an attempt to find the failure before a user does. This is the procedure
a person or an agent follows, from establishing the base to recording the outcome.

## 1. Establish the base and read the diff

Fetch the remote and confirm the base has not moved (`D-11`). Read the diff against
the current base, not against your memory of an earlier one. List the files the
change touches and check for removals you did not expect. A change that silently
reverts a file merged in between looks green from every other angle.

Record the base commit and the list of files before you start. Every finding later
cites a file and line in that diff.

## 2. Run the six lenses

Review the change once per lens (`R-1`). Each lens is a separate pass; a single pass
only finds what you already suspect.

**Lens 1 — Regression against previous behavior.** Compare the new code with what it
replaced. Ask: what did the old code do that the new code no longer does? Which
callers depended on the old shape? Is any behavior that was correct before now
silently different? Maps to `BE-STRUCT-*`, `FE-STRUCT-*`, `CT-7`.

**Lens 2 — Correctness of the new code.** Contains rules: does the service method do
what its name says? Are the branches complete? Is the derivation computed once
(`BE-SVC-7`)? Are the states exhaustive and the dispatch total (`FE-STATE-3`)? Maps
to `BE-DOM-*`, `BE-SVC-*`, `FE-STATE-*`, `FE-MGR-*`.

**Lens 3 — Architecture rules.** Is every decision in its one layer? Does the
handler do only parse, call, respond (`BE-API-1`)? Does the manager own sequencing
(`FE-MGR-2`)? Does the dependency direction hold (`BE-STRUCT-2`, `FE-STRUCT-2`)?
Maps to `P1`, `P6`, `P8`, `P10`.

**Lens 4 — Security.** Are all lookups scoped to the caller (`BE-API-6`)? Is
everything client-controlled capped (`BE-API-7`)? Is authentication default-deny
(`BE-API-5`)? Does any response echo upstream or configuration detail (`BE-API-4`)?
Is any secret in the client bundle (`FE-SVC-9`)? Maps to `P13`.

**Lens 5 — CI and deploy risk.** Does CI run every check the project needs (`D-1`)?
Is the deploy gated and health-checked (`D-4`, `D-6`)? Is a safety net asserted
before any irreversible step (`D-7`)? Maps to `P12`.

**Lens 6 — Test quality.** Does each new behavior have a test at its layer's boundary
(`T-1`)? Was each regression test seen red (`T-2`)? Do failure paths have tests
(`T-3`)? Does each test assert what its name claims (`T-5`)? Maps to `P11`.

**Contract pass (cross-side changes only).** Enumerate every request the client can
send and check each against the server's current validation (`CT-7`). Check the
response shape and status codes both sides act on (`CT-1`, `CT-2`). Confirm the write
returns the read shape (`CT-5`).

## 3. Write findings in the required format

Every finding has five parts (`R-2`): rule ID, file and line, the exact code, a
concrete failure scenario, and a fix. No style remarks. The format:

```
RULE-ID · severity · file:line · evidence · scenario · fix
```

A RED finding, fully written:

```
BE-TXN-1 · RED · invitations/service.py:41 · `create_invitation` calls
`Invitation.objects.create(...)` then `Team.objects.get_or_create(...)` with no
`transaction.atomic`. · If the second write raises, the first row persists with no
invitation to explain it — every failed attempt leaves an orphan. · Wrap the method
body in `with transaction.atomic():`, and add a rollback test (`T-3`).
```

A YELLOW finding, fully written:

```
FE-STATE-8 · YELLOW · invitations/pages/InvitationsPage.tsx:88 · the page branches on
`state.providerLabel === "Google"` to choose a message. · Renaming the label in the
copy module silently changes which branch runs; the manager state now holds UI text. ·
Store `provider: "google" | "microsoft"` on the state and map it to words in the
presentation copy module.
```

## 4. Verify before acting

Try to refute each finding before it is reported as real (`R-3`). Three questions:
can I refute it by reading the code paths? Can I reproduce it with a concrete input?
What actually happens to a user? Drop findings that do not survive. Majority decides
when the reviewers disagree. Mark each acted-on finding as verified and say how.

## 5. Fix round and independent re-audit

After the fixes, someone other than the fixer checks each finding against the new
diff, re-runs the checks, and looks for problems the fixes introduced (`R-4`). Use
this table:

| Finding | Severity | Status | Evidence after fix |
| --- | --- | --- | --- |
| `BE-TXN-1` service.py:41 | RED | Resolved | rollback test green; no orphan on forced failure |
| `FE-STATE-8` page:88 | YELLOW | Deferred | ledger `FE-STATE-8·2026-10-13`; label now an identifier |

## 6. Product run

Before merge, drive the change through the real interface against a real backend
(`R-6`): the main journey, the failure the change addresses, the auth edge cases
(expired token, foreign ID), and every feature-flag state the change touches. Watch
the network log and the console. Record each check and its result.

## 7. Record the outcome

Unfixed findings go in the append-only debt ledger (`R-5`), one file per repository:

```
ID: BE-TXN-3·2026-10-13
Severity: RED
Change: <change reference>
Files: invitations/service.py
What: uniqueness race recovered outside a savepoint
Why: <reason it was not fixed now>
Disposition: fix in next change
Status: open
```

Entries are marked resolved, never deleted. The merge decision (`R-7`): a change
merges automatically only when checks are green, the review has no open findings and
QA passed. State the three results in the change; if any is not clean, stop and ask a
person. When QA runs, record it:

| Flow | Layer | Result | Evidence |
| --- | --- | --- | --- |
| Invite a member | browser | pass | invitation appears in the list |

| Rollback after late failure | api | pass | no rows persisted |