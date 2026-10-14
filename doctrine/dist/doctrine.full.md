# Doctrine full v0.1.0

Version 0.1.0. 14 principles, 118 rules. Generated from `core/` and `howto/`; edit those, never this text.

## Contents

1. Doctrine — operating instructions (`core/operating.md`)
2. Principles (`core/principles.md`)
3. Backend rules (`core/backend.md`)
4. Frontend rules (`core/frontend.md`)
5. Contract rules (`core/contracts.md`)
6. Testing rules (`core/testing.md`)
7. Delivery rules (`core/delivery.md`)
8. Review rules (`core/review.md`)
9. Adoption rules (`core/adoption.md`)
10. Checklists (`core/checklists.md`)
11. Bring Doctrine into a project (`howto/adopt-in-a-project.md`)
12. Build a backend slice end to end (`howto/backend-slice.md`)
13. Build a client experience end to end (`howto/frontend-experience.md`)
14. Review a change against Doctrine (`howto/review-a-change.md`)
15. Ship a change from branch to verified deploy (`howto/ship-a-change.md`)

---

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

---

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

---

# Backend rules

A backend is a set of vertical slices. Each slice has a thin transport that parses
and responds, a service that owns the rules and the unit of work, and typed domain
values at both edges.

## Structure

### BE-STRUCT-1 · Organize the backend as vertical slices, one directory per capability
<!-- doctrine: severity=ORANGE tier=compact principles=P1,P8 -->

**Rule.** Each capability lives in one directory holding its domains, models, service, transport (handlers and routes), migrations, tests and a short README.
**Why.** A change to one capability touches one directory. Layer-first layouts (all models here, all views there) scatter one feature across the tree and hide which code belongs together.
**How.** `invitations/{domains.py,models.py,service.py,views.py,urls.py,tests.py,README.md,migrations/}`. Register the slice once (installed apps, root URL include). Build domains first, then model, then service, then transport.
**Check.** Does every new capability live in its own slice directory with domains, service, transport and tests?

### BE-STRUCT-2 · Dependencies point inward: transport to service to persistence
<!-- doctrine: severity=ORANGE tier=micro principles=P1,P10 -->

**Rule.** Transport imports services and domains. Services import models and other services. Domain modules import no models and no framework persistence at runtime. Nothing imports transport.
**Why.** The direction is what lets you test a service without HTTP and reuse a domain anywhere. An import placed inside a function body to dodge a circular import is the symptom that the direction is already violated.
**How.** Type-only imports go behind `TYPE_CHECKING`. If a domain needs a model to build itself, the service builds the domain instead. Treat a function-local import as a defect to remove, not a technique.
**Anti-pattern.** a `domains.py` that does `from .models import User` at module level, or a domain classmethod that runs a query.
**Check.** Do domain modules import zero model or ORM symbols at runtime, and does no module import from a transport module?

### BE-STRUCT-3 · Name shared code and product code honestly
<!-- doctrine: severity=YELLOW tier=compact principles=P8 -->

**Rule.** A directory named for shared infrastructure holds only code with no product meaning. Product concepts live under a product-named package.
**Why.** Readers trust names. A "common" package full of product concepts tells every reader the wrong thing about what can be reused and what a change will affect.
**How.** Shared: ids, base model, exceptions, request parsing, health. Product: every slice that names a business noun.
**Check.** Is every module under a shared/common package free of product-specific nouns and rules?

### BE-STRUCT-4 · No speculative modules: every slice has a caller and a test
<!-- doctrine: severity=ORANGE tier=compact principles=P6,P8 -->

**Rule.** A module is merged only when an endpoint or another service calls it and a test exercises it. Delete modules that have neither.
**Why.** Unreferenced code is a guess about the future that every reader must still evaluate. In one codebase a third of the backend had no caller and no test, and it hid which parts were real.
**How.** Before adding a slice, name its first caller. When you find a module with zero inbound references and no tests, delete it in its own change. Sketches belong in a design note, not in the source tree.
**Check.** Does every new module have at least one caller outside itself and at least one test?

### BE-STRUCT-5 · Every slice documents its service API in a short README
<!-- doctrine: severity=YELLOW tier=compact principles=P7 -->

**Rule.** Each slice has a README listing its models, domains, service methods (inputs, return, errors) and endpoints, updated in the same change as the code.
**Why.** The README is the map the next author (human or model) reads before the code. A stale map is worse than none, so it is reviewed like code.
**How.** One table for service methods, one for endpoints, a list of error types. State contract facts the code cannot say out loud (which writes are atomic, what is idempotent).
**Check.** If a service method or endpoint changed, did the slice README change in the same diff?

## Domains

### BE-DOM-1 · Parse every request into a request domain at the transport boundary
<!-- doctrine: severity=RED tier=micro principles=P2 -->

**Rule.** Every handler turns the request body and query parameters into a typed request domain with one call before any service is invoked. Handlers never pull fields out of the raw request by hand.
**Why.** A typed layer used only for responses pays for two models of every concept and still lets unvalidated input through. Parsing once at the edge is where the typed layer earns its cost: the service can trust what it receives.
**How.** One `parse_request(RequestClass, data)` helper validates and converts every validation failure into the API error contract (`BE-API-2`). One request class per endpoint, kept next to the slice's other domains. Query strings go through the same helper.
**Anti-pattern.** `first_name = request.data.get("first_name")` followed by `if not first_name: raise ...` in a handler.
**Check.** Does every handler obtain all of its inputs from a single parsed request domain?

### BE-DOM-2 · Request domains are strict about types and lenient about extras
<!-- doctrine: severity=ORANGE tier=compact principles=P2,P13 -->

**Rule.** Request domains ignore unknown fields, strip surrounding whitespace, and constrain every field: enums for vocabularies, minimum lengths, timezone-aware timestamps, typed identifiers, size caps.
**Why.** Ignoring extras lets clients evolve without breaking; strict types stop bad data at the door. Trimming before the minimum-length check is what rejects a whitespace-only name.
**How.** A shared `RequestDomain` base sets extra=ignore and strip-whitespace. Use the same identifier type the services use. Reject offset-less timestamps (`BE-API-8`). Cap free-form payloads (`BE-API-7`).
**Check.** Does each request field have the narrowest type that fits, and are unknown fields ignored rather than rejected?

### BE-DOM-3 · Validate strictly on input, serialize leniently on output
<!-- doctrine: severity=ORANGE tier=compact principles=P2 -->

**Rule.** Response domains map stored data out without re-validating it against input rules.
**Why.** Stored rows outlive the rules that admitted them. If the read path re-applies today's input validation, one legacy row turns a read endpoint into a 500. A stored address with a reserved domain did exactly that to a session endpoint.
**How.** Use strict types (validated email, enum) on request domains; use plain types on response domains, or enums only where the read path first normalizes unknown values (`CT-6`).
**Anti-pattern.** a response domain field typed as a validated email built straight from a database column.
**Check.** Can every row already in the database be serialized by the response domain without raising?

### BE-DOM-4 · Define each vocabulary once as an enum and branch on its members
<!-- doctrine: severity=YELLOW tier=compact principles=P9 -->

**Rule.** A fixed set of values (status, role, action) is one enum, used by the request domain, the service and the model default. Services compare enum members, never string literals.
**Why.** When the request layer accepts a value the service's literal comparison does not know, the request validates and then fails with a second, differently worded error.
**How.** One string-valued enum per vocabulary in the slice's domain module. The service converts once (`Role(value)`) and branches on members.
**Anti-pattern.** `if action == "skip":` in a service while a request enum also lists the actions.
**Check.** Is every fixed vocabulary declared once and compared by member everywhere?

### BE-DOM-5 · Domain objects are plain values: no queries, no I/O
<!-- doctrine: severity=ORANGE tier=compact principles=P1,P10 -->

**Rule.** A domain class holds data and pure derivations. It performs no database access, no token minting, no network call.
**Why.** A value that secretly queries cannot be built in a test, cannot be reused with another data source, and hides work from the reader of the service.
**How.** The service performs the lookup or mints the token and constructs the domain from the results. Mapping from a model is an explicit `from_model` that only copies fields.
**Check.** Can every domain class be constructed in a unit test with no database and no network?

## Services

### BE-SVC-1 · Business rules live in services; transport never touches persistence
<!-- doctrine: severity=RED tier=micro principles=P1 -->

**Rule.** Every business decision and every database access for a slice lives in its service class. Handlers call exactly one service method.
**Why.** One owner per rule (P1). Logic in a handler cannot be reused by a job, a command or another service, and is tested only through HTTP.
**How.** One service class per slice with intention-revealing methods (`create_invitation`, `revoke_invitation`). Handlers stay under roughly fifteen lines.
**Check.** Is the handler free of ORM calls and of branching on business conditions?

### BE-SVC-2 · Inject collaborators through the constructor; wire defaults in a factory
<!-- doctrine: severity=ORANGE tier=compact principles=P10 -->

**Rule.** A service receives the other services and adapters it needs as constructor arguments. A `factory()` classmethod builds the production wiring. Callers use the factory; tests pass fakes.
**Why.** Explicit dependencies are visible in one signature and replaceable in a test without patching module globals.
**How.** `InvitationService(team_service, notifier)`; `InvitationService.factory()` returns it wired with `TeamService.factory()` and the real notifier.
**Check.** Does the service obtain every collaborator from its constructor rather than importing and instantiating it inline?

### BE-SVC-3 · Cross-slice access goes through the other slice's service
<!-- doctrine: severity=ORANGE tier=compact principles=P1,P9 -->

**Rule.** A service never queries another slice's models. It calls that slice's service.
**Why.** The owning slice's rules (validation, scoping, defaults) live in its service. Reaching around it duplicates or skips them, and couples two slices at the table level.
**How.** An orchestrating service holds the other services as collaborators (`BE-SVC-2`). If the method you need is missing, add it to the owning service.
**Anti-pattern.** an onboarding-style service that calls `OtherModel.objects.create(...)` while also holding `OtherService`.
**Check.** Does each service touch only its own slice's models?

### BE-SVC-4 · Services take and return domain values, never ORM objects
<!-- doctrine: severity=ORANGE tier=compact principles=P2 -->

**Rule.** Service methods accept primitives or domain values and return domain values. Models and query sets do not cross the service boundary.
**Why.** A returned model invites the caller to trigger lazy queries, mutate and save outside the unit of work.
**How.** Convert with `Domain.from_model(row)` at the end of the method. Collections return a domain wrapping a list.
**Check.** Do service signatures mention only primitives and domain types?

### BE-SVC-5 · Raise typed business errors from one exception hierarchy
<!-- doctrine: severity=ORANGE tier=compact principles=P3 -->

**Rule.** Expected failures are subclasses of one base exception that carries a message and a status meaning. Each slice defines its own (`InvitationNotFound`, `InvalidInvitationState`).
**Why.** One hierarchy lets one handler map every business failure to the error contract. A second convention (some services raising framework HTTP errors directly) makes the service unusable outside HTTP.
**How.** Base class in the shared package with `status_code` and `message`. Services never raise transport-level exceptions.
**Check.** Does every expected failure raised by a service derive from the shared business-error base?

### BE-SVC-6 · Make retried writes idempotent
<!-- doctrine: severity=ORANGE tier=compact principles=P5 -->

**Rule.** A write the client may send twice (double click, retry after timeout, resubmitted step) produces the same result the second time, not a duplicate.
**Why.** Networks retry. Without idempotency every timeout becomes a duplicate row or a spurious conflict error.
**How.** Look up by the natural key before creating; back it with a uniqueness constraint (`BE-DB-3`) and handle the conflict (`BE-TXN-3`). Test: submit twice, assert one row and equal responses.
**Check.** Is there a test that performs the write twice and asserts no duplicate?

### BE-SVC-7 · Compute derived state in one pure helper shared by reads and writes
<!-- doctrine: severity=YELLOW tier=compact principles=P9 -->

