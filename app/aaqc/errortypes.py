from fastapi import HTTPException
from fastapi.responses import JSONResponse


class APIError(Exception):
    def __init__(
        self,
        status_code: int = 500,
        error: str = "api-error",
        error_string: str = "API Error",
    ):
        self.status_code = status_code
        self.error = error
        self.error_string = error_string

    def compose_response(self):
        return JSONResponse(
            status_code=self.status_code,
            content={
                "success": False,
                "error": self.error,
                "error_message": self.error_string,
            },
        )


class GenericError(APIError):
    def __init__(self):
        self.error = "generic-error"
        self.error_string = "Something went wrong"


class MessageTypeMissing(APIError):
    def __init__(self):
        self.status_code = 400
        self.error = "message-type-missing"
        self.error_string = "The type parameter is missing"


class MessageTypeInvalid(APIError):
    def __init__(self):
        self.status_code = 400
        self.error = "message-type-invalid"
        self.error_string = "The type parameter is of incorrect type"


class APINotImplemented(APIError):
    def __init__(self):
        self.status_code = 501
        self.error = "api-not-implemented"
        self.error_string = "API function not implemented"


class UserNotFound(APIError):
    def __init__(self):
        self.status_code = 404
        self.error = "user-not-found"
        self.error_string = "User not found"


class AuthFailure(APIError):
    def __init__(self):
        self.status_code = 401
        self.error = "authentication-failure"
        self.error_string = (
            "Authentication failure, invalid password or authentication token."
        )


class UserCreationFailure(APIError):
    def __init__(self):
        self.status_code = 400
        self.error = "user-creation-failure"
        self.error_string = "User creation failed."


class EmailUnavailableError(APIError):
    def __init__(self):
        self.status_code = 409
        self.error = "email-in-use"
        self.error_string = "An account with this email already exists."


class GroupJoinFailure(APIError):
    def __init__(self):
        self.status_code = 400
        self.error = "group-join-failure"
        self.error_string = "Could not join group."


class GroupNotFound(APIError):
    def __init__(self):
        self.status_code = 404
        self.error = "group-not-found"
        self.error_string = "Group not found."


class ThirdPartyError(APIError):
    def __init__(self):
        self.status_code = 503
        self.error = "third-party-error"
        self.error_string = f"Third-party API or service failed. Nothing we can do :("


class APIJSONDecodeError(APIError):
    def __init__(self):
        self.status_code = 503
        self.error = "json-decode-error"
        self.error_string = "Failed to parse JSON"
