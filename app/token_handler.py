#!/usr/bin/python

import os
user_home = os.path.expanduser('~')

api_filepath = f"{user_home}/.config/tokens/"

def read_token_file(filepath: str) -> str:
    try:
        fh = open(filepath, "r")
        token = fh.readlines()[0]
        fh.close()

        return token
    except FileNotFoundError:
        print(f"Token not found. {filepath} no such file or directory.")
        return ""

def get_token(api: str) -> str:
    return read_token_file(f"{api_filepath}{api}.token")

