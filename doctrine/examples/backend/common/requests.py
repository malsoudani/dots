from typing import TypeVar

from pydantic import ValidationError

from common.domains import RequestDomain
from common.exceptions import InvalidRequest

RequestT = TypeVar("RequestT", bound=RequestDomain)

OFFSET_REQUIRED = "{field} must be an ISO-8601 datetime with a timezone offset"
# BE-API-3: validator error types become sentences a person can act on.
MESSAGES = {
    "missing": "{field} is required",
    "enum": "Unsupported {field}: {value}",
    "string_too_long": "{field} must be at most {limit} characters",
    # EmailStr reports every failure as value_error. A custom validator must raise
    # its own error type and add it here rather than reuse value_error.
    "value_error": "Enter a valid email address",
    "timezone_aware": OFFSET_REQUIRED,
    "datetime_type": OFFSET_REQUIRED,
    "datetime_parsing": OFFSET_REQUIRED,
    "datetime_from_date_parsing": OFFSET_REQUIRED,
}


def parse_request(request_class: type[RequestT], data: object) -> RequestT:
    """Turn raw transport input into a request domain, or raise InvalidRequest (BE-DOM-1)."""
    if not isinstance(data, dict):
        raise InvalidRequest("Request body must be a JSON object.")
    try:
        return request_class.model_validate(data)
    except ValidationError as error:
        messages = [_message(request_class, item) for item in error.errors()]
        raise InvalidRequest("; ".join(messages)) from error


def _message(request_class: type[RequestDomain], error: dict) -> str:
    field = ".".join(str(part) for part in error["loc"])
    value = error["input"]
    declared = request_class.model_fields.get(field)
    blank = value is None or (isinstance(value, str) and not value.strip())
    if blank and declared is not None and declared.is_required():
        return f"{field} is required"
    template = MESSAGES.get(error["type"], "{field} is invalid")
    return template.format(field=field, value=value, limit=error.get("ctx", {}).get("max_length"))
