#!/usr/bin/python

api_filepath = "/home/elal/.config/tokens/"

def read_token_file(filepath: str) -> str:
    fh = open(filepath, "r")
    token = fh.readlines()[0]
    fh.close()

    return token

def get_token(api: str) -> str:
    return read_token_file(f"{api_filepath}{api}.token")

