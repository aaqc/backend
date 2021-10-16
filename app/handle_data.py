from connection_manager import ConnectionManager
from typing import Any, Optional, Union
from time import time_ns
from errortypes import *
from error import API_Error_Cast
import typing

from api_functions import functions


def handle_data(manager: ConnectionManager, t: str) -> tuple[str, Any]:
    if t not in functions:
        return APINotImplemented().compose_response()

    return functions[t](data={"manager": manager})
