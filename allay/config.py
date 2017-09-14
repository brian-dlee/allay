import os

import allay.paths
import allay.yaml_util


def get_project_root():
    return settings['allay_paths_project_root']


def get_vcs_root():
    return settings['allay_paths_vcs_root']


def get_config_root():
    return settings['allay_paths_config_root']


def get_volumes_dir():
    return settings['allay_paths_volumes_dir']


def load_files():
    settings_config_path = os.path.join(settings['allay_paths_config_root'], 'settings.yml')

    if os.path.exists(settings_config_path):
        settings.update(allay.yaml_util.load(settings_config_path))

    volumes_config_path = os.path.join(settings['allay_paths_config_root'], 'volumes.yml')

    if os.path.exists(volumes_config_path):
        settings['volumes'] = {}
        settings['volumes'].update(
            allay.yaml_util.load(volumes_config_path)
        )

    user_settings_config_path = os.path.join(settings['allay_paths_project_root'], '.allayrc')

    if os.path.exists(user_settings_config_path):
        settings.update(
            allay.yaml_util.load(user_settings_config_path)
        )

settings = {}