**Rule.** Logic that derives state from stored fields (next step, effective status, legacy clean-up) is one pure function called by both the write path and the read path.
**Why.** Two copies of the derivation drift, and then the value the write stored is not the value the read reports.
**How.** A static, side-effect-free helper taking stored values and returning the derived ones; unit-test it directly.
**Check.** Is each derivation implemented exactly once?

## Transactions

### BE-TXN-1 · One service method is one transaction
<!-- doctrine: severity=RED tier=micro principles=P5 -->

**Rule.** Every service method that performs more than one write runs inside a single database transaction.
**Why.** Without it a failure after the second of five writes leaves rows that nothing will ever clean up. A step-submission method once created records and then rejected the request, leaving orphans behind every failed attempt.
**How.** Decorate the service method (Django: `@transaction.atomic`). Do not enable a global per-request transaction when any endpoint holds a long outbound call (`BE-TXN-2`). Prove it with a rollback test (`T-3`).
**Anti-pattern.** a multi-write method with no transaction because "each save is small".
**Check.** Does every multi-write service method run in one transaction, with a test that forces a late failure and asserts nothing persisted?

### BE-TXN-2 · Never hold a transaction open across an outbound network call
<!-- doctrine: severity=RED tier=micro principles=P5 -->

**Rule.** Perform remote calls before opening the transaction or after it commits. The transaction wraps local writes only.
**Why.** An open transaction pins a database connection for the full latency and timeout of someone else's service. An unauthenticated endpoint that does this lets a slow upstream exhaust the pool.
**How.** Call the provider, validate the reply, then `with transaction.atomic():` around the local writes. Never put the atomic decorator on a method whose body awaits a remote system.
**Check.** Is every remote call outside all transaction blocks?

### BE-TXN-3 · Recover from an integrity error only inside a savepoint
<!-- doctrine: severity=RED tier=compact principles=P5 -->

**Rule.** A statement that may violate a constraint and be recovered from runs in its own nested transaction (savepoint). The recovery query runs after the savepoint is released.
**Why.** Inside a transaction a failed statement poisons the whole transaction: the next query raises instead of running. Adding a transaction around a method that already caught a uniqueness error turned a graceful "return the existing row" into a 500, and the test suite on a different engine did not notice.
**How.** `try: with transaction.atomic(): create(...)` then `except IntegrityError: return fetch_existing(...)`. Comment why the savepoint exists. Test the race on the production engine (`T-8`).
**Check.** Is every caught integrity error raised from inside a nested atomic block?

### BE-TXN-4 · Run irreversible side effects after commit
<!-- doctrine: severity=ORANGE tier=compact principles=P5 -->

**Rule.** Emails, queue messages, webhooks and other effects that cannot roll back are scheduled to run only after the surrounding transaction commits.
**Why.** An effect fired inside a transaction that later rolls back tells the world about something that never happened.
**How.** Use the framework's on-commit hook (Django: `transaction.on_commit`). The test asserts the effect did not fire when the transaction rolled back.
**Check.** Are all non-database side effects registered to run on commit?

## Transport

### BE-API-1 · A handler authenticates, parses, calls one service method, and responds
<!-- doctrine: severity=ORANGE tier=compact principles=P1 -->

**Rule.** Handlers contain exactly four moves: declared authentication and permission, one request parse, one service call, one response mapping.
**Why.** Anything else in a handler is a decision in the wrong layer (P1) that only an HTTP test can reach.
**How.** `body = parse_request(...)`; `result = Service.factory().method(...)`; `return Response(result.to_dict())`. No conditionals except error translation, and prefer the global handler for that.
**Check.** Does the handler consist only of parse, one service call and the response?

### BE-API-2 · One error contract for the whole API, produced in one place
<!-- doctrine: severity=RED tier=micro principles=P3,P9 -->

**Rule.** Every non-2xx response has the same body shape, built by one exception handler. Validation failures are 400 in that shape, never 500.
**Why.** Clients write one parser. Any endpoint that returns a different error shape is a bug the client will surface as "unknown error".
**How.** `{"error": "<message>"}`. One handler maps the business-error base, the framework's errors and request-validation failures. Malformed bodies (a list where an object is expected) are also 400.
**Check.** Does every error path, including validation and malformed input, produce the single error shape with a 4xx status?

### BE-API-3 · Write error messages for the end user; clients show them verbatim
<!-- doctrine: severity=ORANGE tier=compact principles=P3 -->

**Rule.** The message in the error body is a short sentence a person can act on. Validator jargon never reaches it.
**Why.** Clients display the server's message as is. "first_name: String should have at least 1 character" is a leak of a library's vocabulary onto someone's screen.
**How.** Map validation error types to phrases: missing or empty -> "<field> is required"; bad enum -> "Unsupported <field>: <value>"; bad address -> "Enter a valid email address"; several -> joined with "; ".
**Check.** Would every error message make sense to a person who has never seen the code?

### BE-API-4 · Never echo upstream or configuration detail to callers; log it instead
<!-- doctrine: severity=RED tier=compact principles=P13 -->

**Rule.** Errors from providers and from missing configuration are mapped to fixed, safe messages. The original detail is logged server-side.
**Why.** "API key is required" tells an anonymous caller a secret is missing; a provider's raw error carries request IDs and internal URLs.
**How.** Provider failure -> 400 or 502 with a fixed sentence; not configured -> 503 "… is not configured." Log the cause with a logger named for the module. Do not catch the broad business-error base in public handlers.
**Check.** Can any response body contain text produced by a third party or by a configuration check?

### BE-API-5 · Deny by default: endpoints are authenticated unless they opt out
<!-- doctrine: severity=RED tier=compact principles=P13 -->

**Rule.** The framework default requires authentication. A public endpoint opts out explicitly through a dedicated base class.
**Why.** A forgotten decorator on a default-open framework is a data leak; on a default-closed one it is a 401 in the first test.
**How.** Global default permission "authenticated". `PublicAPIView` clears authentication and permission classes and is the only way to be public. Test one endpoint without credentials.
**Check.** Is every public endpoint public through the explicit opt-out base and nothing else?

### BE-API-6 · Scope every lookup to the caller; foreign and unknown IDs look the same
<!-- doctrine: severity=RED tier=micro principles=P13 -->

**Rule.** Any identifier supplied by a client is resolved within what the caller may access. An identifier that exists but belongs to someone else returns the same 404 and message as one that does not exist.
**Why.** Unscoped lookups let any signed-in user attach to, list or modify another tenant's data by guessing or harvesting IDs.
**How.** Filter by owner in the query (`team__memberships__user_id=actor_id`). Validate every ID in a list. Test with a second tenant's ID and assert 404 with nothing persisted.
**Check.** For every client-supplied ID, is there a test using another tenant's ID that gets 404?

### BE-API-7 · Cap everything the client controls
<!-- doctrine: severity=ORANGE tier=compact principles=P13 -->

**Rule.** Free-form payloads, lists, strings and selectable options (models, schemas, page sizes) have explicit maximums or allowlists, enforced at the request domain. Reject; do not truncate.
**Why.** An uncapped JSON field stored and echoed on every read is an unbounded per-user blob. An uncapped option list is a way to spend your money.
**How.** Field validators for size; allowlists in configuration for option sets; a test just over and just under each limit.
**Check.** Does every client-controlled size or option have a tested limit?

### BE-API-8 · Timestamps cross the boundary as ISO-8601 with an offset
<!-- doctrine: severity=YELLOW tier=compact principles=P2 -->

**Rule.** The API accepts and returns timezone-aware ISO-8601 timestamps. Offset-less input is rejected. Storage is UTC.
**Why.** A naive timestamp is interpreted by whoever touches it next; the response to a write and the next read then disagree by an offset.
**How.** Timezone-aware field types on request domains; the error message names the field.
**Check.** Is every timestamp field on a request domain timezone-aware?

### BE-API-9 · Reserve 401 for dead credentials
<!-- doctrine: severity=ORANGE tier=compact principles=P3 -->

**Rule.** 401 means only "your credentials are missing, invalid or expired". Validation and business failures never use 401.
**Why.** Clients treat 401 specially: refresh the token, then sign the user out. A 401 for anything else logs people out for a typo.
**How.** Validation -> 400; forbidden -> 403; unknown or foreign -> 404; conflict -> 409. See `CT-2`.
**Check.** Can any non-credential failure produce a 401?

### BE-API-10 · Liveness is shallow and dependency-free; readiness checks dependencies
<!-- doctrine: severity=YELLOW tier=compact principles=P12 -->

**Rule.** The liveness endpoint answers without touching the database or any dependency. A separate readiness check exercises them and feeds monitoring.
**Why.** A liveness check that queries the database restarts healthy processes during a database blip. A system with only the shallow check stayed green through a long database outage because nothing looked deeper.
**How.** Liveness: plain handler outside the API framework, zero queries (asserted in a test), exempt from HTTPS redirects. Readiness: one trivial query, alerting on failure.
**Check.** Does the liveness handler run zero queries, and does something else monitor the dependencies?

## Third parties

### BE-EXT-1 · Third-party credentials stay server-side behind an allowlisting proxy
<!-- doctrine: severity=RED tier=micro principles=P13 -->

**Rule.** A browser or app never holds a provider credential. The client calls your API; your API builds the provider request from an allowlist and forwards it.
**Why.** Anything shipped to a client is public. A proxy that forwards the client's body verbatim hands the caller your account with their parameters.
**How.** Build the upstream body from named fields only; allowlist models and schemas; force server-side limits (max tokens, no streaming); never follow redirects (the credential would be replayed); set a timeout; map every upstream outcome to a typed error; log the caller ID, not the content.
**Check.** Is the upstream request built field by field from an allowlist, with redirects disabled and a timeout?

### BE-EXT-2 · Wrap each provider SDK in one adapter with its own error types
<!-- doctrine: severity=ORANGE tier=compact principles=P3,P10 -->

**Rule.** One adapter class per provider is the only code that imports its SDK. It raises the adapter's own exception types and validates configuration in its factory.
**Why.** SDK exceptions and response shapes then never leak into services, and the provider can be faked or replaced by changing one file.
**How.** `Notifier`, `IdentityProviderClient`: thin methods, each catching the SDK's errors and raising `ProviderError` or `ProviderNotConfigured`.
**Check.** Is the provider SDK imported in exactly one module?

### BE-EXT-3 · Application code reads configuration from the environment only
<!-- doctrine: severity=YELLOW tier=compact principles=P10 -->

**Rule.** The application reads settings from environment variables. It never calls a cloud secret store at runtime; mapping the store to the environment is a deploy step.
**Why.** The same build then runs anywhere, and a secret-store outage is a deploy-time problem instead of a request-time one.
**How.** Settings read `env("NAME")`. The deploy layer renders the environment from the store.
**Check.** Does application code import any cloud SDK to read configuration?

## Persistence

### BE-DB-1 · Generate migrations from models; never hand-write or edit them
<!-- doctrine: severity=RED tier=compact principles=P7 -->

**Rule.** Schema changes are made in the model and the migration is generated by the framework. Generated files are not edited; if one is wrong, change the model and regenerate.
**Why.** A hand-edited migration no longer matches the model, and the next generated migration silently "fixes" it in production.
**How.** Generate, apply, then run the framework's "no pending migrations" check in CI (`D-1`).
**Check.** Does CI fail when models and migrations disagree, and is every migration file tool-generated?

### BE-DB-2 · Use opaque, non-sequential identifiers and audit timestamps
<!-- doctrine: severity=YELLOW tier=compact principles=P13 -->

**Rule.** Primary keys exposed to clients are random opaque strings. Every table has created and updated timestamps.
**Why.** Sequential IDs leak volume and invite enumeration; timestamps are what every incident investigation asks for first.
**How.** A shared abstract base model supplies the ID default and both timestamps.
**Check.** Do new tables inherit the shared base model?

