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