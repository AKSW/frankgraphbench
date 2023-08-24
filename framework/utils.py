def get_optional_argument(config, key, default=False):
    try:
        return config[key]
    except KeyError:
        return default
    except TypeError:
        return default
    except Exception as e:
        print(e)
        return default