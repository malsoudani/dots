# Doctrine micro v0.1.0

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
- `P11` Tests prove behavior at boundaries, including failure
- `P12` Ship in small reversible steps and verify at the edge
- `P13` Secure by construction
- `P14` The host project wins

## Rules

### Backend

- `BE-STRUCT-2` Dependencies point inward: transport to service to persistence
- `BE-DOM-1` Parse every request into a request domain at the transport boundary
- `BE-SVC-1` Business rules live in services; transport never touches persistence
- `BE-TXN-1` One service method is one transaction
- `BE-TXN-2` Never hold a transaction open across an outbound network call
- `BE-API-2` One error contract for the whole API, produced in one place
- `BE-API-6` Scope every lookup to the caller; foreign and unknown IDs look the same
- `BE-EXT-1` Third-party credentials stay server-side behind an allowlisting proxy
- `BE-CFG-3` No secret in any repository or client; one store, one manifest, one test

### Frontend

- `FE-STRUCT-2` Dependencies point inward: presentation, manager, services, models
- `FE-STATE-1` Intents are explicit events in a closed, tagged union
- `FE-STATE-2` Renderable states are explicit, tagged, and shaped for the UI
- `FE-MGR-1` The manager is a plain class; the framework binding is a thin adapter
- `FE-MGR-2` The manager owns sequencing, branching, validation, and automatic actions
- `FE-SVC-1` Every service method returns a result value: failure left, success right
- `FE-SVC-4` One HTTP client owns URLs, headers, error parsing, and auth
- `FE-SVC-5` Refresh once on 401; clear tokens only when the session is provably dead
- `FE-UI-1` Components render state and emit events; local state is ephemeral only

### Contracts

- `CT-4` The server owns workflow state; the client derives display from it

### Testing

- `T-1` Test at the boundary each layer exposes
- `T-2` Prove every fix red before green

### Delivery

- `D-1` CI gates every change: lint, types, tests, deploy checks
- `D-9` Verify a deploy by observing new behavior at the public edge
- `D-11` Re-fetch and compare before squashing; check for silent removals

### Review

- `R-2` A finding needs a location, evidence, a failure scenario, and a fix

### Adoption

- `A-1` Follow the precedence order: user, project, existing code, Doctrine
- `A-3` Apply the principle in the local idiom; never plant a competing pattern
- `A-4` No drive-by refactors
