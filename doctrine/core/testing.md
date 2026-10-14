# Testing rules

Tests are how a pattern's benefit is collected. A layer extracted for testability
and left untested is cost with no return (`P6`).

## Testing

### T-1 · Test at the boundary each layer exposes
<!-- doctrine: severity=ORANGE tier=micro principles=P11 -->

**Rule.** Server: through the HTTP API against a real database. Client manager: by emitting events against fake services. Client service: against a fake transport and in-memory storage. Pure functions: directly.
**Why.** Boundary tests survive refactors inside the layer and fail when behaviour changes. Tests of private internals do the opposite.
**How.** Server tests use the framework's API client and assert status, body and database state. Manager tests construct the plain class (`FE-MGR-1`).
**Check.** Does each new behaviour have a test at its layer's public boundary?

### T-2 · Prove every fix red before green
<!-- doctrine: severity=ORANGE tier=micro principles=P11 -->

**Rule.** A regression test is run against the unfixed code and seen to fail for the right reason before the fix is applied.
**Why.** A test that passes with and without the fix is decoration. This is the only cheap evidence that a test can detect the defect it is named for.
**How.** Write the test, run it, read the failure, then fix. Say in the change description that it was observed failing.
**Check.** Does the change state that each new regression test failed before the fix?

### T-3 · Failure paths are first-class test cases
<!-- doctrine: severity=ORANGE tier=compact principles=P11,P5 -->

**Rule.** Every unit of work has tests for its failures: rollback after a late error, the constraint race, the expired session, the upstream outage, the invalid input message.
**Why.** The happy path is exercised by every demo. Failure paths run for the first time in production unless a test runs them.
**How.** Rollback: patch a late collaborator to raise, assert nothing persisted. Race: insert the competing row between check and create. Client: 401 then refresh; 5xx during refresh.
**Check.** For each new write path, is there a rollback test and, where a constraint exists, a conflict test?

### T-4 · Fakes fail loudly
<!-- doctrine: severity=YELLOW tier=compact principles=P11 -->

**Rule.** A fake returns queued results and throws when called more times than expected or with a signature the real object would reject.
**Why.** A permissive fake accepts a renamed argument or an extra call and the test stays green while production breaks.
**How.** Result queues that throw when empty; auto-specced mocks bound to the real class signature.
**Check.** Would the test fail if the code called the collaborator with a wrong argument or one extra time?

### T-5 · A test asserts exactly what its name claims
<!-- doctrine: severity=YELLOW tier=compact principles=P7 -->

**Rule.** Each claim in a test's name is seeded and asserted in its body.
**Why.** A test named "clears both tokens" that seeds and checks one of them passes when the other is leaked.
**How.** Read the name, then find the assertion for each noun in it.
**Check.** Does each test assert every outcome its name states?

### T-6 · Tests are deterministic, order-independent, and offline
<!-- doctrine: severity=ORANGE tier=compact principles=P11 -->

**Rule.** Tests make no network calls, do not depend on execution order, and control time and randomness.
**Why.** A suite that fails one run in twenty is ignored within a month.
**How.** Run the suite shuffled at least once before merging; fake the transport; inject clocks.
**Check.** Does the suite pass in shuffled order with the network disabled?

### T-7 · Run the same command locally and in CI, and know what it selects
<!-- doctrine: severity=ORANGE tier=compact principles=P7 -->

**Rule.** CI runs the documented local test command. Authors know which database, settings profile and environment that command actually uses on their machine.
**Why.** A configuration library that silently falls back to a local settings file meant "the CI command" ran against a different database engine locally than in CI, so a claim of parity was false.
**How.** One make or script target. To reproduce CI locally, set the selecting variables explicitly rather than unsetting them.
**Check.** Is the CI test step the same command the README documents, and is the engine it selects stated?

### T-8 · Exercise transactions and constraints on the production database engine
<!-- doctrine: severity=ORANGE tier=compact principles=P11 -->

**Rule.** Tests that depend on transaction or constraint behaviour run on the same engine as production at least once before merge.
**Why.** Engines differ in how a failed statement affects an open transaction. A recovery path that works on a lightweight engine can fail on the real one.
**How.** Keep the fast engine for the default run if needed; run the transactional tests on the production engine locally or in a dedicated job.
**Check.** Were the transaction and constraint tests run on the production engine?

### T-9 · A pattern justified by testability must have tests
<!-- doctrine: severity=ORANGE tier=compact principles=P6 -->

**Rule.** If a layer exists so that logic can be tested (a manager, a pure derivation, a service behind an interface), the change that introduces it includes its tests and a runner that CI executes.
**Why.** Extracting logic costs indirection. Without tests the cost is paid and nothing is bought.
**How.** A unit-test runner is part of the project from the first manager; it runs in CI and in the deploy gate (`D-1`, `D-3`).
**Check.** Does every manager, derivation and service introduced have tests that CI runs?

### T-10 · Keep end-to-end tests few, on stable hooks, with stated prerequisites
<!-- doctrine: severity=YELLOW tier=compact principles=P11 -->

**Rule.** End-to-end tests cover a handful of critical journeys, select on agreed hooks (`FE-UI-4`), and document what they need to run.
**Why.** They are slow and environment-dependent; used for everything they become the suite nobody runs.
**How.** State prerequisites (live API, seeded user, flag values) at the top of the spec and in the README.
**Check.** Are the prerequisites for each end-to-end test written down, including feature-flag values?

### T-11 · Contract-test configuration: code, infrastructure, and docs must agree
<!-- doctrine: severity=YELLOW tier=compact principles=P7 -->

**Rule.** Where the same fact is declared in several places (settings, infrastructure manifest, documentation), a test reads all of them and fails on disagreement.
**Why.** Documentation and manifests are the first things to drift, and they drift silently.
**How.** A test that parses the settings module, the manifest and the documented table and compares the sets.
**Check.** Is each multiply-declared fact covered by a test that compares its sources?