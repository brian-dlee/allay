import os

import allay.paths
import allay.yaml_util


def merge(source, destination):
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            merge(value, node)
        else:
            destination[key] = value

    return destination


def divide_and_conquer(s, k, v):
    if k.find('.') > -1:
        ks = k.split('.')
        k = ks[0]

        if k not in s:
            s[k] = {}

        s = merge({k: divide_and_conquer(s[k], '.'.join(ks[1:]), v)}, s)
    else:
        s = merge({k: v}, s)

    return s


def flat_settings():
    def flatten(k, v):
        if not isinstance(v, (dict, list, tuple)):
            return {
                k: v
            }

        iterable = v.iteritems() if isinstance(v, dict) else enumerate(v)
        result = {}

        for nk, nv in iterable:
            result.update(flatten(str(nk) if k is None else k + '.' + str(nk), nv))

        return result

    return flatten(None, settings)


def g(name=None, default=None):
    if name is None:
        for k, v in flat_settings().iteritems():
            result = merge(divide_and_conquer(result, k, v), result)

        return result

    return settings.get(name, default).format(**flat_settings())


def s(name, value):
    global settings

    if name:
        settings = divide_and_conquer(settings, name, value)
    else:
        settings = merge(value, settings)


def get_project_root():
    return g('allay_paths_project_root')


def get_vcs_root():
    return g('allay_paths_vcs_root')


def get_config_root():
    return g('allay_paths_config_root')


def get_volumes_dir():
    return g('allay_paths_volumes_dir')


def load_files():
    settings_config_path = os.path.join(
        g('allay_paths_config_root'),
        'settings.yml'
    )

    if os.path.exists(settings_config_path):
        settings.update(allay.yaml_util.load(settings_config_path))

    volumes_config_path = os.path.join(
        g('allay_paths_config_root'), 'volumes.yml')

    if os.path.exists(volumes_config_path):
        s('volumes', allay.yaml_util.load(volumes_config_path))

    remotes_config_path = os.path.join(g('allay_paths_config_root'), 'remotes.yml')

    if os.path.exists(remotes_config_path):
        s('remotes', allay.yaml_util.load(remotes_config_path))

    user_settings_config_path = os.path.join(g('allay_paths_project_root'), '.allayrc')

    if os.path.exists(user_settings_config_path):
        s(None, allay.yaml_util.load(user_settings_config_path))


settings = {}
