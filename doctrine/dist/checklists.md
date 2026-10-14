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

## Rule checks

### Backend

- [ ] `BE-STRUCT-1` Does every new capability live in its own slice directory with domains, service, transport and tests?
- [ ] `BE-STRUCT-2` Do domain modules import zero model or ORM symbols at runtime, and does no module import from a transport module?
- [ ] `BE-STRUCT-3` Is every module under a shared/common package free of product-specific nouns and rules?
- [ ] `BE-STRUCT-4` Does every new module have at least one caller outside itself and at least one test?
- [ ] `BE-STRUCT-5` If a service method or endpoint changed, did the slice README change in the same diff?
- [ ] `BE-DOM-1` Does every handler obtain all of its inputs from a single parsed request domain?
- [ ] `BE-DOM-2` Does each request field have the narrowest type that fits, and are unknown fields ignored rather than rejected?
- [ ] `BE-DOM-3` Can every row already in the database be serialized by the response domain without raising?
- [ ] `BE-DOM-4` Is every fixed vocabulary declared once and compared by member everywhere?
- [ ] `BE-DOM-5` Can every domain class be constructed in a unit test with no database and no network?
- [ ] `BE-SVC-1` Is the handler free of ORM calls and of branching on business conditions?
- [ ] `BE-SVC-2` Does the service obtain every collaborator from its constructor rather than importing and instantiating it inline?
- [ ] `BE-SVC-3` Does each service touch only its own slice's models?
- [ ] `BE-SVC-4` Do service signatures mention only primitives and domain types?
- [ ] `BE-SVC-5` Does every expected failure raised by a service derive from the shared business-error base?
- [ ] `BE-SVC-6` Is there a test that performs the write twice and asserts no duplicate?
- [ ] `BE-SVC-7` Is each derivation implemented exactly once?
- [ ] `BE-TXN-1` Does every multi-write service method run in one transaction, with a test that forces a late failure and asserts nothing persisted?
- [ ] `BE-TXN-2` Is every remote call outside all transaction blocks?
- [ ] `BE-TXN-3` Is every caught integrity error raised from inside a nested atomic block?
- [ ] `BE-TXN-4` Are all non-database side effects registered to run on commit?
- [ ] `BE-API-1` Does the handler consist only of parse, one service call and the response?
- [ ] `BE-API-2` Does every error path, including validation and malformed input, produce the single error shape with a 4xx status?
- [ ] `BE-API-3` Would every error message make sense to a person who has never seen the code?
- [ ] `BE-API-4` Can any response body contain text produced by a third party or by a configuration check?
- [ ] `BE-API-5` Is every public endpoint public through the explicit opt-out base and nothing else?
- [ ] `BE-API-6` For every client-supplied ID, is there a test using another tenant's ID that gets 404?
- [ ] `BE-API-7` Does every client-controlled size or option have a tested limit?
- [ ] `BE-API-8` Is every timestamp field on a request domain timezone-aware?
- [ ] `BE-API-9` Can any non-credential failure produce a 401?
- [ ] `BE-API-10` Does the liveness handler run zero queries, and does something else monitor the dependencies?
- [ ] `BE-EXT-1` Is the upstream request built field by field from an allowlist, with redirects disabled and a timeout?
- [ ] `BE-EXT-2` Is the provider SDK imported in exactly one module?
- [ ] `BE-EXT-3` Does application code import any cloud SDK to read configuration?
- [ ] `BE-DB-1` Does CI fail when models and migrations disagree, and is every migration file tool-generated?
- [ ] `BE-DB-2` Do new tables inherit the shared base model?
- [ ] `BE-DB-3` Is every uniqueness rule backed by a constraint and a tested conflict path?
- [ ] `BE-CFG-1` Is there exactly one mechanism that selects the profile?
- [ ] `BE-CFG-2` Does booting production with an unsafe value fail, and does CI run the production configuration check?
- [ ] `BE-CFG-3` Does a test fail if a setting is read that the manifest does not declare?
- [ ] `BE-CFG-4` Is each trusted header backed by evidence captured at the origin?

### Frontend

