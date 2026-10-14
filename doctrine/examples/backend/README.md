# Backend reference implementation: team invitations

A signed-in member of a team invites people to it by email, lists the team's
invitations, and revokes a pending one. The project is small on purpose: every
file exists to show one or more Doctrine rules, and the rule catalogs and how-to
guides quote it verbatim.

Stack: Python 3.10+, Django 5.2, Django REST framework, pydantic v2, SQLite.

## Run it

```
uv run --no-project --with-requirements requirements.txt python manage.py makemigrations --check --dry-run
uv run --no-project --with-requirements requirements.txt python manage.py test
```

The first command fails when models and migrations disagree (`BE-DB-1`). The
second runs the suite against in-memory SQLite, with no network and no services
(`T-6`, `T-7`). Transaction and constraint behavior differs between engines, so
run the same suite on the production engine before relying on it (`T-8`).

## Layout

```
config/        settings and the root URL table
common/        shared code with no product meaning: ids, base model, domain bases,
               business-error base, request parsing, error handler, liveness
accounts/      the user model and the bearer authentication scheme
teams/         slice: membership checks and the member directory
invitations/   slice: list, create and revoke invitations
```

Each slice holds its own domains, models, service, transport, migrations, tests
and README (`BE-STRUCT-1`). Read `invitations/README.md` first.

## API

Every non-2xx response has the body `{"error": "<message for the end user>"}`.

| Method and path | Answers |
| --- | --- |
| `GET /api/invitations/?team_id=<id>` | 200 `{"team_id", "invitations": [Invitation]}` |
| `POST /api/invitations/` | 200, the same snapshot |
| `POST /api/invitations/<id>/revoke/` | 200, the same snapshot |
| `GET /api/teams/<team_id>/members/?q=<text>` | 200 `{"team_id", "members": [{"id", "email", "name"}]}` |
| `GET /api/status/` | 200 `{"status": "ok"}`, public |
| `GET /healthz` | 200 `{"status": "ok"}`, public, zero queries |

Requests carry `Authorization: Bearer <token>`. Issuing and refreshing tokens is
outside this example; the tests create a token row directly.

## Where each rule is shown

| Rule | File |
| --- | --- |
| `BE-STRUCT-1`, `BE-STRUCT-5` | `invitations/`, `teams/` and their READMEs |
| `BE-STRUCT-2` | `invitations/domains.py`, `teams/domains.py` (type-only model imports) |
| `BE-STRUCT-3` | `common/` |
| `BE-DOM-1`, `BE-API-3` | `common/requests.py` |
| `BE-DOM-2`, `BE-DOM-3` | `common/domains.py`, `invitations/domains.py` |
| `BE-DOM-4` | `invitations/domains.py`, `invitations/models.py`, `invitations/service.py` |
| `BE-DOM-5`, `BE-SVC-4` | `invitations/domains.py` (`from_model` only copies fields) |
| `BE-SVC-1`, `BE-SVC-2`, `BE-SVC-3`, `BE-SVC-6` | `invitations/service.py` |
| `BE-SVC-5` | `common/exceptions.py`, `invitations/service.py`, `teams/service.py` |
| `BE-TXN-1`, `BE-TXN-2`, `BE-TXN-3`, `BE-TXN-4` | `invitations/service.py` |
| `BE-API-1` | `invitations/views.py`, `teams/views.py` |
| `BE-API-2`, `BE-API-5` | `common/views.py`, `config/settings.py` |
| `BE-API-6` | `teams/service.py`, `invitations/service.py` |
| `BE-API-7`, `BE-API-8` | `invitations/domains.py`, `teams/domains.py` |
| `BE-API-9` | `accounts/authentication.py`, `common/views.py` |
| `BE-API-10` | `common/health.py`, `config/urls.py` |
| `BE-EXT-2` | `invitations/notifier.py` |
| `BE-DB-1` | `*/migrations/` (generated, never edited) |
| `BE-DB-2` | `common/ids.py`, `common/models.py` |
| `BE-DB-3` | `invitations/models.py`, `invitations/service.py` |
| `CT-3`, `CT-5` | `invitations/domains.py`, `invitations/service.py` |
| `T-1`, `T-3`, `T-4`, `T-5` | `invitations/tests.py`, `teams/tests.py`, `common/tests.py` |

## What is left out

- Settings are one file. A real project has base, local and production profiles
  selected by one environment variable, and a production profile that refuses to
  boot on unsafe values (`BE-CFG-1`, `BE-CFG-2`).
- Only liveness is implemented. A real project adds a readiness check that
  exercises the database and feeds monitoring (`BE-API-10`).
- `LoggingNotifier` stands in for a mail provider. A real adapter replaces it in
  `InvitationService.factory()` and nowhere else (`BE-EXT-2`).
