import collections


def deep_merge(base, new_settings):
    for k, v in new_settings.iteritems():
        if k in base and isinstance(base[k], dict) and isinstance(new_settings[k], collections.Mapping):
            base[k] = deep_merge(base[k], new_settings[k])
        else:
            base[k] = new_settings[k]

    return base
