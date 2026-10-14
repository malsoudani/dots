from pydantic import BaseModel, ConfigDict


class RequestDomain(BaseModel):
    """Base for request domains: unknown fields are ignored, text is trimmed (BE-DOM-2)."""

    # Trimming runs before length checks, so a whitespace-only value fails min_length.
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)


class ResponseDomain(BaseModel):
    """Base for response domains: plain types, no input rules (BE-DOM-3)."""

    def to_dict(self) -> dict:
        return self.model_dump(mode="json")
