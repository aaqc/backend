from fastapi import HTTPException

# error_msgs = {
#     "json-decode-error": "Message could not be parsed",
#     "message-type-missing": "The type parameter is missing",
#     "message-type-invalid": "The type parameter is of incorrect type (should be string)",
#     "not-implemeneted": "The message type is not implemented",
#     "generic-error": "Something went wrong, check logs",
# }

def API_Error(Exception):
    def __init__(self, message: str="API Error", errorcode: int=500):
        self.message = message
        self.errorcode = errorcode

def GenericError(API_Error):
    def __init__(self, *args, **kwargs):
        super(*args, **kwargs)
        self.message = "Something went wrong, check logs"

def MessageTypeMissing(API_Error):
    def __init__(self, *args, **kwargs):
        super(*args, **kwargs)
        self.message = "The type parameter is missing"

def MessageTypeInvalid(API_Error):
    def __init__(self, *args, **kwargs):
        super(*args, **kwargs)
        self.message = "The type parameter is of incorrect type"

def NotImplemented(API_Error):
    def __init__(self, *args, **kwargs):
        super(*args, **kwargs)
        self.message = "Not implemented"
        self.errorcode = 501


def UserNotFound(API_Error):
    def __init__(self, *args, **kwargs):
        super(*args, **kwargs)
        self.message = "User not found"
        self.errorcode = 404

def AuthFailure(API_Error):
    def __init__(self, *args, **kwargs):
        super(*args, **kwargs)
        self.message = "Authetication failure"
        self.errorcode = 401

def UserCreationFailure(API_Error):
    def __init__(self, *args, **kwargs):
        super(*args, **kwargs)
        self.message = "User creation failed. Possible duplicate credentials"
        self.errorcode = 400


def ThirdPartyError(API_Error):
    def __init__(self, *args, **kwargs):
        super(*args, **kwargs)
        self.message = "Third-party API or service failed. Nothing we can do :("
        self.errorcode = 503 
