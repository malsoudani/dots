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