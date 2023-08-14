import os
import json


def get_env_var_value(var_name, default=None):
    return os.environ.get(var_name, default=default)


def load_config():
    with open('config_sch_bot.json') as file:
        config = json.load(file)
    return config
