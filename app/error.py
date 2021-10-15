from typing import Any


error_msgs = {
    "json-decode-error": "Message could not be parsed",
    "message-type-missing": "The type parameter is missing",
    "message-type-invalid": "The type parameter is of incorrect type (should be string)",
    "not-implemeneted": "The message type is not implemented",
    "generic-error": "Something went wrong, check logs",
}

error_types = {
    NotImplementedError: "not-implemeneted",
    TypeError: "message-type-invalid",
    KeyError: "message-type-missing",
}


def error_compose(err) -> dict[str, Any]:
    error_type = err if type(err) == str else error_types[err]
    
    error_msg = error_msgs[error_type]
    return {"success": False, "error": error_type, "error_message": error_msg}

