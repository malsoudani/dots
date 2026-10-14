# Review rules

A review is an attempt to find the failure before a user does. It is done from
several independent angles, its findings are verified, and its outcome is recorded.

## Review

### R-1 · Review through independent lenses
<!-- doctrine: severity=YELLOW tier=compact principles=P11 -->

**Rule.** Review a change separately for: regression against the previous behaviour, correctness of the new code, architecture rules, security, CI and deploy risk, and test quality. For a change spanning client and server, add a contract pass.
**Why.** One pass looks for what the reviewer already suspects. Separate lenses find different defects; the worst defect in one review was found only by the regression lens.
**How.** One pass (or one reviewer or agent) per lens, each reading the diff against the base.
**Check.** Was each lens applied, and is the outcome of each recorded?

### R-2 · A finding needs a location, evidence, a failure scenario, and a fix
<!-- doctrine: severity=ORANGE tier=micro principles=P7 -->

**Rule.** Report each finding with the rule ID, file and line, the exact code that shows it, a concrete input or state that produces a wrong outcome, and a proposed fix.
**Why.** "This looks fragile" cannot be verified or prioritized. A scenario can.
**How.** Format: `RULE-ID · severity · file:line · evidence · scenario · fix`. No style remarks.
**Check.** Does every finding include all five parts?

### R-3 · Verify a finding before acting on it
<!-- doctrine: severity=ORANGE tier=compact principles=P11 -->

**Rule.** Before a finding is fixed or reported as real, try to refute it by reading the code paths, reproduce it if possible, and judge its impact. Drop findings that do not survive.
**Why.** Plausible findings are cheap to produce and expensive to act on. Verification is what makes a review trustworthy.
**How.** Three questions: can I refute it, can I reproduce it, what actually happens to a user. Majority decides.
**Check.** Is each acted-on finding marked as verified, with how?

### R-4 · Re-audit every fix independently
<!-- doctrine: severity=YELLOW tier=compact principles=P11 -->

**Rule.** After the fix round, someone other than the fixer checks each finding against the new diff, re-runs the checks, and looks for problems the fixes introduced.
**Why.** Fixes are changes and have their own defects; the fixer is the worst-placed person to see them.
**How.** Item-by-item table: finding, resolved or not, evidence.
**Check.** Was each finding re-checked against the final diff by someone who did not write the fix?

### R-5 · Classify by severity and keep an append-only debt ledger
<!-- doctrine: severity=YELLOW tier=compact principles=P7 -->

**Rule.** Findings are RED, ORANGE or YELLOW. Anything not fixed in the change is recorded in the project's debt ledger with its rule ID, location, reason and disposition. Entries are marked resolved, never deleted.
**Why.** Deferred work that is not written down is not deferred, it is forgotten. An append-only ledger also records why a shortcut was taken.
**How.** One file per repository; entry: ID, severity, date, change, files, what, why, disposition, status.
**Check.** Is every unfixed finding in the ledger with a rule ID and a disposition?

### R-6 · Exercise the change in the running product, including flag states
<!-- doctrine: severity=ORANGE tier=compact principles=P11,P12 -->

**Rule.** Before merge the change is driven through the real interface against a real backend: the main journey, the failure the change addresses, the auth edge cases, and every feature-flag state it touches.
**Why.** Unit tests prove the parts. Only the running product shows whether the parts were connected.
**How.** Local stack; watch the network log and console; record each check and result.
**Check.** Is there a recorded run of the change in the product for each flag state?

### R-7 · Merge on green checks, clean review, and passing QA; else a human decides
<!-- doctrine: severity=ORANGE tier=compact principles=P12 -->

**Rule.** A change merges automatically only when checks are green, the review has no open findings and QA passed. Otherwise the decision belongs to a person.
**Why.** An agent that merges past its own findings has removed the only control on its work.
**How.** State the three results in the change; stop and ask when any is not clean.
**Check.** Are all three gates green, or has a person explicitly accepted the remaining findings?