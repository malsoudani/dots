# Principles

Two ideas run through everything in this package.

The first is that the same shape repeats on the server and on the client: a thin
layer that speaks the protocol, a layer that owns the decisions and normalizes
failure, and explicit typed shapes at every boundary. Learn the shape once and you
can read either side.

The second is that a pattern is a purchase. Every pattern costs ceremony — files,
indirection, typing — and buys a specific benefit: validation, exhaustiveness,
testability, a single owner for a decision. A pattern whose benefit you are not
collecting is pure cost.

Each principle names the trade it makes and ends with the rules that implement it.

### P1 · Decisions live in one layer
<!-- doctrine: tier=micro -->

**Principle.** Transport translates and the layer that owns decisions decides: services on the server, managers on the client. A rule lives in exactly one file.
**Why.** Two places that decide the same thing drift apart, and only one of them gets tested. When a handler or a component branches on a business condition, the rule now lives twice.
**In practice.** `BE-STRUCT-1`, `BE-STRUCT-2`, `BE-DOM-5`, `BE-SVC-1`, `BE-SVC-3`, `BE-API-1`, `FE-STRUCT-1`, `FE-STRUCT-2`, `FE-STATE-8`, `FE-STATE-9`, `FE-MGR-2`, `FE-MGR-5`, `FE-UI-1`, `FE-UI-2`, `FE-UI-3`, `CT-4`.

### P2 · Parse at the boundary, trust inside
<!-- doctrine: tier=micro -->

**Principle.** Everything that crosses a boundary — a request in, a response out, a stored row, an environment value, a third-party reply — is parsed once into an explicit typed shape at the edge. Inside the boundary, code trusts its types.
**Why.** A boundary parsed in two places pays twice. Half a boundary — a typed layer used only for output — still lets raw, unvalidated input reach the decisions. Be strict on the way in and lenient on the way out.
**In practice.** `BE-DOM-1`, `BE-DOM-2`, `BE-DOM-3`, `BE-DOM-4`, `BE-SVC-4`, `BE-API-8`, `FE-SVC-7`, `CT-3`, `CT-6`.

### P3 · Expected failures are values, mapped once
<!-- doctrine: tier=micro -->

**Principle.** An invalid input, a missing record and an expired session are part of the program, not exceptions to it. Each boundary has exactly one place that turns failure into its contract.
**Why.** Expected failures follow a value path; unexpected failures stay exceptions and fail loudly. When the two are mixed, a control-flow outcome is reported as a crash and every caller invents its own mapping. Never leak internals in the message.
**In practice.** `BE-SVC-5`, `BE-API-2`, `BE-API-3`, `BE-API-9`, `BE-EXT-2`, `FE-SVC-1`, `FE-SVC-2`, `FE-SVC-3`, `CT-1`, `CT-2`.

### P4 · State is explicit, closed, and exhaustive
<!-- doctrine: tier=micro -->

**Principle.** Model what can be true as a closed set of named shapes with a discriminator. The compiler or a test proves every case is handled, and an unknown case is an error rather than a silent no-op.
**Why.** Orthogonal facts get separate machines, because one union holding two concerns discards the other each time one changes. If you need a hidden variable to remember what the visible state forgot, the state is modelled wrong.
**In practice.** `FE-STATE-1`, `FE-STATE-2`, `FE-STATE-3`, `FE-STATE-4`, `FE-STATE-5`, `FE-STATE-7`, `FE-MGR-3`, `FE-SVC-8`, `CT-4`.

### P5 · A unit of work is all-or-nothing
<!-- doctrine: tier=micro -->

**Principle.** A user-visible action either fully happens or does not happen. On the server that is one transaction per service method; on the client a submission owns the flow until it settles.
**Why.** Partial success is the most expensive kind of failure, because nobody is told about it. A failure between two writes leaves rows nothing cleans up; a late result that half-applies leaves the screen disagreeing with the server.
**In practice.** `BE-SVC-6`, `BE-TXN-1`, `BE-TXN-2`, `BE-TXN-3`, `BE-TXN-4`, `BE-DB-3`, `FE-STATE-6`, `FE-MGR-3`, `FE-SVC-5`, `T-3`, `D-6`.

### P6 · Pay for ceremony only where you collect
<!-- doctrine: tier=micro -->

**Principle.** Every pattern has a price — files, indirection, typing — and a payoff: validation, exhaustiveness, testability. If you are not collecting the payoff, either start collecting it or delete the ceremony.
**Why.** Ceremony also shapes behaviour: when the right way costs seven files and the shortcut costs one line, logic leaks into the shortcut. Keep the right thing cheap, and delete the pattern that returns nothing.
**In practice.** `BE-STRUCT-4`, `FE-MGR-1`, `T-9`, `A-6`.

### P7 · Machines enforce, prose explains
<!-- doctrine: tier=micro -->

