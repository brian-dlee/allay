import os

from allay.dict_utils import deep_merge
import allay.paths
import allay.yaml_util


def divide_and_conquer(s, k, v):
    if k.find('.') > -1:
        ks = k.split('.')
        k = ks[0]

        if k not in s:
            s[k] = {}

        s = deep_merge(s, {k: divide_and_conquer(s[k], '.'.join(ks[1:]), v)})
    else:
        s = deep_merge(s, {k: v})

    return s


def flat_settings(s=None):
    if not s:
        s = settings

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

    return flatten(None, s)


def g(name=None, default=None):
    def format_value(v):
        return v.format(**flat_settings()) if isinstance(v, str) else v

    focus = settings

    if name is not None:
        for p in name.split('.'):
            focus = focus.get(p, None)

            if focus is None:
                return default

    result = {}

    if not isinstance(focus, dict):
        return format_value(focus)

    for k, v in flat_settings(focus).iteritems():
        value = format_value(v)

        result = deep_merge(result, divide_and_conquer(result, k, value))

    return result


def s(name, value):
    global settings

    if name:
        settings = divide_and_conquer(settings, name, value)
    else:
        settings = deep_merge(settings, value)


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