### BE-DB-3 · Enforce uniqueness in the database and handle the conflict in code
<!-- doctrine: severity=ORANGE tier=compact principles=P5,P7 -->

**Rule.** Any "at most one" rule is a database constraint. The code that inserts handles the conflict (`BE-TXN-3`).
**Why.** A check-then-insert in application code is a race: two requests both pass the check. Only the database can decide.
**How.** Unique constraint on the natural key; create inside a savepoint; on conflict fetch and return the existing row (`BE-SVC-6`).
**Check.** Is every uniqueness rule backed by a constraint and a tested conflict path?

## Configuration

### BE-CFG-1 · Select the settings profile with one switch
<!-- doctrine: severity=YELLOW tier=compact principles=P9 -->

**Rule.** Shared settings live in a base module; local and production profiles extend it; one environment variable selects the profile; the package itself is not a valid target.
**Why.** One switch means there is one answer to "which configuration is this process running".
**How.** `settings/{base,local,production}.py`; entry points default to local.
**Check.** Is there exactly one mechanism that selects the profile?

### BE-CFG-2 · Production configuration validates itself and refuses to boot when unsafe
<!-- doctrine: severity=RED tier=compact principles=P7,P13 -->

**Rule.** The production profile checks its own values at import and raises on debug mode, weak or default secrets, wildcard hosts, non-HTTPS or loopback origins, or a non-production database. The local profile refuses to boot when the environment says production.
**Why.** A misconfigured production process should fail at start, loudly, not serve traffic insecurely. Failing closed converts a silent risk into a failed deploy.
**How.** A validation module raising one configuration error type; a `check-deploy` command that validates the production profile with throwaway values and runs in CI.
**Check.** Does booting production with an unsafe value fail, and does CI run the production configuration check?

### BE-CFG-3 · No secret in any repository or client; one store, one manifest, one test
<!-- doctrine: severity=RED tier=micro principles=P13,P7 -->

**Rule.** Secret values exist only in the secret store and the process environment. A manifest lists every secret path, the variable it feeds and its owner. A test fails when settings, the manifest and the documentation disagree.
**Why.** Secrets in a repository are permanent. A manifest nobody checks drifts until a deploy boots without a key.
**How.** Local `.env` is ignored by version control and never shipped. The contract test reads all three sources.
**Check.** Does a test fail if a setting is read that the manifest does not declare?

### BE-CFG-4 · Trust a proxy header only after verifying it arrives at the origin
<!-- doctrine: severity=ORANGE tier=compact principles=P13,P11 -->

**Rule.** Before configuring the application to trust a forwarded header, capture real traffic at the origin and confirm the header is present and cannot be supplied by a client. Trust it only while the origin is unreachable except through the proxy.
**Why.** Proxies rewrite and drop headers in ways their documentation does not list. A forwarded-protocol header that was silently dropped produced an infinite redirect loop that only a packet capture explained.
**How.** Capture at the origin, send a spoofed header through the edge and confirm it is replaced, then restrict origin ingress to the proxy.
**Check.** Is each trusted header backed by evidence captured at the origin?

---

# Frontend rules

A client is a set of experiences. Each has presentation that renders state and
emits events, a manager that turns events into states, services that talk to the
outside world and return result values, and pure models. The flow is always:
presentation emits event -> manager handles event -> service returns a result value
-> manager translates it into state -> presentation renders state.

## Structure

### FE-STRUCT-1 · Organize the client by experience; each owns its flow end to end
<!-- doctrine: severity=ORANGE tier=compact principles=P1,P8 -->

**Rule.** Code is grouped by the user outcome it serves. An experience directory holds its components, manager, services, models, pages and routes.
**Why.** A feature is changed as a unit, so it should be found as a unit. Type-first trees (all components here, all hooks there) hide ownership.
**How.** `src/experiences/<feature>/{components,manager,services,models,pages,routes}`. Inside `manager/`: `<Feature>Event`, `<Feature>State`, `<Feature>Manager`, the framework binding, pure derivations.
**Check.** Does each feature's code live under one experience directory with the six sub-folders it needs?

### FE-STRUCT-2 · Dependencies point inward: presentation, manager, services, models
<!-- doctrine: severity=ORANGE tier=micro principles=P1,P10 -->

**Rule.** Presentation imports the manager's events and states. The manager imports service interfaces and models. Services import shared transport and models. Models import nothing but other models. Nothing imports presentation.
**Why.** The direction is what keeps the manager testable without the UI framework and the models reusable everywhere.
**How.** Models never import storage or services. Presentation never imports a service. Shared transport, storage keys and failure types live in `src/common/`.
**Anti-pattern.** a model type defined inside a storage module in `common/`, so the domain depends on storage.
**Check.** Does any model import a service or storage module, or any component import a service?

### FE-STRUCT-3 · Share code only after a second real use
<!-- doctrine: severity=YELLOW tier=compact principles=P8 -->

**Rule.** Code moves to the shared area when a second experience needs it, not in anticipation.
**Why.** Premature sharing produces abstractions shaped by one caller that fit no other. The exception is infrastructure that is single by nature (`FE-SVC-4`, `FE-SVC-6`).
**How.** Start inside the experience. On the second use, move it and delete the copy in the same change.
**Check.** Does everything in the shared area have at least two callers or is it single-by-nature infrastructure?

### FE-STRUCT-4 · Routes are composition roots: build services once, inject, decide nothing
<!-- doctrine: severity=ORANGE tier=compact principles=P10 -->

**Rule.** A route constructs the experience's services once per mount, reads environment, flags and stored values, passes them to the provider and renders the page. It contains no workflow logic.
**Why.** Constructing services on every render creates a new instance per render and breaks any per-instance guard. Logic in a route is logic nobody tests.
**How.** `useState(createRouteServices)`; the factory reads env and storage; the route renders `<Provider …><Page/></Provider>` and nothing else.
**Check.** Does the route construct each service exactly once per mount and contain no conditional workflow?

## Events and state

### FE-STATE-1 · Intents are explicit events in a closed, tagged union
<!-- doctrine: severity=ORANGE tier=micro principles=P4 -->

**Rule.** Every intent that can enter a manager is its own named type with a literal discriminator, and all of them form one exported union.
**Why.** A closed union is the manager's public API in one place, and it lets the compiler prove the dispatcher handles every case. Loose string actions with untyped payloads give neither.
**How.** `class SubmitRequested { readonly kind = "SubmitRequested" as const }`; `export type InvitationsEvent = A | B | C`.
**Anti-pattern.** `dispatch({ type: "submit", payload })`.
**Check.** Is every event a member of one tagged union with a literal `kind`?

### FE-STATE-2 · Renderable states are explicit, tagged, and shaped for the UI
<!-- doctrine: severity=ORANGE tier=micro principles=P4 -->

**Rule.** Every state the screen can be in is its own named type with a literal discriminator. A state models what the UI needs to render, not the event that caused it.
**Why.** With tagged states the UI narrows by `kind` and the compiler knows which fields exist. States named after events couple the screen to the history instead of the present.
**How.** `Idle | Loading | Loaded{…} | Submitting{…} | Failed{failure, …}`; presentation switches on `state.kind`.
**Check.** Does presentation select what to render by `state.kind` with no `instanceof` chains or optional-field probing?

### FE-STATE-3 · Dispatch exhaustively; an unknown event is an error
<!-- doctrine: severity=ORANGE tier=compact principles=P4,P7 -->

**Rule.** The manager dispatches with a switch over the discriminator whose default branch fails to compile when a case is missing and throws at runtime.
**Why.** An `if` chain silently ignores an event nobody wired. The exhaustive switch is how the typed events pay for themselves (P6).
**How.** `default: return assertNever(event)` where `assertNever(value: never): never` throws.
**Check.** Does adding a new event type without a case fail the type check?

### FE-STATE-4 · Give orthogonal concerns separate state machines
<!-- doctrine: severity=ORANGE tier=compact principles=P4 -->

**Rule.** Facts that vary independently (who is signed in; what the screen has loaded) are separate state unions, each with its own transitions.
**Why.** One union holding both means entering any state of one concern discards the other, and the manager grows hidden variables to remember what was lost.
**How.** `sessionState: SessionState` and `flowState: FlowState` side by side on the manager; presentation reads both.
**Anti-pattern.** one union containing `SignedOut | Authenticated | Loading | Loaded | Submitting`.
**Check.** Does any single state union mix two concerns that can change independently?

### FE-STATE-5 · Background work is sub-state of the loaded state, never a replacement
<!-- doctrine: severity=ORANGE tier=compact principles=P4 -->

**Rule.** A search, a lookup or a refresh that happens while a screen is loaded is a field on the loaded state with its own status. It never replaces the loaded state.
**Why.** Replacing `Loaded` with `Searching` throws away the loaded data; the manager then keeps a hidden copy to restore it, and the page rebuilds the data through a chain of type checks.
**How.** `Loaded { record, search: { query, status: "idle" | "searching" | "loaded", results } }` updated with a copying `with…` method.
**Anti-pattern.** a ref on the manager that "remembers the last loaded record".
**Check.** Does the manager hold any variable that duplicates data from a previous state?

### FE-STATE-6 · A submission owns the flow until it settles
<!-- doctrine: severity=RED tier=compact principles=P5 -->

**Rule.** While a submission is in flight, the state is `Submitting`. Requests that arrive during it are ignored, and results of earlier requests that land during it, success or failure, do not replace it.
**Why.** If a late search result replaces `Submitting` with `Loaded`, the submit button re-enables and the user sends the same write twice.
**How.** Guard at the top of every non-submit handler; in every result branch return the current state unchanged when it is `Submitting`. Test a search that fails mid-submit.
**Check.** Is there a test showing that a result arriving during a submission leaves the state `Submitting`?

### FE-STATE-7 · Never show data loaded for a different key
<!-- doctrine: severity=RED tier=compact principles=P4 -->

**Rule.** When the key of a request changes (another organization, another record), the loading state exposes no data until data for the new key arrives.
**Why.** Carrying the previous list under the new key renders one tenant's items as another's, selectable, until the response lands — or forever if it fails.
**How.** While loading, keep previous data only if the key is unchanged; otherwise an empty list. Test A-then-B.
**Check.** Is there a test that switches keys and asserts the loading state is empty?

### FE-STATE-8 · State carries data and intent; presentation owns the words
<!-- doctrine: severity=YELLOW tier=compact principles=P1 -->

**Rule.** States hold data and intents (which action continues the flow, which provider is redirecting). Titles, labels and toast sentences are produced by a presentation-side copy module.
**Why.** Copy inside manager state couples the manager to one screen's wording, and screens start making decisions by comparing label strings.
**How.** `continueIntent: "continue" | "schedule"` on state; `continueCopy(intent)` in presentation. Store identifiers, not labels.
**Anti-pattern.** `if (state.providerLabel === "Google")` in a page.
**Check.** Does any manager state contain a user-facing sentence, or any component branch on one?

### FE-STATE-9 · Derive view models with pure functions
<!-- doctrine: severity=ORANGE tier=compact principles=P1,P11 -->

**Rule.** Anything computed from state for display (step number, which buttons are enabled, what the tracker shows) is a pure function of states and inputs, with unit tests.
**Why.** Step arithmetic scattered through a page cannot be tested and is recomputed differently in two components.
**How.** `deriveStepper({ sessionState, flowState, forms, flags }) -> StepperState` in the manager folder; the manager exposes the result; presentation reads it.
**Check.** Is each derived display value computed in one tested pure function?

## Manager

### FE-MGR-1 · The manager is a plain class; the framework binding is a thin adapter
<!-- doctrine: severity=ORANGE tier=micro principles=P6,P10,P11 -->

