# Review rules

Review looks for defects the author could not see, and records what it found.

## Review

### R-1 · Review every change through the same fixed lenses
<!-- doctrine: severity=YELLOW tier=compact principles=P1 -->

**Rule.** Apply the same ordered list of lenses to every change.

**Why.** A reviewer without a list reviews what they happen to notice.

**How.** Walk structure, correctness, contracts, tests, security and delivery in that order.

**Check.** Does the review name each lens it applied?

### R-2 · Report findings with evidence and a failure scenario
<!-- doctrine: severity=ORANGE tier=micro principles=P3 -->

**Rule.** A finding names the rule ID, the file and line, the evidence and a concrete failure.

**Why.** A finding without a scenario cannot be verified or ranked.

**How.** Write: rule, location, evidence, scenario, fix.

**Check.** Does every finding carry a rule ID, a location and a failure scenario?
