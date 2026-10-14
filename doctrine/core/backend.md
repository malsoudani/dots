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