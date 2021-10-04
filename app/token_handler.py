#!/usr/bin/python

import yaml

CONFIG = {} # config for everything
config_filepath = "./config.yml"

with open(config_filepath, "r") as stream:
    try:
        CONFIG = yaml.safe_load(stream)

    except FileNotFoundError as err:
        print("Unable to load config.yml. No such file or directory.")
        raise err

    except yaml.YAMLError as err:
        print(f"YAML Error: {err}")

# def read_token_file(filepath: str) -> str:
#     try:
#         fh = open(filepath, "r")
#         token = fh.readlines()[0]
#         fh.close()
# 
#         return token
#     except FileNotFoundError:
#         print(f"Token not found. {filepath} no such file or directory.")
#         return ""
# 
# def get_token(api: str) -> str:
#     return read_token_file(f"{api_filepath}{api}.token")

