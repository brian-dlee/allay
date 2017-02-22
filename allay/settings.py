import os
import sys

import allay.paths
import allay.yaml_util

settings = {}


def explain():
    global settings

    print "\n{0:-^50}".format(' Active Configuration ')
    sys.stdout.write(allay.yaml_util.pretty_print(settings))
    print '-' * 50, "\n"


def import_settings(obj):
    global settings

    for setting in obj.__dict__.keys():
        settings[setting] = getattr(obj, setting)


def load_config():
    global settings

    settings_config_path = os.path.join(allay.paths.paths['allay_config_root'], 'settings.yaml')
    settings.update(allay.yaml_util.load(settings_config_path) or {})

    user_settings_config_path = os.path.join(allay.paths.paths['project_root'], '.allayrc')

    if os.path.exists(user_settings_config_path):
        settings.update(allay.yaml_util.load(user_settings_config_path) or {})
