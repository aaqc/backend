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

    def compose_response(self):
        json_response = self.error_cast.compose_response()
