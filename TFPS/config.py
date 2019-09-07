import json


settings: {}
with open('config.json', 'r') as f:
    settings = json.load(f)


def get_setting(key):
    return settings[key]