**Rule.** The manager imports nothing from the UI framework. It takes services and an `onChange` listener in its constructor, exposes its states, and has one `emit(event)` method. A small hook or store adapter binds one instance to the framework.
**Why.** A manager written as a framework hook can only be tested by rendering. The reason to extract logic from components is to test it; a manager that needs the framework does not collect that benefit.
**How.** `new Manager({ services, onChange })`; the binding creates it once (`useState(() => new Manager(...))`) and mirrors snapshots into framework state.
**Check.** Can the manager be constructed and driven in a unit test with no UI framework import?

### FE-MGR-2 · The manager owns sequencing, branching, validation, and automatic actions
<!-- doctrine: severity=RED tier=micro principles=P1 -->

**Rule.** What happens next, whether a step is valid, when to retry, when to skip, and once-only guards are decided in the manager. Presentation only reports what the user did.
**Why.** One codebase had a manager that merely forwarded API calls while a five-hundred-line page decided step order, validity and submission mapping. The pattern's ceremony was paid and the testability was never collected.
**How.** Events like `ContinueRequested`, `BackRequested`; the manager validates the current step, picks the submission, and applies automatic actions (for example skipping a disabled step once).
**Anti-pattern.** a page-level effect that watches state and fires a submit.
**Check.** Is there any conditional about the workflow outside the manager and its pure helpers?

### FE-MGR-3 · Compute each transition from the state at the moment the result arrives
<!-- doctrine: severity=RED tier=compact principles=P4,P5 -->

**Rule.** After an `await`, the next state is computed from the manager's current state, not from a value captured before the call.
**Why.** Other events may have been handled while the request was in flight. A transition computed from a stale snapshot overwrites them.
**How.** `this.update(current => next(current, result))`. Never read `this.state` into a local before `await` and use it after.
**Check.** Does every post-await transition read the current state inside the update function?

### FE-MGR-4 · Resolve flags and environment at the composition root and pass them in
<!-- doctrine: severity=ORANGE tier=compact principles=P10 -->

**Rule.** Feature flags and environment values are parsed by a pure function at the route and passed to the manager as constructor inputs. The manager derives behavior from them. Presentation never reads the environment.
**Why.** A flag read inside a page puts a workflow decision in presentation and makes both flag states untestable.
**How.** `isFeatureEnabled(env)` in `models/`; route passes the boolean; pure derivation takes it as input; tests cover both values.
**Check.** Does any file outside routes and the flag model read the environment?

### FE-MGR-5 · Forms report snapshots; validity and submission mapping are pure functions
<!-- doctrine: severity=ORANGE tier=compact principles=P1 -->

**Rule.** A form component keeps its own input state and reports a snapshot through an event on change. Whether the snapshot is valid and what request it becomes are pure functions in the model layer, called by the manager.
**Why.** Input text is ephemeral UI state and belongs in the component; "is this submittable" and "what do we send" are rules and belong where they can be tested.
**How.** `FormChanged{snapshot}` event; `draftValid(snapshot)`, `submissionFromDraft(snapshot)` in `models/`; manager uses them on `SubmitRequested`.
**Check.** Are validity and request mapping pure functions with tests, not code in a component?

## Services

### FE-SVC-1 · Every service method returns a result value: failure left, success right
<!-- doctrine: severity=RED tier=micro principles=P3 -->

**Rule.** Service methods return a result type (`Either<Failure, T>`). Expected failures are returned on the left; services do not throw them.
**Why.** A thrown error is invisible in the type; a result value forces every caller to handle failure and lets the manager map both arms to states in one expression.
**How.** Services sit behind an interface; `try { … return right(x) } catch (e) { return left(toFailure(e)) }`; managers use `match(onLeft, onRight)`.
**Check.** Does every service method's return type include the failure arm, with no expected failure thrown?

### FE-SVC-2 · Normalize failures at the service boundary into typed codes
<!-- doctrine: severity=ORANGE tier=compact principles=P3 -->

**Rule.** Every failure leaving a service is one `AppFailure` with a stable `code`, a displayable `message`, and the original error kept on a non-rendered `cause`.
**Why.** Managers branch on codes ("session expired" versus "could not save"); branching on message text breaks the first time the wording changes.
**How.** Codes are constants per service; the session-expired code is shared.
**Check.** Does the manager branch on failure codes only, never on message text?

### FE-SVC-3 · Show users only messages your own API wrote
<!-- doctrine: severity=ORANGE tier=compact principles=P3,P13 -->

**Rule.** Only text from your API's error contract passes through to the screen. Any other error (network failure, parse error) is replaced by the service's fallback message.
**Why.** "Failed to fetch" and "Unexpected token <" are transport internals; shown to a user they are noise at best and information disclosure at worst.
**How.** The failure mapper passes through the message only when the error is the client's own HTTP error type.
**Check.** Can a browser or parser error string reach the UI?

### FE-SVC-4 · One HTTP client owns URLs, headers, error parsing, and auth
<!-- doctrine: severity=ORANGE tier=micro principles=P9 -->

**Rule.** One class builds URLs, sets headers, parses the API error contract into one HTTP error type, and applies authentication. Services call it; nothing else calls `fetch`.
**Why.** Two services each carrying their own copy of the request helper will differ in exactly the edge cases. Token handling duplicated in two places diverged on what a failed refresh means.
**How.** `ApiClient.requestJson` and `ApiClient.requestAuthenticatedJson`, constructed once at the route and shared by the experience's services. A successful response whose body is not the expected format is an error, not a crash.
**Check.** Is `fetch` (or the HTTP library) called from exactly one module?

### FE-SVC-5 · Refresh once on 401; clear tokens only when the session is provably dead
<!-- doctrine: severity=RED tier=micro principles=P5,P9 -->

**Rule.** On a 401 the client refreshes the access token once and retries once. Tokens are cleared only when there is no refresh token, the refresh is rejected as unauthorized, or the retry is 401 again. Any other failure is rethrown with tokens intact. The client is the only code that clears tokens reactively.
**Why.** Clearing tokens on any refresh failure signs users out for a network blip or a 503. Two refresh paths with different rules sign them out unpredictably.
**How.** Tests for: 401 -> refresh -> retry success; refresh 401 clears both tokens; refresh 503 keeps them; retry 500 keeps them; no access token makes no request.
**Check.** Do tests prove a 5xx or network error during refresh leaves both tokens in place?

### FE-SVC-6 · Storage keys live in one module and storage is injected
<!-- doctrine: severity=ORANGE tier=compact principles=P9,P10 -->

**Rule.** Every persistent key string is declared in one module with read and write helpers that take the storage object as an argument. Services and models never read a global storage object or spell a key themselves.
**Why.** Key strings are load-bearing: live sessions already hold data under them, and a rename silently signs everyone out. Injected storage is what lets tests use an in-memory one.
**How.** `readAccessToken(storage)`, `clearAuthTokens(storage)`; the route passes `window.localStorage`.
**Check.** Does each key string appear in exactly one source file?

### FE-SVC-7 · Map wire formats to models in one place at the service boundary
<!-- doctrine: severity=YELLOW tier=compact principles=P2 -->

**Rule.** Each response type is converted to a model by one `fromResponse` mapper that supplies defaults for missing optional fields. Wire naming conventions stop at the service.
**Why.** Components that read raw response fields break when the API adds, renames or omits one.
**How.** `Invitation.fromResponse(raw)`; services return models only.
**Check.** Does any code outside a service or mapper reference a wire field name?

### FE-SVC-8 · Keep concurrency guards on instances and make effects idempotent
<!-- doctrine: severity=ORANGE tier=compact principles=P4 -->

**Rule.** Deduplication of in-flight work (a one-time code exchange) is a field on the service instance, never module-level state. Effects that trigger work tolerate being invoked twice.
**Why.** Frameworks may run an effect twice in development. A module-level map "fixes" that by leaking state across instances and tests.
**How.** `private readonly pending = new Map()`; one instance per mount (`FE-STRUCT-4`); a test fires two concurrent calls and asserts one request.
**Check.** Is there any mutable module-level variable in a service?

### FE-SVC-9 · Nothing in the bundle is secret; build-time configuration needs a rebuild
<!-- doctrine: severity=RED tier=compact principles=P13 -->

**Rule.** No credential is placed in client configuration. Values inlined at build time change only when the client is rebuilt.
**Why.** Every value in a client bundle is readable by anyone. A build-time value changed in the hosting configuration but not rebuilt stays stale forever.
**How.** Provider calls go through the server (`BE-EXT-1`). Deploys rebuild; they do not re-upload an old build (`D-5`).
**Check.** Does any client environment variable hold a secret?

## Presentation

### FE-UI-1 · Components render state and emit events; local state is ephemeral only
<!-- doctrine: severity=ORANGE tier=micro principles=P1 -->

**Rule.** A component turns state into markup and user actions into events. The only state it owns is ephemeral UI state: input text, focus, open or closed.
**Why.** The moment a component owns durable or decision-bearing state, there are two sources of truth and only one is tested.
**How.** Props in, callbacks out; pages translate callbacks to events.
**Check.** Does any component hold state that outlives the interaction or affects the workflow?

### FE-UI-2 · No services, storage, environment, or business branching in presentation
<!-- doctrine: severity=RED tier=compact principles=P1 -->

**Rule.** Components and pages never call a service, read storage, read the environment, or decide a business condition.
**Why.** Each is a decision or a dependency in the one layer that has no unit tests.
**How.** Need data -> emit an event. Need a stored value or flag -> the route reads it. Need a business conditional -> the manager exposes it as state.
**Anti-pattern.** `readStoredSignInMethod()` called in a page body; `consumeToast()` called during render.
**Check.** Do presentation files import any service, storage helper or environment accessor?

### FE-UI-3 · Business constants and rules are pure, tested model functions
<!-- doctrine: severity=YELLOW tier=compact principles=P1,P11 -->

**Rule.** Lists and predicates with business meaning (which email domains are generic, which IDs are placeholders, how a name is inferred) live in the model layer as pure functions with tests.
**Why.** A rule embedded in an eight-hundred-line component is invisible to tests and gets re-implemented by the next component that needs it.
**How.** `models/<Feature>Rules.ts` plus a test file.
**Check.** Does any component define a constant or predicate with business meaning?

### FE-UI-4 · Test hooks in the markup are a contract; refactors keep them
<!-- doctrine: severity=YELLOW tier=compact principles=P7 -->

**Rule.** Identifiers and attributes that end-to-end tests select on are preserved through refactors, or changed together with the tests.
**Why.** A refactor that keeps behavior but renames an element breaks the only tests that exercise the whole product.
**How.** List the hooks before a presentation refactor; diff them after.
**Check.** Are all selectors used by end-to-end tests still present after the change?

### FE-UI-5 · Consume design tokens and shared primitives; never duplicate them
<!-- doctrine: severity=YELLOW tier=compact principles=P9 -->

**Rule.** Colors, spacing, type and shared controls come from the token set and the primitive library. No hard-coded duplicate of a token; no ad hoc copy of a primitive.
**Why.** Every duplicate is a place the next brand or accessibility change will miss.
**How.** Tokens as CSS custom properties in one stylesheet; primitives in one directory; experience styles in co-located files.
**Check.** Does the change hard-code a value that exists as a token or re-create an existing primitive?

---

# Contract rules

The client and the server are written by different hands at different times. The
contract between them is the only thing both can rely on, so it is small, written
down, and tested on both sides.

## Contract

### CT-1 · One documented error shape; clients parse only that
<!-- doctrine: severity=RED tier=compact principles=P3,P9 -->

**Rule.** The API has exactly one error body shape, documented in one place. The client's HTTP layer parses that shape and nothing else.
**Why.** Every additional shape is a client code path nobody tests until production produces it.
**How.** Server side is `BE-API-2`; the client (`FE-SVC-4`) parses `{"error": string}` into its HTTP error type and falls back to a status-based message otherwise.
**Check.** Do both sides implement the same single error shape?

### CT-2 · Status codes carry meaning both sides act on
<!-- doctrine: severity=ORANGE tier=compact principles=P3 -->

