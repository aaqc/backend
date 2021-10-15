from fastapi import HTTPException


def API_Error(Exception):
    def __init__(self, message: str = "API Error", status_code: int = 500):
        self.message = message
        self.status_code = status_code


def GenericError(API_Error):
    def __init__(self, *args, **kwargs):
        super(*args, **kwargs)
        self.message = "Something went wrong, check logs"


def MessageTypeMissing(API_Error):
    def __init__(self, *args, **kwargs):
        super(*args, **kwargs)
        self.message = "The type parameter is missing"
        self.status_code = 400


def MessageTypeInvalid(API_Error):
    def __init__(self, *args, **kwargs):
        super(*args, **kwargs)
        self.message = "The type parameter is of incorrect type"
        self.status_code = 400


def APINotImplemented(API_Error):
    def __init__(self, *args, **kwargs):
        super(*args, **kwargs)
        self.message = "Not implemented"
        self.status_code = 501


def UserNotFound(API_Error):
    def __init__(self, *args, **kwargs):
        super(*args, **kwargs)
        self.message = "User not found"
        self.status_code = 404


def AuthFailure(API_Error):
    def __init__(self, *args, **kwargs):
        super(*args, **kwargs)
        self.message = "Authetication failure"
        self.status_code = 401


def UserCreationFailure(API_Error):
    def __init__(self, *args, **kwargs):
        super(*args, **kwargs)
        self.message = "User creation failed. Possible duplicate credentials"
        self.status_code = 400


def ThirdPartyError(API_Error):
    def __init__(self, *args, **kwargs):
        super(*args, **kwargs)
        self.message = "Third-party API or service failed. Nothing we can do :("
        self.status_code = 503
