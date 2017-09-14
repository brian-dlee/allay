import os

from config import settings, get_volumes_dir, get_project_root, get_config_root
import allay.paths
import allay.yaml_util
import allay.logger


def configure_volumes():
    if 'volumes' not in settings:
        settings['volumes'] = {}

    for service, service_definition in env['services'].items():
        for volume in service_definition['volumes']:
            if volume in settings['volumes']:
                settings['volumes'][volume] = ':'.join([
                    get_volume_source(volume),
                    get_volume_target(volume),
                    get_volume_opts(volume)
                ])


def get_volume_target(name):
    if 'volumes' not in settings or name not in settings['volumes']:
        return None

    if 'target' in settings['volumes'][name]:
        return settings['volumes'][name]['target']

    return os.path.join('/volumes', name)


def get_volume_source(name):
    if 'volumes' not in settings or name not in settings['volumes']:
        return None

    if 'source' in settings['volumes'][name]:
        return settings['volumes'][name]['source']

    return os.path.join(get_volumes_dir(), name)


def get_volume_opts(name):
    if 'volumes' not in settings or name not in settings['volumes']:
        return None

    if 'opts' in settings['volumes'][name]:
        return settings['volumes'][name]['opts']

    return 'rw'


def load_files():
    global env

    env_config_path = os.path.join(get_config_root(), 'env.yml')

    if not os.path.exists(env_config_path):
        allay.logger.error("Allay env.yml does not exist. Checked at " + env_config_path)

    env = allay.yaml_util.load(env_config_path)


def write_docker_compose():
    docker_compose_path = os.path.join(get_project_root(), 'docker-compose.yml')
    allay.yaml_util.write(env, docker_compose_path)

env = {}
