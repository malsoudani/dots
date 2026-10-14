# teams

Teams, their memberships, and the member directory. Other slices ask this
slice's service whether a user belongs to a team; they never read its tables.

## Models

- `Team`: `name`.
- `Membership`: `team`, `user`. Unique on (`team`, `user`).

## Domains

- Request: `SearchMembersRequest` (`q`, at most 100 characters, default empty).
- Responses: `MemberDomain`, `TeamMembersDomain`.

## Service: `TeamService()`

Build it with `TeamService.factory()`.

| Method | Returns | Errors |
| --- | --- | --- |
| `is_member(user_id, team_id)` | `bool` | none |
| `require_member(user_id, team_id)` | `None` | `TeamNotFound` |
| `search_members(actor_id, team_id, query)` | `TeamMembersDomain` | `TeamNotFound` |

Facts the signatures cannot state:

- `TeamNotFound` is raised both for a team that does not exist and for a team the
  caller does not belong to, with the same message.
- `search_members` matches `query` against name or email, ignoring case, and
  orders by name. An empty query returns every member.
- The directory reads each member's name and email through the membership's user
  relation. The user model has no rules of its own, so it has no service.

## Endpoints

| Method and path | Request | 200 response |
| --- | --- | --- |
| `GET /api/teams/<team_id>/members/?q=<text>` | query `q`, optional | `{"team_id", "members": [{"id", "email", "name"}]}` |

## Errors

| Status | Message |
| --- | --- |
| 400 | `q must be at most 100 characters` |
| 401 | `Sign in to continue.` |
| 404 | `Team <id> was not found.` |