**Rule.** 400 is an invalid request or a broken business rule; 401 is dead credentials only; 403 is forbidden; 404 is unknown or not yours; 409 is a conflict; 5xx is a server or upstream failure. Clients act on the class, not on the message.
**Why.** The client's behaviour (retry, refresh, sign out, show the message) is keyed on the status. A wrong status triggers the wrong behaviour.
**How.** The server follows `BE-API-9`, the client's refresh logic follows `FE-SVC-5`. Validation never produces 401 or 5xx.
**Check.** Does each failure path return the status this table assigns?

### CT-3 · Absent and null mean the same; clients omit empty optionals
<!-- doctrine: severity=YELLOW tier=compact principles=P2 -->

**Rule.** For optional request fields the server treats a missing key and an explicit null identically. Clients omit optional fields that are empty.
**Why.** Clients differ in how they serialize "nothing". A server that distinguishes the two breaks one of them.
**How.** Optional fields default to null on request domains; the client builds bodies with conditional spreads.
**Check.** Does each optional field accept both an omitted key and null?

### CT-4 · The server owns workflow state; the client derives display from it
<!-- doctrine: severity=ORANGE tier=micro principles=P1,P4 -->

**Rule.** Where the user is in a multi-step flow is stored and decided by the server. The client renders what the server reports; a local override (going back a step) is pinned to the server value it was taken from and expires when that value changes.
**Why.** Two owners of "current step" disagree after the first refresh, the second tab or a resumed session.
**How.** Mutations return the new state (`CT-5`); the client's override stores `{serverStep, shownStep}` and applies only while `serverStep` matches.
**Check.** Does the client persist or compute workflow position independently of the server?

### CT-5 · Every mutation returns the full updated snapshot
<!-- doctrine: severity=YELLOW tier=compact principles=P9 -->

**Rule.** A write endpoint responds with the complete updated resource state, the same shape the read endpoint returns.
**Why.** The client replaces its state instead of patching it, so client and server cannot drift.
**How.** Service write methods end by building the same domain the read method returns.
**Check.** Does each write endpoint return the same shape as its read endpoint?

### CT-6 · Read paths tolerate legacy data and unknown fields
<!-- doctrine: severity=ORANGE tier=compact principles=P2 -->

**Rule.** The server normalizes obsolete stored values on read. The client supplies defaults for missing fields and ignores unknown ones.
**Why.** Deployed clients and stored rows are always older than the code. A removed step or a new field must not break a session that started last week.
**How.** Server: scrub retired values in the shared derivation (`BE-SVC-7`) with a back-compat test. Client: defaults in `fromResponse` (`FE-SVC-7`).
**Check.** Is there a test reading a record that contains a retired value?

### CT-7 · A contract change lands on both sides with tests and a written note
<!-- doctrine: severity=RED tier=compact principles=P7 -->

**Rule.** Changing a request field, response field, status or error message is done on the server and the client together, with a test on each side and a "contract changes" note in the change description and the slice README.
**Why.** Tightening the server alone (a new required offset on a timestamp, a newly rejected value) breaks deployed clients silently.
**How.** List every request the client can send and check each against the new validation before merging. Deploy order: the server accepts both shapes first, then the client changes, then the server drops the old shape.
**Check.** Does the change description list every contract change and the client impact of each?

### CT-8 · State the auth transport and its consequences
<!-- doctrine: severity=ORANGE tier=compact principles=P13 -->

**Rule.** The project documents whether the client authenticates with bearer tokens or cookies, and applies the matching protections: explicit allowed origins for cross-origin bearer APIs; CSRF protection for cookies; a recorded decision about where tokens are stored.
**Why.** Each transport has a different threat. Bearer tokens in web storage are readable by any injected script; that is a decision to record, not to discover in an audit.
**How.** Allowed origins come from configuration, never a wildcard in production. Record token-storage risk in the debt ledger if accepted (`R-5`).
**Check.** Is the auth transport documented with its origin policy and token-storage decision?

---

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

---

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

---

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

---

# Adoption rules

Doctrine is applied to real projects that already have habits. These rules say how
to bring the standards in without fighting the project.

## Adoption

### A-1 · Follow the precedence order: user, project, existing code, Doctrine
<!-- doctrine: severity=RED tier=micro principles=P14 -->

**Rule.** When instructions conflict, obey in this order: the user's explicit request; the project's own instruction files and tooling configuration; the conventions visible in the existing code; Doctrine; your defaults.
**Why.** A standard that overrides the project's own rules produces changes the maintainers will reject.
**How.** Read the project's instruction files, README, lint and CI configuration first. Note the conflict in one line and follow the higher authority.
**Check.** Where the change departs from Doctrine, is the higher-precedence source named?

### A-2 · Detect the adoption mode before writing code
<!-- doctrine: severity=ORANGE tier=compact principles=P14 -->

**Rule.** Classify the project as greenfield (no conventions yet), aligned (already follows these patterns), or divergent (follows different ones), and act accordingly.
**Why.** The right move differs: build it by the book, extend what is there, or work in the local idiom.
**How.** Greenfield: apply Doctrine fully. Aligned: follow the existing structure and fix gaps the task touches. Divergent: `A-3`.
**Check.** Is the adoption mode stated at the start of the work?

### A-3 · Apply the principle in the local idiom; never plant a competing pattern
<!-- doctrine: severity=ORANGE tier=micro principles=P14 -->

**Rule.** In a divergent project, satisfy the principle with the project's existing mechanisms. Do not introduce Doctrine's structure in one corner of a codebase built another way.
**Why.** Two architectures in one codebase is worse than either. The principle (one owner per decision, parse at the boundary, atomic unit of work) can almost always be met inside the existing structure.
**How.** Use the stack translation table. Propose a structural migration separately, as its own task.
**Check.** Does the change use the project's existing mechanisms for layering, errors and state?

### A-4 · No drive-by refactors
<!-- doctrine: severity=ORANGE tier=micro principles=P14,P12 -->

**Rule.** Change only what the task requires. Improvements noticed along the way are reported, not made.
**Why.** Unrequested changes enlarge the diff, hide the real change from review, and collide with other people's work.
**How.** List them under follow-ups; record them in the debt ledger where one exists.
**Check.** Is every changed line required by the task?

### A-5 · When a rule cannot be met, say so and record it as debt with its ID
<!-- doctrine: severity=YELLOW tier=compact principles=P7 -->

**Rule.** If the project, the deadline or the task prevents meeting a rule, state the rule ID and the reason in the change description and add a ledger entry.
**Why.** A silent exception looks like compliance until it fails.
**How.** "Not met: `BE-TXN-1` — <reason>. Ledger: <entry>."
**Check.** Is each unmet rule named with a reason?

### A-6 · Migrate existing code in order of risk removed per unit of effort
<!-- doctrine: severity=YELLOW tier=compact principles=P6 -->

**Rule.** When bringing an existing codebase toward Doctrine, do the cheapest high-risk fixes first and the structural moves last.
**Why.** The order decides whether the project gets safer in the first week or only after the last refactor.
**How.** Use the migration order below; one step per change.
**Check.** Does the migration plan start with data integrity and input validation rather than restructuring?

## Stack translation

Rows are Doctrine concepts; columns are stacks. Each cell names the idiomatic
mechanism only. Where a stack's idiom is uncertain the cell reads "equivalent
mechanism" rather than a guess.

| Server concept | Django + DRF + pydantic | FastAPI + SQLAlchemy | Node + Prisma/TypeORM + zod | Rails | Go (net/http + sqlc/pgx) | Spring Boot |
| --- | --- | --- | --- | --- | --- | --- |
| request domain | pydantic request model | pydantic model | zod schema | strong params | struct + validation | DTO + Bean Validation |
| response domain | plain dataclass | plain dataclass | plain object type | serializer | response struct | DTO |
| service | service class | service class | service class | service object | service package | `@Service` bean |
| unit of work | `transaction.atomic` | session transaction | `$transaction` | `ActiveRecord::Base.transaction` | `pgx` tx | `@Transactional` |
| savepoint | nested `atomic` | nested transaction | nested transaction | `requires_new: true` | savepoint | `Propagation.NESTED` |
| business error + handler | exception + DRF handler | exception + handler | error class + middleware | exception + rescue | error value + middleware | exception + `@ControllerAdvice` |
| after-commit hook | `transaction.on_commit` | `after_commit` event | event emitter | `after_commit` | tx commit callback | `TransactionSynchronization` |
| migrations | generated migrations | Alembic | Prisma migrate | Rails migrations | sqlc/migrate | Flyway/Liquibase |
| settings + boot validation | settings module | settings + startup check | config module | initializers | config struct | `@ConfigurationProperties` + validation |
| composition root | app/urls wiring | app factory | module wiring | initializer | main wiring | Spring context |

| Client concept | React | Vue 3 | Svelte | Angular | Flutter (BLoC) | SwiftUI |
| --- | --- | --- | --- | --- | --- | --- |
| experience | feature folder | feature folder | feature folder | feature module | feature folder | feature group |
| event | discriminated union | discriminated union | discriminated union | action union | event class | enum + payload |
| state | tagged union | tagged union | tagged union | state union | state class | enum + associated value |
| manager | plain class | plain class | plain class | service class | BLoC | ObservableObject |
| binding | hook/context | composable | store | injectable | `BlocBuilder` | `@StateObject` |
| result value | `Either` | `Either` | `Either` | `Result` | `Either` | `Result` |
| HTTP client | `ApiClient` | `ApiClient` | `ApiClient` | `HttpClient` service | repository | `URLSession` wrapper |
| composition root | route component | route component | route component | route + providers | app-level provider | app entry |
| pure derivation | pure module function | pure module function | pure module function | pure pipe/function | pure function | pure function |
| storage access | injected `Storage` | injected `Storage` | injected `Storage` | injected service | injected store | injected store |

## Migration order

1. Transaction boundaries on multi-write methods (`BE-TXN-1`..`BE-TXN-3`).
2. Request validation at the boundary and the single error contract (`BE-DOM-1`, `BE-API-2`).
3. Scoping of client-supplied IDs and input caps (`BE-API-6`, `BE-API-7`).
4. Delete dead code (`BE-STRUCT-4`).
5. One HTTP client and the token rule (`FE-SVC-4`, `FE-SVC-5`).
6. A unit-test runner in CI (`T-9`, `D-1`).
7. Split tangled state and tag it (`FE-STATE-1`, `FE-STATE-2`, `FE-STATE-3`, `FE-STATE-4`, `FE-STATE-5`).
8. Move workflow logic from pages into the manager, with tests (`FE-MGR-1`, `FE-MGR-2`).

Why this order: step 1 removes the risk of partially applied writes, the most
expensive failure because nobody is told about it. Step 2 makes every later test
easy — bad input stops failing in ways only production sees. Step 3 closes the
worst data-exposure hole. Step 4 shrinks the surface every later step has to move.
Step 5 stops sessions being signed out by a network blip. Step 6 is what makes the
next steps safe to attempt. Steps 7 and 8 are structural and come last, because
they are the largest diffs and buy the least immediate safety.

---

# Checklists

Run the list for each area you touched. Each line names the rules behind it.

## Before you start

- [ ] Read the project's instructions, conventions and CI first (`A-1`).
- [ ] Name the layer that owns each change (`BE-SVC-1`, `FE-MGR-1`).
- [ ] State the adoption mode: greenfield, aligned or divergent (`A-2`).
- [ ] For a write path, decide the unit of work before writing code (`BE-TXN-1`).

## Before you open a change

- [ ] Fetched and compared against the current base; no removals you did not make (`D-11`).
- [ ] The diff contains only what the task required (`A-4`).
- [ ] The description states what, why, contract changes, evidence and rollback (`D-13`).
- [ ] Documentation changed in the same diff as the code (`BE-STRUCT-5`).

## Server change

