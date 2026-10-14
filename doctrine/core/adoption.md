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