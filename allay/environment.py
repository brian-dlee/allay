import glob
import os

from config import get_volumes_dir, get_project_root, get_config_root
import config
import yaml_util
import logger


def configure_services():
    config.s('services', {})

    for service, service_definition in env['services'].items():
        if service in config.g('services'):
            if not config.g('services.' + service + '.active', True):
                del env['services'][service]

            if config.g('services.' + service + '.port'):
                (src_port, dest_port) = \
                    config.g('services.' + service + '.port').split(':')
                new_setting = src_port + ':' + dest_port if dest_port else src_port

                if 'ports' in env['services'][service]:
                    for (i, port_setting) in enumerate(env['services'][service]['ports']):
                        if str(port_setting) == dest_port or str(port_setting).find(':' + dest_port) > -1:
                            env['services'][service]['ports'][i] = new_setting
                else:
                    env['services'][service]['ports'] = [new_setting]

        if 'ports' in env['services'][service]:
            for (i, port_setting) in enumerate(env['services'][service]['ports']):
                if str(port_setting).find(':') == -1:
                    logger.warn(
                        'Port {0} for the service {1} is '.format(port_setting, service) +
                        'has not been mapped to a host port.'
                    )


def configure_volumes():
    config.s('volumes', {})

    for service, service_definition in env['services'].items():
        for i, volume in enumerate(service_definition['volumes']):
            opts = None

            if ':' in volume:
                volume, opts = volume.split(':')

            if opts is None:
                opts = get_volume_opts(volume)

            if volume in config.g('volumes'):
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
        'default': {}
    }

    config.s('remotes', {})

    all_remotes_active = {}
    extra_hosts = []
    aliases = {}

    for name in config.g('remotes'):
        key = 'remotes.' + name
        service = config.g(key + '.service')
        ip = config.g(key + '.ip', None)
        active = True

        if service not in all_remotes_active:
            all_remotes_active[service] = True

        if service in env['services'] and not config.g(key + '.active', False):
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
    if not config.g('volumes.' + name, False):
        return None

    return config.g(
        'volumes.' + name + '.target',
        os.path.join('/volumes', name)
    )


def get_volume_source(name):
    if not config.g('volumes.' + name, False):
        return None

    return config.g(
        'volumes.' + name + '.source',
        os.path.join(get_volumes_dir(), name)
    )


def get_volume_opts(name):
    if not config.g('volumes.' + name, False):
        return None

    return config.g('volumes.' + name + '.opts', 'rw')


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