- [ ] Requests parse into a request domain at the boundary (`BE-DOM-1`).
- [ ] Request domains are strict, ignore extras and cap every client-controlled size (`BE-DOM-2`, `BE-API-7`).
- [ ] Business rules live in the service, not the handler (`BE-SVC-1`).
- [ ] The handler is parse, one service call, respond (`BE-API-1`).
- [ ] Multi-write methods run in one transaction, with a rollback test (`BE-TXN-1`, `T-3`).
- [ ] Remote calls sit outside every transaction (`BE-TXN-2`).
- [ ] A recovered integrity error is raised inside a savepoint (`BE-TXN-3`).
- [ ] Irreversible side effects run after commit (`BE-TXN-4`).
- [ ] Every client-supplied ID is scoped to the caller (`BE-API-6`).
- [ ] Migrations are generated from models, never edited (`BE-DB-1`).
- [ ] Errors use the one contract and end-user messages (`BE-API-2`, `BE-API-3`).

## Client change

- [ ] Events and states are tagged unions; dispatch is exhaustive (`FE-STATE-1`, `FE-STATE-2`, `FE-STATE-3`).
- [ ] Independent concerns have separate state machines (`FE-STATE-4`).
- [ ] A submission owns the flow until it settles (`FE-STATE-6`).
- [ ] No data loaded for a different key is shown (`FE-STATE-7`).
- [ ] The manager owns sequencing and validation; presentation reports (`FE-MGR-2`).
- [ ] Transitions after an `await` read the current state (`FE-MGR-3`).
- [ ] Every service method returns a result value (`FE-SVC-1`).
- [ ] One HTTP client; refresh once on 401 and keep tokens otherwise (`FE-SVC-4`, `FE-SVC-5`).
- [ ] Nothing secret is in the bundle (`FE-SVC-9`).
- [ ] Presentation calls no service, storage or environment (`FE-UI-2`).

## Change that crosses client and server

- [ ] One error shape; both sides parse that shape (`CT-1`).
- [ ] Each failure path returns the status the table assigns (`CT-2`).
- [ ] Writes return the full updated snapshot (`CT-5`).
- [ ] Read paths tolerate legacy values and unknown fields (`CT-6`).
- [ ] Contract changes land on both sides with tests and a written note (`CT-7`).
- [ ] Workflow position is owned by the server (`CT-4`).

## Before merge

- [ ] Each regression test was seen to fail before the fix (`T-2`).
- [ ] Failure paths have tests: rollback, race, expired session (`T-3`).
- [ ] Transaction and constraint tests ran on the production engine (`T-8`).
- [ ] The change was exercised in the running product, per flag state (`R-6`).
- [ ] Findings carry evidence and were verified before acting (`R-2`, `R-3`).
- [ ] Unfixed findings are in the debt ledger (`R-5`).
- [ ] Checks green, review clean, QA passed — otherwise a human decides (`R-7`).

## After deploy

- [ ] New behavior observed at the public edge (`D-9`).
- [ ] Rolled back to a known-good revision if the health check failed (`D-6`).

## Architecture regressions (stop and fix)

- [ ] Business logic in presentation (`FE-MGR-2`).
- [ ] A handler that queries the database (`BE-SVC-1`).
- [ ] A service method that throws an expected failure (`BE-SVC-5`).
- [ ] A second HTTP client (`FE-SVC-4`).
- [ ] A multi-write method with no transaction (`BE-TXN-1`).
- [ ] A caught integrity error with no savepoint (`BE-TXN-3`).
- [ ] A state union mixing two concerns (`FE-STATE-4`).
- [ ] An event with no dispatch case (`FE-STATE-3`).

---

# Bring Doctrine into a project

Doctrine is applied to projects that already have habits. The order is always the
same: read the project, classify it, then bring the standards in without fighting it.

## 1. Read the project first

Before writing anything, read what the project already says about itself (`A-1`):
its instruction files for coding agents, its README, its lint and formatter
configuration, its CI workflows, and the shape of the code nearest the change. The
precedence order is the user's explicit instruction, then the project's own
instructions and conventions, then Doctrine, then your defaults. Where a change
departs from Doctrine, name the higher-precedence source in one line.

## 2. Classify the mode

State the adoption mode at the start of the work (`A-2`). Observable signals:

- **Greenfield** — no application code yet, or a new area with no conventions.
- **Aligned** — the code already separates layers, or mostly does. Read for the
  signals: request parsing at the edge, business rules out of handlers, a client with
  a manager-like object, one HTTP helper.
- **Divergent** — the code works but organized differently: fat controllers, logic in
  pages, several HTTP helpers, no unit tests for the client.

## 3. Greenfield: the first week

Apply Doctrine fully. In order: decide the unit of work and the contract before code;
create the slice or experience directory (`BE-STRUCT-1`, `FE-STRUCT-1`); write domains
and states first, then the model, service and transport (`BE-DOM-*`, `BE-SVC-*`,
`BE-API-*`); stand up a unit-test runner in CI from the first service
(`T-9`, `D-1`). Keep the right thing cheap: adding an event must not cost seven files
if a local state hook costs one line (`P6`).

## 4. Aligned: check for gaps

Follow the existing structure and fix the gaps the task touches (`A-2`). Look for: a
handler that queries the database (`BE-SVC-1`); a multi-write method without a
transaction (`BE-TXN-1`); a service that throws an expected failure (`BE-SVC-5`); a
component that reads storage (`FE-UI-2`); a state union mixing two concerns
(`FE-STATE-4`). Do not fix these unless the task needs the touched code to be
correct — otherwise record them.

## 5. Divergent: honor each principle in the local idiom

Never plant a competing pattern in one corner (`A-3`). Meet the principle with the
project's own mechanisms. Three worked translations:

**A controller-heavy MVC server.** The principle "one owner per decision" (P1) does
not require Doctrine's service classes; it requires that the decision lives in one
place. Keep the controller thin by moving the rules into a model method or a domain
object the controller already uses. "Parse at the boundary" (P2) becomes the
project's existing form or validator object at the controller's entry, not a new
pydantic model. "Unit of work" (P5) becomes the framework's transaction helper
wrapped around the multi-write method, at the same layer the rules already live.

**A client built on a global store with reducers.** "Explicit state" (P4) becomes a
tagged field inside the existing store shape rather than a new manager class; the
reducer's switch is the exhaustive dispatch. "One owner per decision" (P1) means the
reducer, not the component, decides the next step. "Result values" (P3) means the
thunk returns a typed failure rather than throwing, and the reducer maps it to state.

**A server with no ORM.** "Unit of work" (P5) becomes the database transaction the
query layer already exposes, opened after any remote call and closed around local
writes. "Domains are plain values" (BE-DOM-5) is already true; keep the row-to-domain
mapping explicit. "Scoped lookups" (BE-API-6) becomes a `WHERE` clause built from the
caller's identity in every query, not a scan in code.

## 6. Migration order

Bring existing code toward Doctrine in this order (`A-6`), one step per change. The
order is by risk removed per unit of effort:

1. Transaction boundaries on multi-write methods (`BE-TXN-1`..`BE-TXN-3`). Removes
   the most expensive failure — a partially applied write nobody is told about.
2. Request validation at the boundary and the single error contract (`BE-DOM-1`,
   `BE-API-2`). Makes every later test easy and stops bad input failing in production.
3. Scoping of client-supplied IDs and input caps (`BE-API-6`, `BE-API-7`). Closes the
   worst data-exposure hole.
4. Delete dead code (`BE-STRUCT-4`). Shrinks the surface every later step must move.
5. One HTTP client and the token rule (`FE-SVC-4`, `FE-SVC-5`). Stops network blips
   signing users out.
6. A unit-test runner in CI (`T-9`, `D-1`). What makes the next steps safe to attempt.
7. Split tangled state and tag it (`FE-STATE-1`..`FE-STATE-5`). Structural.
8. Move workflow logic from pages into the manager, with tests (`FE-MGR-1`,
   `FE-MGR-2`). The largest diff, the least immediate safety — so it comes last.

## 7. Recording exceptions

When a rule cannot be met, say so with its ID and the reason, and add a ledger entry
(`A-5`): "Not met: `BE-TXN-1` — the legacy helper owns its own transaction. Ledger:
`BE-TXN-1·2026-10-13`." A named exception is a decision; a silent one looks like
compliance until it fails.

## 8. Loading Doctrine into an agent

Point the agent at `agents/README.md`, which lists each supported agent and the file
it reads (a project instruction file, a workspace rules file, or a system prompt).
Install for a project with the CLI, or print the tier you need and paste it into the
agent's system prompt. The operating instructions (`core/operating.md`) travel in
every tier, so the agent knows the precedence order and how to report unmet rules.

---

# Build a backend slice end to end

This guide builds the invitations slice from an empty directory, in the order an
author should work. Each step cites the rule it applies.

## 1. Decide the unit of work and the contract before code

Name the user-visible action and what must fully happen or not at all (`BE-TXN-1`).
Two of this slice's actions write more than once: creating an invitation writes the
invitation and an audit event; revoking writes a status change and an audit event.
Both are units of work, so both will run in a transaction. Listing reads only and
needs none.

Write the contract down before the code: the endpoints, the request and response
shapes, and the exact error sentence for each expected failure. Deciding the messages
now is what lets the transport stay trivial later (`BE-API-3`).

| Method | Path | Body | Response |
| --- | --- | --- | --- |
| GET | `/api/invitations/?team_id=<id>` | — | the list snapshot |
| POST | `/api/invitations/` | `team_id, email, role, message?, expires_at?` | the list snapshot |
| POST | `/api/invitations/<id>/revoke/` | — | the list snapshot |

Every error is `{"error": "<sentence>"}` (`BE-API-2`). Deciding that once, now, means
no endpoint invents its own error shape later.

## 2. Domains: enums, request domains, response domains

Create the slice directory and write `domains.py` first (`BE-STRUCT-1`). Declare each
fixed vocabulary once as an enum (`BE-DOM-4`). Then the request domain: strict types,
extras ignored, whitespace stripped, every client-controlled size capped.

<!-- excerpt: examples/backend/invitations/domains.py -->
```python
class CreateInvitationRequest(RequestDomain):
    team_id: str = Field(min_length=1)
    # Lowercased so the (team, email) natural key does not depend on letter case (BE-SVC-6).
    email: Annotated[EmailStr, AfterValidator(str.lower)]
    role: Role
    # CT-3: null and absent mean the same. BE-API-7: reject over the cap, never truncate.
    message: Optional[str] = Field(default=None, max_length=500)
    # BE-API-8: a timestamp without an offset is rejected.
    expires_at: Optional[AwareDatetime] = None
```

Note the choices. `EmailStr` rejects a malformed address at the boundary (`BE-DOM-1`).
`AfterValidator(str.lower)` normalizes before the natural key is used, so the same
address in different letter case is one invitation (`BE-SVC-6`). `max_length=500`
rejects an oversized message rather than truncating it (`BE-API-7`). `AwareDatetime`
rejects an offset-less timestamp (`BE-API-8`).

The response domain reuses the same field names but plain types, because it serializes
rows that already exist and must not re-validate them (`BE-DOM-3`).

## 3. Model and generated migration

Write the model with an opaque identifier, audit timestamps and a uniqueness
constraint on the natural key (`BE-DB-2`, `BE-DB-3`). Inherit the shared base model so
the identifier and timestamps are not spelled by hand.

Generate the migration; do not write or edit it (`BE-DB-1`). Run the framework's
"no pending migrations" check in CI so a model change without a migration fails the
build (`D-1`).

The audit event is its own table with a foreign key to the invitation, the actor and
the action. It exists because "what happened to this invitation" is asked during every
incident; the write is why the create and revoke paths need transactions.

## 4. Service: injection, factory, transactions, the savepoint, after-commit

The service class owns every rule and every write for the slice (`BE-SVC-1`). It
receives its collaborators through the constructor and offers a `factory()` for the
production wiring (`BE-SVC-2`).

