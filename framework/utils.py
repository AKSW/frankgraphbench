

def get_optional_argument(config, key, default):
    try:
        return config[key]
    except KeyError:
        return default