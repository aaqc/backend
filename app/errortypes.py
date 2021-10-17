from fastapi import HTTPException
from fastapi.responses import JSONResponse


class API_Error(Exception):
    def __init__(
        self,
        status_code: int = 500,
        error: str = "api-error",
        errorString: str = "API Error",
    ):
        self.status_code = status_code
        self.error = error
        self.errorString = errorString

    def compose_response(self):
        return JSONResponse(
            status_code=self.status_code,
            content={
                "success": False,
                "error": self.error,
                "error_message": self.errorString,
            },
        )


class GenericError(API_Error):
    def __init__(self, *args, **kwargs):
        self.error = "generic-error"
        self.errorString = "Something went wrong"


class MessageTypeMissing(API_Error):
    def __init__(self, *args, **kwargs):
        self.status_code = 400
        self.error = "message-type-missing"
        self.errorString = "The type parameter is missing"


class MessageTypeInvalid(API_Error):
    def __init__(self, *args, **kwargs):
        self.status_code = 400
        self.error = "message-type-invalid"
        self.errorString = "The type parameter is of incorrect type"


class APINotImplemented(API_Error):
    def __init__(self, *args, **kwargs):
        self.status_code = 501
        self.error = "api-not-implemented"
        self.errorString = "API function not implemented"


class UserNotFound(API_Error):
    def __init__(self, *args, **kwargs):
        self.status_code = 404
        self.error = "user-not-found"
        self.errorString = "User not found"


class AuthFailure(API_Error):
    def __init__(self, *args, **kwargs):
        self.status_code = 401
        self.error = "authentication-failure"
        self.errorString = (
            "Authetication failure, invalid password or authentication token."
        )


class UserCreationFailure(API_Error):
    def __init__(self, *args, **kwargs):
        self.status_code = 400
        self.error = "user-creation-failure"
        self.errorString = "User creation failed. Possible duplicate credentials"


class ThirdPartyError(API_Error):
    def __init__(self, *args, **kwargs):
        self.status_code = 503
        self.error = "third-party-error"
        self.errorString = "Third-party API or service failed. Nothing we can do :("


class APIJSONDecodeError(API_Error):
    def __init__(self, *args, **kwargs):
        self.status_code = 503
        self.error = "json-decode-error"
        self.errorString = "Failure to parse JSON"
