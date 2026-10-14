# Doctrine compact v0.1.0

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

## Principles

- `P1` Decisions live in one layer
- `P2` Parse at the boundary, trust inside
- `P3` Expected failures are values, mapped once
- `P4` State is explicit, closed, and exhaustive
- `P5` A unit of work is all-or-nothing
- `P6` Pay for ceremony only where you collect
- `P7` Machines enforce, prose explains
- `P8` Build what is used, delete what is not
- `P9` One way to do each thing
- `P10` Wire dependencies at the edge
- `P11` Tests prove behavior at boundaries, including failure
- `P12` Ship in small reversible steps and verify at the edge
- `P13` Secure by construction
- `P14` The host project wins

## Frontend

- `FE-STRUCT-1` Organize the client by experience; each owns its flow end to end
- `FE-STRUCT-2` Dependencies point inward: presentation, manager, services, models
- `FE-STRUCT-3` Share code only after a second real use
- `FE-STRUCT-4` Routes are composition roots: build services once, inject, decide nothing
- `FE-STATE-1` Intents are explicit events in a closed, tagged union
- `FE-STATE-2` Renderable states are explicit, tagged, and shaped for the UI
- `FE-STATE-3` Dispatch exhaustively; an unknown event is an error
- `FE-STATE-4` Give orthogonal concerns separate state machines
- `FE-STATE-5` Background work is sub-state of the loaded state, never a replacement
- `FE-STATE-6` A submission owns the flow until it settles
- `FE-STATE-7` Never show data loaded for a different key
- `FE-STATE-8` State carries data and intent; presentation owns the words
- `FE-STATE-9` Derive view models with pure functions
- `FE-MGR-1` The manager is a plain class; the framework binding is a thin adapter
- `FE-MGR-2` The manager owns sequencing, branching, validation, and automatic actions
- `FE-MGR-3` Compute each transition from the state at the moment the result arrives
- `FE-MGR-4` Resolve flags and environment at the composition root and pass them in
- `FE-MGR-5` Forms report snapshots; validity and submission mapping are pure functions
- `FE-SVC-1` Every service method returns a result value: failure left, success right
- `FE-SVC-2` Normalize failures at the service boundary into typed codes
- `FE-SVC-3` Show users only messages your own API wrote
- `FE-SVC-4` One HTTP client owns URLs, headers, error parsing, and auth
- `FE-SVC-5` Refresh once on 401; clear tokens only when the session is provably dead
- `FE-SVC-6` Storage keys live in one module and storage is injected
- `FE-SVC-7` Map wire formats to models in one place at the service boundary
- `FE-SVC-8` Keep concurrency guards on instances and make effects idempotent
- `FE-SVC-9` Nothing in the bundle is secret; build-time configuration needs a rebuild
- `FE-UI-1` Components render state and emit events; local state is ephemeral only
- `FE-UI-2` No services, storage, environment, or business branching in presentation
- `FE-UI-3` Business constants and rules are pure, tested model functions
- `FE-UI-4` Test hooks in the markup are a contract; refactors keep them
- `FE-UI-5` Consume design tokens and shared primitives; never duplicate them

## Contracts

- `CT-1` One documented error shape; clients parse only that
- `CT-2` Status codes carry meaning both sides act on
- `CT-3` Absent and null mean the same; clients omit empty optionals
- `CT-4` The server owns workflow state; the client derives display from it
- `CT-5` Every mutation returns the full updated snapshot
- `CT-6` Read paths tolerate legacy data and unknown fields
- `CT-7` A contract change lands on both sides with tests and a written note
- `CT-8` State the auth transport and its consequences

## Testing

- `T-1` Test at the boundary each layer exposes
- `T-2` Prove every fix red before green
- `T-3` Failure paths are first-class test cases
- `T-4` Fakes fail loudly
- `T-5` A test asserts exactly what its name claims
- `T-6` Tests are deterministic, order-independent, and offline
- `T-7` Run the same command locally and in CI, and know what it selects
- `T-8` Exercise transactions and constraints on the production database engine
- `T-9` A pattern justified by testability must have tests
- `T-10` Keep end-to-end tests few, on stable hooks, with stated prerequisites
- `T-11` Contract-test configuration: code, infrastructure, and docs must agree

## Delivery

- `D-1` CI gates every change: lint, types, tests, deploy checks
- `D-2` CI has least privilege and pinned dependencies
- `D-3` A deploy workflow re-tests before it ships
- `D-4` Gate deploys with an explicit switch checked before credentials
- `D-5` Know what triggers a deploy; baked configuration needs a rebuild
- `D-6` Releases are additive until an atomic swap, then health-gated
- `D-7` Assert the safety net before any irreversible step
- `D-8` Publish hashed assets first, the entry document last and uncached
- `D-9` Verify a deploy by observing new behavior at the public edge
- `D-10` Work in a fresh branch from current main, never in a dirty checkout
- `D-11` Re-fetch and compare before squashing; check for silent removals
- `D-12` Infrastructure applies are deliberate, never automatic from defaults
- `D-13` A pull request states what, why, contract changes, evidence, and rollback

## Review

- `R-1` Review through independent lenses
- `R-2` A finding needs a location, evidence, a failure scenario, and a fix
- `R-3` Verify a finding before acting on it
- `R-4` Re-audit every fix independently
- `R-5` Classify by severity and keep an append-only debt ledger
- `R-6` Exercise the change in the running product, including flag states
- `R-7` Merge on green checks, clean review, and passing QA; else a human decides

## Adoption

- `A-1` Follow the precedence order: user, project, existing code, Doctrine
- `A-2` Detect the adoption mode before writing code
- `A-3` Apply the principle in the local idiom; never plant a competing pattern
- `A-4` No drive-by refactors
- `A-5` When a rule cannot be met, say so and record it as debt with its ID
- `A-6` Migrate existing code in order of risk removed per unit of effort

## Deep dives

The lists above are titles only. Before you apply, cite or review against a rule, read its full text (rule, why, how, check):

- Principles: `.doctrine/core/principles.md`
- Frontend: `.doctrine/core/frontend.md`
- Contracts: `.doctrine/core/contracts.md`
- Testing: `.doctrine/core/testing.md`
- Delivery: `.doctrine/core/delivery.md`
- Review: `.doctrine/core/review.md`
- Adoption: `.doctrine/core/adoption.md`
- Checklists: `.doctrine/checklists.md`

How-to guides. Read the matching one before you start that kind of work:

- `.doctrine/howto/adopt-in-a-project.md`: Bring Doctrine into a project
- `.doctrine/howto/backend-slice.md`: Build a backend slice end to end
- `.doctrine/howto/frontend-experience.md`: Build a client experience end to end
- `.doctrine/howto/review-a-change.md`: Review a change against Doctrine
- `.doctrine/howto/ship-a-change.md`: Ship a change from branch to verified deploy
