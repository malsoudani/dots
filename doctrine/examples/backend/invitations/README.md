# invitations

Invite people to a team by email, list a team's invitations, revoke a pending one.

## Models

- `Invitation`: `team`, `email`, `role`, `status`, `message`, `expires_at`.
  Unique on (`team`, `email`).
- `InvitationEvent`: audit row (`invitation`, `actor`, `action`).

## Domains

- Vocabularies: `Role` (`member`, `admin`), `InvitationStatus` (`pending`,
  `accepted`, `revoked`), `InvitationAction` (`created`, `revoked`).
- Requests: `ListInvitationsRequest`, `CreateInvitationRequest`.
- Responses: `InvitationDomain`, `InvitationListDomain` (the snapshot).

## Service: `InvitationService(team_service, notifier)`

Build it with `InvitationService.factory()`. Every method takes the caller's user
id first and returns the team's full snapshot, `InvitationListDomain`.

| Method | Input | Errors |
| --- | --- | --- |
| `list_invitations(actor_id, team_id)` | team id | `TeamNotFound` |
| `create_invitation(actor_id, request)` | `CreateInvitationRequest` | `TeamNotFound` |
| `revoke_invitation(actor_id, invitation_id)` | invitation id | `InvitationNotFound`, `InvalidInvitationState` |

Facts the signatures cannot state:

- `create_invitation` and `revoke_invitation` are each one transaction. The
  invitation change and its `InvitationEvent` are written together or not at all.
- `create_invitation` is idempotent on (`team_id`, `email`), compared in lower
  case. A repeat returns the existing invitation unchanged, writes no event and
  sends no notification. This holds when two requests race.
- The notification is sent after commit. A `NotifierError` is logged and does not
  fail the request.
- Membership is decided by `TeamService`. A team or an invitation the caller
  cannot access answers exactly like one that does not exist.

## Endpoints

| Method and path | Request | 200 response |
| --- | --- | --- |
| `GET /api/invitations/?team_id=<id>` | query `team_id` | `{"team_id", "invitations": [Invitation]}` |
| `POST /api/invitations/` | `{"team_id", "email", "role", "message"?, "expires_at"?}` | same snapshot |
| `POST /api/invitations/<id>/revoke/` | none | same snapshot |

Invitation: `{"id", "team_id", "email", "role", "status", "message", "expires_at", "created_at"}`.
`message` is at most 500 characters. `expires_at` is ISO-8601 with an offset and is
returned in UTC. `message` and `expires_at` may be omitted or null.

## Errors

| Status | Message |
| --- | --- |
| 400 | `<field> is required`, `Enter a valid email address`, `Unsupported role: <value>`, `expires_at must be an ISO-8601 datetime with a timezone offset`, `message must be at most 500 characters`, `Request body must be a JSON object.` Several are joined with `; `. |
| 400 | `Only a pending invitation can be revoked.` |
| 401 | `Sign in to continue.` |
| 404 | `Team <id> was not found.`, `Invitation <id> was not found.` |
