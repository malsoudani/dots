import secrets


def new_id() -> str:
    """Return a random, URL-safe identifier that reveals neither order nor volume (BE-DB-2)."""
    return secrets.token_urlsafe(16)
