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