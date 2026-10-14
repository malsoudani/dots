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