**Principle.** A rule that lives only in a document will be broken by the next tired person or model. Back it with a type, a test, a lint or a CI gate; where that is impossible, a checklist question.
**Why.** Documentation states intent and must match the code: when they disagree, one of them is a bug and is fixed in the same change.
**In practice.** `BE-STRUCT-5`, `BE-DB-1`, `BE-CFG-2`, `BE-CFG-3`, `FE-STATE-3`, `FE-UI-4`, `CT-7`, `T-5`, `T-7`, `T-11`, `D-1`, `D-13`, `R-2`, `R-5`, `A-5`.

### P8 · Build what is used, delete what is not
<!-- doctrine: tier=micro -->

**Principle.** Code with no caller and no test is a guess about the future that every reader must now evaluate. Build what is used and delete what is not.
**Why.** Unused code dilutes the signal about what is real. Extract shared code after the second real use, and name things for what they are — a folder called common that holds product concepts misleads everyone who opens it.
**In practice.** `BE-STRUCT-1`, `BE-STRUCT-3`, `BE-STRUCT-4`, `FE-STRUCT-1`, `FE-STRUCT-3`.

### P9 · One way to do each thing
<!-- doctrine: tier=micro -->

**Principle.** One HTTP client, one error convention, one source of storage keys, one place that clears tokens, one refresh path. There is one way to do each thing.
**Why.** Two mechanisms for the same job start identical and drift apart in exactly the edge cases — what happens on a 503 during a token refresh. When you find a second way, converge it before adding a third.
**In practice.** `BE-DOM-4`, `BE-SVC-3`, `BE-SVC-7`, `BE-API-2`, `BE-CFG-1`, `FE-SVC-4`, `FE-SVC-5`, `FE-SVC-6`, `FE-UI-5`, `CT-1`, `CT-5`.

### P10 · Wire dependencies at the edge
<!-- doctrine: tier=compact -->

**Principle.** A unit receives its collaborators; it does not reach for them. Servers pass collaborators through constructors and wire production defaults in one factory; clients construct services once at the route and inject them.
**Why.** Environment, feature flags, storage and the clock are read at the composition root and passed inward as values. This is what makes a unit testable without the framework.
**In practice.** `BE-STRUCT-2`, `BE-DOM-5`, `BE-SVC-2`, `BE-EXT-2`, `BE-EXT-3`, `FE-STRUCT-2`, `FE-STRUCT-4`, `FE-MGR-1`, `FE-MGR-4`, `FE-SVC-6`.

### P11 · Tests prove behavior at boundaries, including failure
<!-- doctrine: tier=micro -->

**Principle.** Test where a layer meets its caller: the HTTP API against a real database, the manager against fake services, the service against a fake transport. The cases that matter most are the failures.
**Why.** Rollback, race, expired session and upstream outage run for the first time in production unless a test runs them. A test that has never been seen to fail proves nothing; make it fail first.
**In practice.** `BE-CFG-4`, `FE-STATE-9`, `FE-MGR-1`, `FE-UI-3`, `T-1`, `T-2`, `T-3`, `T-4`, `T-6`, `T-8`, `T-10`, `R-1`, `R-3`, `R-4`, `R-6`.

### P12 · Ship in small reversible steps and verify at the edge
<!-- doctrine: tier=micro -->

**Principle.** Automation guards the main branch and the deploy. Every irreversible step has a safety net that is asserted before the step runs.
**Why.** A green pipeline is a claim; the new behaviour observed at the public edge is the proof. Rollback is a routine redeploy of a known-good revision, not an improvisation.
**In practice.** `BE-API-10`, `D-1`, `D-3`, `D-4`, `D-5`, `D-6`, `D-7`, `D-8`, `D-9`, `D-10`, `D-11`, `D-12`, `R-6`, `R-7`, `A-4`.

### P13 · Secure by construction
<!-- doctrine: tier=micro -->

**Principle.** Secrets never enter a repository or a client bundle. Third-party credentials stay on the server behind a proxy that builds the upstream request from an allowlist, every lookup is scoped to the caller, and everything the client controls is capped.
**Why.** These are structural properties, not review-time hopes. Error bodies never carry upstream or configuration detail, because a message that is convenient in a log is a disclosure in a response.
**In practice.** `BE-DOM-2`, `BE-API-4`, `BE-API-5`, `BE-API-6`, `BE-API-7`, `BE-EXT-1`, `BE-DB-2`, `BE-CFG-2`, `BE-CFG-3`, `BE-CFG-4`, `FE-SVC-3`, `FE-SVC-9`, `CT-8`, `D-2`.

### P14 · The host project wins
<!-- doctrine: tier=micro -->

**Principle.** Doctrine serves the project, not the reverse. Precedence: the user's explicit instruction, then the project's own instructions and conventions, then Doctrine, then the model's defaults.
**Why.** In a project built differently, apply the principle in the local idiom; never plant a competing pattern in one corner, and never refactor what you were not asked to touch. Surface conflicts in one line.
**In practice.** `A-1`, `A-2`, `A-3`, `A-4`.