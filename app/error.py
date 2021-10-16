from typing import Any
from errortypes import *

error_casts = {
    NotImplementedError: APINotImplemented,
    TypeError: APITypeError,
    KeyError: MessageTypeMissing,
}


# error_msgs = {
#     "json-decode-error": "Message could not be parsed",
#     "message-type-missing": "The type parameter is missing",
#     "message-type-invalid": "The type parameter is of incorrect type (should be string)",
#     "not-implemeneted": "The message type is not implemented",
#     "generic-error": "Something went wrong, check logs",
# }
# 
# error_types = {
#     NotImplementedError: "not-implemeneted",
#     TypeError: "message-type-invalid",
#     KeyError: "message-type-missing",
# }


class API_Error_Cast(API_Error):
    def __init__(
        self,
        status_code: int = 500,
        error: str = "ws-api-error",
        errorString: str = "WS API Error",
    ):
        self.status_code = status_code
        self.error = error
        self.errorString = errorString

    def compose_error(self, error: Exception):
        error_cast = error_casts.get(error, GenericError)
        return error_cast().compose_error(self)


# def error_compose(err) -> dict[str, Any]:
#     error_type = err if type(err) == str else error_types[err]
# 
#     error_msg = error_msgs[error_type]
#     return {"success": False, "error": error_type, "error_message": error_msg}
