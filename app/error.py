from typing import Any
from errortypes import *

error_casts = {
    NotImplementedError: APINotImplemented,
    TypeError: APITypeError,
    KeyError: MessageTypeMissing,
}


class API_Error_Cast(API_Error):
    def __init__(self, error: Exception, *args, **kwargs):
        super(*args, **kwargs)
        self.error_cast = error_casts.get(error, GenericError)(*args, **kwargs)

    def compose_error(self):
        return self.error_cast.compose_error()


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


# def error_compose(err) -> dict[str, Any]:
#     error_type = err if type(err) == str else error_types[err]
#
#     error_msg = error_msgs[error_type]
#     return {"success": False, "error": error_type, "error_message": error_msg}
