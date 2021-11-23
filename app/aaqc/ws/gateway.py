from .connection_manager import ConnectionManager
from typing import Any, Optional, Union
from time import time_ns
from .handle_data import handle_data
import typing
from .. import error


def construct(
    _type: str,
    data: Optional[Union[dict[Any, Any], list[Any]]] = None,
    nonce: Optional[Any] = None,
):
    payload = {"type": _type}
    if data is not None:
        payload |= {"data": data}
    if nonce is not None:
        payload |= {"nonce": nonce}
    return payload


def handle_message(message: Any, manager: ConnectionManager):
    if "type" not in message:
        raise KeyError("Message type missing")

    t: str = message["type"]
    if type(t) != str:
        raise TypeError("Message type was off incorrect type")
    nonce: Optional[Any] = None
    if "nonce" in message:
        nonce = message["nonce"]

    try:
        return construct(*handle_data(manager, t), nonce)
    except (TypeError, NotImplementedError, KeyError) as error:
        pass
        # return error.compose_error(error)
