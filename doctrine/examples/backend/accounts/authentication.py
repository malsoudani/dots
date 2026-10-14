from rest_framework.authentication import TokenAuthentication


class BearerAuthentication(TokenAuthentication):
    """Reads `Authorization: Bearer <token>`; missing or dead credentials answer 401 (BE-API-9)."""

    keyword = "Bearer"
