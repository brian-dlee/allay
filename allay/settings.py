import collections
import os
import sys

import allay.paths
import allay.yaml_util

settings = {}


def merge_settings(new_settings):
    global settings

    for k, v in new_settings.iteritems():
        if (k in settings and isinstance(settings[k], dict)
                and isinstance(new_settings[k], collections.Mapping)):
            merge_settings(settings[k], new_settings[k])
        else:
            settings[k] = new_settings[k]


def explain():
    global settings

    print "\n{0:-^50}".format(' Active Configuration ')
    sys.stdout.write(allay.yaml_util.pretty_print(settings))
    print '-' * 50, "\n"


def load_config():
    global settings

    settings_config_path = os.path.join(allay.paths.paths['allay_config_root'], 'settings.yaml')
    merge_settings(allay.yaml_util.load(settings_config_path) or {})

    user_settings_config_path = os.path.join(allay.paths.paths['project_root'], '.allayrc')

    if os.path.exists(user_settings_config_path):
        merge_settings(allay.yaml_util.load(user_settings_config_path) or {})
