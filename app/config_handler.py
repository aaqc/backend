#!/usr/bin/python

import yaml
from shutil import copyfile

CONFIG = {}  # config for everything
TOKENS = {}

config_filepath = "/app/config.yml"
default_config = "default_config.yml"


with open(config_filepath, "r") as stream:
    try:
        CONFIG = yaml.safe_load(stream)
        TOKENS = CONFIG["tokens"]

    except FileNotFoundError as err:
        print("Unable to load config.yml. No such file or directory.")
        print(f'Creating config at "{config_filepath}"...')
        copyfile(default_config, config_filepath)
        exit(1)

    except yaml.YAMLError as err:
        print(f"YAML Error: {err}")
        raise err
