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

def fetch_token(api: str) -> str:
    return CONFIG["tokens"][api] 

