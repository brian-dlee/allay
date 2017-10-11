import glob
import os

from config import settings, get_volumes_dir, get_project_root, get_config_root
import yaml_util
import logger


def configure_services():
    if 'services' not in settings:
        settings['services'] = {}

    for service, service_definition in env['services'].items():
        if service in settings['services']:
            if not settings['services'][service].get('active', True):
                del env['services'][service]


def configure_volumes():
    if 'volumes' not in settings:
        settings['volumes'] = {}

    for service, service_definition in env['services'].items():
        for i, volume in enumerate(service_definition['volumes']):
            opts = None

            if ':' in volume:
                volume, opts = volume.split(':')

            if opts is None:
                opts = get_volume_opts(volume)

            if volume in settings['volumes']:
                env['services'][service]['volumes'][i] = ':'.join([
                    get_volume_source(volume),
                    get_volume_target(volume),
                    opts
                ])
            else:
                logger.error("The volume " + volume + " is defined in the service " + service +
                             ", but no volume named " + volume + " has been configured.")


def configure_networking():
    env['networks'] = {
        'default': None
    }

    if 'remotes' not in settings:
        settings['remotes'] = {}

    all_remotes_active = {}
    extra_hosts = []
    aliases = {}

    for name, config in settings['remotes'].items():
        service = config.get('service', name)
        ip = config.get('ip', None)
        active = True

        if service not in all_remotes_active:
            all_remotes_active[service] = True

        if service in env['services'] and not config.get('active', False):
            active = False

        all_remotes_active[service] = all_remotes_active[service] and active

        if service not in aliases:
            aliases[service] = []

        if not active:
            aliases[service].append(name)
            continue

        if ip is None:
            logger.error("No IP address provided for the remote {0}.".format(name))

        extra_hosts.append(name + ':' + ip)

    services = env['services'].keys()

    for service in services:
        service_definition = env['services'][service]

        if service in all_remotes_active and all_remotes_active[service]:
            del env['services'][service]
            continue

        if 'networks' not in service_definition:
            service_definition['networks'] = {}

        if 'default' not in service_definition['networks']:
            service_definition['networks']['default'] = {}

        if 'aliases' not in service_definition['networks']['default']:
            service_definition['networks']['default']['aliases'] = aliases.get(service, [])

        if 'extra_hosts' not in service_definition:
            service_definition['extra_hosts'] = []

        for host in extra_hosts:
            service_definition['extra_hosts'].append(host)


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
        logger.error("Allay env.yml does not exist. Checked at " + env_config_path)

    env = yaml_util.load(env_config_path)


def write_docker_compose():
    for f in glob.glob(os.path.join(get_project_root(), 'docker-compose.y*')):
        os.remove(f)

    docker_compose_path = os.path.join(get_project_root(), 'docker-compose.yml')
    yaml_util.write(env, docker_compose_path)

env = {}