<!-- excerpt: examples/backend/invitations/service.py -->
```python
class InvitationService:
    def __init__(self, team_service: TeamService, notifier: Notifier) -> None:
        self._team_service = team_service
        self._notifier = notifier

    @classmethod
    def factory(cls) -> "InvitationService":
        return cls(TeamService.factory(), LoggingNotifier())
```

Cross-slice access goes through the other slice's service. Membership is the team
slice's rule, so the team service decides it, not a query against the team's tables
(`BE-SVC-3`).

The create method is one transaction, and it is idempotent: a resubmitted invitation
returns the existing one instead of creating a second (`BE-TXN-1`, `BE-SVC-6`).

<!-- excerpt: examples/backend/invitations/service.py -->
```python
    @transaction.atomic
    def create_invitation(
        self, actor_id: str, request: CreateInvitationRequest
    ) -> InvitationListDomain:
        self._team_service.require_member(actor_id, request.team_id)
        # BE-SVC-6: a resubmitted invitation is the same invitation, not a second one.
        if not self._is_invited(request.team_id, request.email):
            self._invite(actor_id, request)
        return self._snapshot(request.team_id)
```

The uniqueness race is where the savepoint earns its keep. Two requests can both pass
the `_is_invited` check and both reach the insert. The database's unique constraint
decides; the code must recover without breaking the surrounding transaction.

<!-- excerpt: examples/backend/invitations/service.py -->
```python
    def _invite(self, actor_id: str, request: CreateInvitationRequest) -> None:
        try:
            # BE-TXN-3: the savepoint keeps the outer transaction usable. Without it the
            # failed INSERT poisons the transaction and the snapshot query raises.
            with transaction.atomic():
                invitation = Invitation.objects.create(
                    team_id=request.team_id,
                    email=request.email,
                    role=request.role.value,
                    message=request.message or "",
                    expires_at=request.expires_at,
                )
        except IntegrityError:
            # BE-DB-3: a concurrent request inserted the same (team, email) first.
            # Its row is the result, exactly as if the lookup had found it.
            return
        self._record(invitation, actor_id, InvitationAction.CREATED)
        # BE-TXN-4: the notification cannot be rolled back, so it is sent only once the
        # invitation is committed. BE-TXN-2: by then no transaction is open.
        transaction.on_commit(partial(self._notify, InvitationDomain.from_model(invitation)))
```

Read the comment on the savepoint literally. `create_invitation` is atomic. Inside it,
a bare `try: create() except IntegrityError:` would catch the error but leave the
outer transaction poisoned: the next query — the `_snapshot` call that builds the
response — raises instead of running, and the endpoint returns a 500 for a race it was
supposed to absorb. Wrapping the insert in its own `transaction.atomic()` opens a
savepoint; the failed statement rolls back to it, and the outer transaction continues.
The recovery query then runs on a healthy transaction.

The notification is sent after commit (`BE-TXN-4`), and by then no transaction is open
(`BE-TXN-2`). The notify failure is logged and swallowed: the invitation is already
committed, so the request should succeed.

Scoped lookups make a foreign identifier indistinguishable from a missing one
(`BE-API-6`), and each write answers with the same read shape (`CT-5`).

## 5. Transport: parse, one call, respond

The handler contains exactly its four moves (`BE-API-1`): declared authentication,
one parse, one service call, one response.

<!-- excerpt: examples/backend/invitations/views.py -->
```python
class InvitationsView(APIView):
    def get(self, request: Request) -> Response:
        query = parse_request(ListInvitationsRequest, request.query_params.dict())
        snapshot = InvitationService.factory().list_invitations(request.user.id, query.team_id)
        return Response(snapshot.to_dict())

    def post(self, request: Request) -> Response:
        body = parse_request(CreateInvitationRequest, request.data)
        snapshot = InvitationService.factory().create_invitation(request.user.id, body)
        return Response(snapshot.to_dict())
```

There is no validation here, no ORM call, no branching on business state. The single
exception handler maps every business error and every validation failure to
`{"error": ...}` with the right status (`BE-API-2`). Validation failures are 400, never
500, and the message is the friendly sentence chosen in step 1 (`BE-API-3`).

Authentication is default-deny; this slice's views require it (`BE-API-5`). A public
endpoint would have to opt out through the dedicated base class, which makes a
forgotten requirement impossible.

## 6. Tests, in the order to write them

Write the tests as you go, each one at the layer's boundary (`T-1`), and watch each
fail before it passes (`T-2`).

1. **Happy path** — create returns the snapshot; the row exists; the audit event exists.
2. **Validation messages** — a malformed email, an oversized message, an offset-less
   timestamp each return 400 with the sentence from step 1.
3. **Scoping** — revoking another team's invitation returns 404 and changes nothing.
4. **Rollback** — force a late failure and assert no invitation and no audit event
   persisted (`T-3`, `T-4`).
5. **Idempotency** — submit the same invitation twice; assert one row and equal
   responses (`BE-SVC-6`).
6. **Race** — two concurrent creates for the same email; assert one row, no 500
   (`T-3`). Run this one on the production engine (`T-8`), because savepoint behavior
   differs by engine.
7. **After-commit** — assert the notifier was not called when the transaction rolled
   back (`BE-TXN-4`).

## 7. README for the slice

Write the slice README in the same change (`BE-STRUCT-5`): its models, its service
methods with inputs, return and errors, and its endpoints. State the facts the code
cannot say out loud — that create and revoke are atomic, that create is idempotent,
that the notification is best-effort.

## Common mistakes

- A bare `try/except IntegrityError` with no savepoint — the recovery query raises and
  the race becomes a 500 (`BE-TXN-3`).
- `@transaction.atomic` on a method that also calls a remote provider — the connection
  is held for the provider's latency (`BE-TXN-2`).
- Sending the notification inside the transaction — it announces a write that may roll
  back (`BE-TXN-4`).
- A handler that reads `request.data` field by field instead of parsing once
  (`BE-DOM-1`).
- A response domain that re-validates stored data and 500s on a legacy row
  (`BE-DOM-3`).
- A second copy of the derivation used by both read and write (`BE-SVC-7`).
- An unscoped `filter(id=...)` that lets one tenant reach another's row (`BE-API-6`).
- A hand-edited migration that diverges from the model (`BE-DB-1`).

## Slice checklist

- [ ] Request domain parsed once, strict, extras ignored (`BE-DOM-1`, `BE-DOM-2`).
- [ ] Every fixed vocabulary is one enum (`BE-DOM-4`).
- [ ] Response domain serializes old rows without raising (`BE-DOM-3`).
- [ ] Service owns all rules and writes (`BE-SVC-1`).
- [ ] Collaborators injected; `factory()` wires production (`BE-SVC-2`).
- [ ] Cross-slice access via the other service (`BE-SVC-3`).
- [ ] Multi-write methods atomic, with a rollback test (`BE-TXN-1`, `T-3`).
- [ ] No transaction spans a remote call (`BE-TXN-2`).
- [ ] Integrity errors recovered inside a savepoint (`BE-TXN-3`).
- [ ] Side effects after commit (`BE-TXN-4`).
- [ ] Handler is parse, one call, respond (`BE-API-1`).
- [ ] One error contract; friendly messages (`BE-API-2`, `BE-API-3`).
- [ ] Client-supplied IDs scoped (`BE-API-6`); sizes capped (`BE-API-7`).
- [ ] Migration generated, never edited (`BE-DB-1`).

---

# Build a client experience end to end

Same treatment as the backend slice, for the client. This guide builds the
invitations experience: a signed-in member opens a team, sees its invitations,
invites someone by email, searches the member directory while the list stays on
screen, and revokes a pending invitation.

## 1. Name the outcome, the events and the states before code

Write down what the user can do (events) and what the screen can show (states) before
writing a line. Events are intents entering the manager; states are renderable shapes
leaving it (`FE-STATE-1`, `FE-STATE-2`). Both are closed, tagged unions.

<!-- excerpt: examples/frontend/src/experiences/invitations/manager/InvitationsEvent.ts -->
```typescript
/** FE-MGR-5: the form reports its whole snapshot on every change. */
export class DraftChanged {
  readonly kind = "DraftChanged" as const;
  constructor(readonly draft: InvitationDraft) {}
}

export class SubmitRequested {
  readonly kind = "SubmitRequested" as const;
}

export class RevokeRequested {
  readonly kind = "RevokeRequested" as const;
  constructor(readonly invitationId: string) {}
}

export type InvitationsEvent =
  | SessionRequested
  | InvitationsRequested
  | DirectorySearchRequested
  | DraftChanged
  | SubmitRequested
  | RevokeRequested;
```

Note what is not here: no "submit succeeded", no "list loaded". Results are not
events. An event is something the user (or the framework) did; the manager turns the
result of that into a state.

Two concerns change independently: who is signed in, and what the screen has loaded.
They get two unions, side by side on the manager (`FE-STATE-4`). One union holding
both would throw away the loaded list every time the session state changed, and the
manager would grow a hidden copy to restore it.

<!-- excerpt: examples/frontend/src/experiences/invitations/manager/InvitationsState.ts -->
```typescript
export class SessionIdle {
  readonly kind = "SessionIdle" as const;
}

export class SessionChecking {
  readonly kind = "SessionChecking" as const;
}

export class SessionSignedOut {
  readonly kind = "SessionSignedOut" as const;
}

export class SessionAuthenticated {
  readonly kind = "SessionAuthenticated" as const;
  constructor(readonly user: TeamMember) {}
}

export class SessionFailed {
  readonly kind = "SessionFailed" as const;
  constructor(readonly failure: AppFailure) {}
}

export type SessionState = SessionIdle | SessionChecking | SessionSignedOut | SessionAuthenticated | SessionFailed;
```

The flow union is shaped for the screen, not for the history that produced it. A
submission is its own state, and the background search is a field of the loaded state
rather than a state of its own.

<!-- excerpt: examples/frontend/src/experiences/invitations/manager/InvitationsState.ts -->
```typescript
/** FE-STATE-6: an invite or a revoke is in flight and owns the flow until it settles. */
export class FlowSubmitting {
  readonly kind = "FlowSubmitting" as const;
  constructor(
    readonly teamId: string,
    readonly invitations: readonly Invitation[],
  ) {}
}

/** Keeps the team and the last known list so the screen can offer a reload without going blank. */
export class FlowFailed {
  readonly kind = "FlowFailed" as const;
  constructor(
    readonly failure: AppFailure,
    readonly teamId: string,
    readonly invitations: readonly Invitation[],
  ) {}
}

export type FlowState = FlowIdle | FlowLoading | FlowLoaded | FlowSubmitting | FlowFailed;
```

## 2. Models and pure rules

Each wire shape becomes a model with a `fromResponse` mapper that supplies defaults
for missing optionals (`FE-SVC-7`). Rules with business meaning live in the model
layer as pure functions with tests (`FE-UI-3`): is an invitation pending, is this
email domain generic, is this an expiry the form may send. The draft is a value, and
the two functions that matter are pure (`FE-MGR-5`): `draftValid(draft)` and
`submissionFromDraft(draft, flags)`. Presentation collects input text; the model
decides whether it is submittable and what request it becomes.

## 3. Services: result values, failure codes, one HTTP client

Each service sits behind an interface and every method returns a result value —
`Either<AppFailure, T>`, failure on the left (`FE-SVC-1`). Expected failures are
returned, never thrown, so the manager's `match` maps both arms to states in one
expression. Failures are normalized at the service boundary into one `AppFailure`
with a stable code (`FE-SVC-2`); the manager branches on the code, never on the
message text. Only messages the API wrote reach the screen; a browser or parser error
string is replaced by the service's fallback (`FE-SVC-3`).

One `ApiClient` builds URLs, sets headers, applies authentication and parses the one
error contract (`FE-SVC-4`). Token handling is a decision table, not scattered
`if`s (`FE-SVC-5`):

