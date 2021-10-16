from errortypes import *
from typing import Any


error_ids = {
    "json-decode-error": APIJSONDecodeError,
    "message-type-missing": MessageTypeMissing,
    "message-type-invalid": MessageTypeInvalid,
    "not-implemeneted": APINotImplemented,
    "generic-error": GenericError,
}
