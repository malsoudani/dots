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