| Observed | Action |
| --- | --- |
| No access token stored | No request is made. |
| 401, refresh token present | Refresh once, retry the request once. |
| Refresh rejected 401 | Clear both tokens. |
| Retry returns 401 | Clear both tokens. |
| No refresh token | Clear both tokens. |
| Refresh fails 5xx or network error | Keep both tokens; surface the failure. |
| Retry fails 5xx or network error | Keep both tokens; surface the failure. |

The reading of that table is the rule: a network blip must not sign a user out. Every
key string lives in one storage module with helpers that take the storage object as an
argument (`FE-SVC-6`). Nothing in the bundle is a secret; provider calls go through the
server (`FE-SVC-9`).

## 4. The manager: dispatch, functional transitions, guards

The manager is a plain class with no framework import. It takes its services and an
`onChange` callback in the constructor and exposes one `emit` method (`FE-MGR-1`).

<!-- excerpt: examples/frontend/src/experiences/invitations/manager/InvitationsManager.ts -->
```typescript
  async emit(event: InvitationsEvent): Promise<void> {
    // FE-STATE-3: a new event without a case here fails the type check in `assertNever`.
    switch (event.kind) {
      case "SessionRequested":
        return this.checkSession();
      case "InvitationsRequested":
        return this.loadInvitations(event.teamId);
      case "DirectorySearchRequested":
        return this.searchDirectory(event.query);
      case "DraftChanged":
        return this.changeDraft(event.draft);
      case "SubmitRequested":
        return this.submit();
      case "RevokeRequested":
        return this.revoke(event.invitationId);
      default:
        return assertNever(event);
    }
  }
```

The `default` branch is the exhaustiveness check: adding an event type without a case
fails the type check, and at runtime it throws rather than silently doing nothing.

<!-- excerpt: examples/frontend/src/experiences/invitations/manager/InvitationsManager.ts -->
```typescript
function assertNever(event: never): never {
  throw new Error(`Unhandled event: ${JSON.stringify(event)}`);
}
```

Every transition is a function of the state at the moment the result arrives — never a
value captured before the `await` (`FE-MGR-3`).

<!-- excerpt: examples/frontend/src/experiences/invitations/manager/InvitationsManager.ts -->
```typescript
  /** FE-MGR-3: every transition is a function of the state at the moment it is applied. */
  private updateFlow(next: (current: FlowState) => FlowState): void {
    this.flowState = next(this.flowState);
    this.onChange(this.snapshot);
  }
```

Here is the stale-snapshot bug the pattern avoids. Suppose `loadInvitations` captured
`const before = this.flowState` before the request and, after the `await`, wrote a new
state derived from `before`. While the request was in flight, the user submitted an
invitation, so the flow went `FlowLoaded` -> `FlowSubmitting`. The late load result
would build its next state from `before` (a `FlowLoaded`), overwrite `FlowSubmitting`,
and re-enable the submit button with the write still in flight — a duplicate write from
one impatient double-click. Computing from `current` and returning `current` unchanged
when the state is no longer the one that issued the request prevents it.

The two guards do the rest. A submission owns the flow until it settles: other events
are ignored while `FlowSubmitting`, and a result that lands during it does not replace
it (`FE-STATE-6`). When the key changes, the loading state carries the key only, so a
list loaded for another team cannot be shown under the new one (`FE-STATE-7`).

<!-- excerpt: examples/frontend/src/experiences/invitations/manager/InvitationsManager.ts -->
```typescript
  private async write(
    loaded: FlowLoaded,
    request: () => Promise<Either<AppFailure, readonly Invitation[]>>,
  ): Promise<void> {
    this.updateFlow(() => new FlowSubmitting(loaded.teamId, loaded.invitations));
    const result = await request();
    this.updateFlow((current) => {
      if (current.kind !== "FlowSubmitting") {
        return current;
      }
      return pipe(
        result,
        match<AppFailure, readonly Invitation[], FlowState>(
          (failure) => new FlowFailed(failure, current.teamId, current.invitations),
          // CT-5: the write answers with the full list, which replaces the old one.
          (invitations) => new FlowLoaded(current.teamId, invitations, idleDirectory),
        ),
      );
    });
    this.signOutIfExpired(result);
  }
```

Sequencing, branching, validation and once-only guards are all the manager's job.
Presentation reports what the user did and renders what comes back (`FE-MGR-2`). A
search that is only valid on a loaded screen, a submit that is only valid on a valid
draft, a revoke that is only valid on a pending invitation — each is a guard here, not
a condition in a component.

## 5. Pure derivation and flags

Anything computed for display is a pure function of the states (`FE-STATE-9`):
`deriveView({ sessionState, flowState, draft, flags })` returns the step, which buttons
are enabled, what the tracker shows. Feature flags are parsed by a pure function at the
composition root and passed to the manager as constructor input (`FE-MGR-4`); the
manager derives behavior from them, and both flag states are testable.

## 6. Binding, route, page, components, copy

The framework binding creates one manager per mount and mirrors snapshots into
framework state (`FE-MGR-1`). The route is a composition root: it constructs the
services once, reads environment, flags and storage, passes them to the provider, and
renders the page (`FE-STRUCT-4`). It contains no workflow logic.

The page and components turn state into markup and callbacks; they hold only ephemeral
UI state and call no service, storage or environment (`FE-UI-1`, `FE-UI-2`). Titles,
labels and toast sentences come from a copy module, produced from data and intents on
the state rather than stored on it (`FE-STATE-8`) — the state carries
`continueIntent: "continue" | "schedule"`, and the copy module turns that into words.
Test selectors are a contract; a presentation refactor keeps them or updates the tests
together (`FE-UI-4`). Colors and spacing come from design tokens, not hard-coded
duplicates (`FE-UI-5`).

## 7. Tests

Three layers. The manager is driven directly with queued fake services: build it,
`await emit(...)`, assert the snapshots — submit twice and assert one write; fail a
search mid-submit and assert the state stays `FlowSubmitting`; request team B while
team A is loading and assert the loading state carries no members. The `ApiClient` is
tested for each row of the token table. The pure functions — draft validity, submission
mapping, the view derivation, the flag parse — are tested on their own.

## How this maps to other UI frameworks

Only the binding changes. Where the reference binds with a React context and a hook,
a Vue binding uses a composable holding a `reactive` manager instance, a Svelte binding
uses a store wrapper, an Angular binding injects the manager into a service, and a
Flutter binding exposes it through a `ChangeNotifier`. The manager, the events, the
states, the services and the models are identical in every case, because none of them
import the framework.

## Common mistakes

- Replacing `FlowLoaded` with a `Searching` state, then keeping a hidden copy of the
  list to restore it (`FE-STATE-5`).
- Letting a late search result overwrite `FlowSubmitting` and re-enable submit
  (`FE-STATE-6`).
- Carrying the previous list into the loading state under a new team id
  (`FE-STATE-7`).
- Deciding the next step in the page instead of the manager (`FE-MGR-2`).
- Branching on a failure's message text instead of its code (`FE-SVC-2`).
- Clearing tokens on any refresh failure, signing users out on a 503 (`FE-SVC-5`).
- Reading storage or the environment inside a component (`FE-UI-2`).
- Putting user-facing sentences on the state (`FE-STATE-8`).

## Experience checklist

- [ ] Events and states are closed, tagged unions (`FE-STATE-1`, `FE-STATE-2`).
- [ ] Dispatch is exhaustive; an unknown event throws (`FE-STATE-3`).
- [ ] Independent concerns are separate unions (`FE-STATE-4`).
- [ ] Background work is a field of the loaded state (`FE-STATE-5`).
- [ ] A submission owns the flow until it settles (`FE-STATE-6`).
- [ ] No data loaded for another key is shown (`FE-STATE-7`).
- [ ] State carries data and intent; copy is presentation-side (`FE-STATE-8`).
- [ ] Derived display values are pure and tested (`FE-STATE-9`).
- [ ] The manager has no framework import and is unit-tested (`FE-MGR-1`).
- [ ] Sequencing and validation live in the manager (`FE-MGR-2`).
- [ ] Transitions read current state after every `await` (`FE-MGR-3`).
- [ ] Flags are resolved at the route and passed in (`FE-MGR-4`).
- [ ] Forms report snapshots; mapping is pure (`FE-MGR-5`).
- [ ] Services return result values and typed failure codes (`FE-SVC-1`, `FE-SVC-2`).
- [ ] One HTTP client; the token table is tested (`FE-SVC-4`, `FE-SVC-5`).
- [ ] Presentation calls no service, storage or environment (`FE-UI-2`).

---

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

---

# Ship a change from branch to verified deploy

A runbook. Follow it in order; each step names the rule behind it and the evidence to
capture.

1. **Fetch and compare.** Fetch the remote and confirm your base is still the tip
   (`D-11`). If the base moved, rebase or merge deliberately and re-read the diff.
   Evidence: the base commit hash you branched from and the hash you will merge into.
2. **Branch fresh.** Create the branch from current main, not from an old local copy
   (`D-10`). Evidence: the branch name and its parent commit.
3. **Work in small steps.** Each commit changes one thing and leaves the tree
   buildable (`D-12`). Evidence: `git log --oneline` for the branch.
4. **Run the local checks, identical to CI.** The local script runs every check the
   pipeline runs (`D-1`, `D-2`). Fix failures before pushing. Evidence: the exact
   command and its exit status.
5. **Write the change description.** What changed, why, any contract change, the
   evidence, and how to roll back (`D-13`). Evidence: the description text.
6. **Open the change and let CI run.** The pipeline is the same set of checks (`D-1`).
   Do not merge on a red or skipped pipeline. Evidence: the pipeline result per job.
7. **Pass the review and QA gates.** A review with no open RED or ORANGE findings, and
   QA passed (`R-7`). Outstanding findings that are recorded and deferred do not block
   if they are YELLOW and in the ledger (`R-5`). Evidence: review result, QA result.
8. **Merge.** Merge with the repository's default method. Do not merge with a moved
   base or a running pipeline (`D-11`). Evidence: the merge commit or PR number.
9. **Watch the deploy.** The deploy is gated by the health check; a failing check
   stops the rollout (`D-4`, `D-6`). Evidence: the deploy job result.
10. **Verify at the edge.** Exercise the changed behavior against the public entry
    point, not an internal host (`D-9`). Evidence: the request and its response.
11. **Clean up.** Delete the branch; close the change (`D-12`). Evidence: the branch
    is gone.
12. **Rollback procedure.** Know the previous known-good revision before you deploy
    (`D-6`). To roll back, redeploy that revision; do not forward-fix a broken deploy
    under time pressure. Evidence: the revision you would return to.

## What to do when

| Situation | Action |
| --- | --- |
| The base moved after your last push (`D-11`) | Re-read the diff against the new base, then re-run CI. Never merge on a stale base. |
| A local check failed (`D-1`) | Fix it locally and re-run the identical command. Do not push expecting CI to differ. |
| A regression test was never seen red (`T-2`) | Revert the fix, watch the test fail, re-apply. A test that never failed proves nothing. |
| Deploy failed before the swap (`D-4`) | Nothing is serving the new code; fix and redeploy. Evidence: the failed job log. |
| Deploy failed after the swap (`D-6`) | Redeploy the previous known-good revision first, then investigate. |
| The health check passed but the edge is wrong (`D-9`) | Roll back, then reproduce against the edge; the health check is not a substitute for the edge check. |
| Configuration-only change (`D-7`, `D-8`) | Change the value, assert the running configuration changed as intended, then verify at the edge. |
| A safety net cannot be asserted before an irreversible step (`D-7`) | Stop. Fix the net first. |
| The change is large | Split it. A reversible change merges sooner and rolls back cheaper (`P12`). |

## Evidence to keep for the change

- The base commit hash and the branch parent.
- The local check command and its result.
- The pipeline result per job.
- The review result and the QA result.
- The deploy result and the edge verification.
- The previous known-good revision for rollback.
