import os

import allay.paths
import allay.yaml_util

env = None


def load_config():
    global env

    env_config_path = os.path.join(allay.paths.paths['allay_config_root'], 'env.yaml')
    env = allay.yaml_util.load(env_config_path)


def write_docker_compose():
    docker_compose_path = os.path.join(allay.paths.paths['project_root'], 'docker-compose.yaml')
    allay.yaml_util.write(env, docker_compose_path)