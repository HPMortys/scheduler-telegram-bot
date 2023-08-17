import os
import json


def get_environ_var_value(variable_name, default=None):
    return os.environ.get(variable_name, default)


def set_environ_var(variable_name, value):
    os.environ.setdefault(variable_name, value)


def load_config():
    with open('config_sch_bot.json') as file:
        config = json.load(file)
    return config
