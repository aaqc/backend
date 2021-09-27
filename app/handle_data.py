from connection_manager import ConnectionManager
from typing import Any, Optional, Union
from time import time_ns
import typing

from api_functions import functions

def handle_data(manager: ConnectionManager, t: str) -> tuple[str, Any]:
    if(t not in functions):
        raise NotImplementedError("Message t is not implemented")

    return functions[t](data={"manager": manager})

