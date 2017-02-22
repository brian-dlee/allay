import collections
import os
import sys

import allay.paths
import allay.yaml_util

settings = {}


def _merge_settings(dict1, dict2):
    for k, v in dict2.iteritems():
        if (k in dict1 and isinstance(dict1[k], dict)
                and isinstance(dict2[k], collections.Mapping)):
            _merge_settings(dict1[k], dict2[k])
        else:
            dict1[k] = dict2[k]


def explain():
    global settings

    print "\n{0:-^50}".format(' Active Configuration ')
    sys.stdout.write(allay.yaml_util.pretty_print(settings))
    print '-' * 50, "\n"


def import_settings(obj):
    _merge_settings(settings, obj.__dict__)


def load_config():
    global settings

    settings_config_path = os.path.join(allay.paths.paths['allay_config_root'], 'settings.yaml')
    _merge_settings(settings, allay.yaml_util.load(settings_config_path) or {})

    user_settings_config_path = os.path.join(allay.paths.paths['project_root'], '.allayrc')

    if os.path.exists(user_settings_config_path):
        _merge_settings(settings, allay.yaml_util.load(user_settings_config_path) or {})