- [ ] `FE-STRUCT-1` Does each feature's code live under one experience directory with the six sub-folders it needs?
- [ ] `FE-STRUCT-2` Does any model import a service or storage module, or any component import a service?
- [ ] `FE-STRUCT-3` Does everything in the shared area have at least two callers or is it single-by-nature infrastructure?
- [ ] `FE-STRUCT-4` Does the route construct each service exactly once per mount and contain no conditional workflow?
- [ ] `FE-STATE-1` Is every event a member of one tagged union with a literal `kind`?
- [ ] `FE-STATE-2` Does presentation select what to render by `state.kind` with no `instanceof` chains or optional-field probing?
- [ ] `FE-STATE-3` Does adding a new event type without a case fail the type check?
- [ ] `FE-STATE-4` Does any single state union mix two concerns that can change independently?
- [ ] `FE-STATE-5` Does the manager hold any variable that duplicates data from a previous state?
- [ ] `FE-STATE-6` Is there a test showing that a result arriving during a submission leaves the state `Submitting`?
- [ ] `FE-STATE-7` Is there a test that switches keys and asserts the loading state is empty?
- [ ] `FE-STATE-8` Does any manager state contain a user-facing sentence, or any component branch on one?
- [ ] `FE-STATE-9` Is each derived display value computed in one tested pure function?
- [ ] `FE-MGR-1` Can the manager be constructed and driven in a unit test with no UI framework import?
- [ ] `FE-MGR-2` Is there any conditional about the workflow outside the manager and its pure helpers?
- [ ] `FE-MGR-3` Does every post-await transition read the current state inside the update function?
- [ ] `FE-MGR-4` Does any file outside routes and the flag model read the environment?
- [ ] `FE-MGR-5` Are validity and request mapping pure functions with tests, not code in a component?
- [ ] `FE-SVC-1` Does every service method's return type include the failure arm, with no expected failure thrown?
- [ ] `FE-SVC-2` Does the manager branch on failure codes only, never on message text?
- [ ] `FE-SVC-3` Can a browser or parser error string reach the UI?
- [ ] `FE-SVC-4` Is `fetch` (or the HTTP library) called from exactly one module?
- [ ] `FE-SVC-5` Do tests prove a 5xx or network error during refresh leaves both tokens in place?
- [ ] `FE-SVC-6` Does each key string appear in exactly one source file?
- [ ] `FE-SVC-7` Does any code outside a service or mapper reference a wire field name?
- [ ] `FE-SVC-8` Is there any mutable module-level variable in a service?
- [ ] `FE-SVC-9` Does any client environment variable hold a secret?
- [ ] `FE-UI-1` Does any component hold state that outlives the interaction or affects the workflow?
- [ ] `FE-UI-2` Do presentation files import any service, storage helper or environment accessor?
- [ ] `FE-UI-3` Does any component define a constant or predicate with business meaning?
- [ ] `FE-UI-4` Are all selectors used by end-to-end tests still present after the change?
- [ ] `FE-UI-5` Does the change hard-code a value that exists as a token or re-create an existing primitive?

### Contracts

- [ ] `CT-1` Do both sides implement the same single error shape?
- [ ] `CT-2` Does each failure path return the status this table assigns?
- [ ] `CT-3` Does each optional field accept both an omitted key and null?
- [ ] `CT-4` Does the client persist or compute workflow position independently of the server?
- [ ] `CT-5` Does each write endpoint return the same shape as its read endpoint?
- [ ] `CT-6` Is there a test reading a record that contains a retired value?
- [ ] `CT-7` Does the change description list every contract change and the client impact of each?
- [ ] `CT-8` Is the auth transport documented with its origin policy and token-storage decision?

### Testing

- [ ] `T-1` Does each new behaviour have a test at its layer's public boundary?
- [ ] `T-2` Does the change state that each new regression test failed before the fix?
- [ ] `T-3` For each new write path, is there a rollback test and, where a constraint exists, a conflict test?
- [ ] `T-4` Would the test fail if the code called the collaborator with a wrong argument or one extra time?
- [ ] `T-5` Does each test assert every outcome its name states?
- [ ] `T-6` Does the suite pass in shuffled order with the network disabled?
- [ ] `T-7` Is the CI test step the same command the README documents, and is the engine it selects stated?
- [ ] `T-8` Were the transaction and constraint tests run on the production engine?
- [ ] `T-9` Does every manager, derivation and service introduced have tests that CI runs?
- [ ] `T-10` Are the prerequisites for each end-to-end test written down, including feature-flag values?
- [ ] `T-11` Is each multiply-declared fact covered by a test that compares its sources?

### Delivery

- [ ] `D-1` Does CI run every check the project relies on, including the newly added one?
- [ ] `D-2` Do check jobs run without cloud credentials and are all actions pinned to a commit?
- [ ] `D-3` Does the deploy workflow run the test suite on the revision it ships?
- [ ] `D-4` Is the gate a job-level condition that runs before credentials are requested?
- [ ] `D-5` After this change merges, is a manual deploy or rebuild needed, and is that written in the change description?
- [ ] `D-6` Can every step before the swap fail without affecting traffic, and does a failed health check restore the previous release?
- [ ] `D-7` Is each irreversible step preceded by an assertion of its safety net?
- [ ] `D-8` Is the entry document uploaded after its assets and served uncached?
- [ ] `D-9` Does the change description record evidence taken from the public endpoint after deploy?
- [ ] `D-10` Was the work done in a task-specific branch from current main with no unrelated files touched?
- [ ] `D-11` Does the diff against the current base contain only changes this task intended?
- [ ] `D-12` Can CI apply infrastructure without a deliberate human or protected step?
- [ ] `D-13` Does the description contain all five parts with concrete evidence?

### Review

- [ ] `R-1` Was each lens applied, and is the outcome of each recorded?
- [ ] `R-2` Does every finding include all five parts?
- [ ] `R-3` Is each acted-on finding marked as verified, with how?
- [ ] `R-4` Was each finding re-checked against the final diff by someone who did not write the fix?
- [ ] `R-5` Is every unfixed finding in the ledger with a rule ID and a disposition?
- [ ] `R-6` Is there a recorded run of the change in the product for each flag state?
- [ ] `R-7` Are all three gates green, or has a person explicitly accepted the remaining findings?

### Adoption

- [ ] `A-1` Where the change departs from Doctrine, is the higher-precedence source named?
- [ ] `A-2` Is the adoption mode stated at the start of the work?
- [ ] `A-3` Does the change use the project's existing mechanisms for layering, errors and state?
- [ ] `A-4` Is every changed line required by the task?
- [ ] `A-5` Is each unmet rule named with a reason?
- [ ] `A-6` Does the migration plan start with data integrity and input validation rather than restructuring?
