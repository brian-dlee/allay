import argparse
import re
import sys

from config import settings
import extension_manager
import logger


def split_args():
    allay = []
    extension = []

    is_allay = True

    for arg in sys.argv[1:]:
        if arg.startswith('--allay-') or re.search('^-[A-Z]', arg):
            allay.append(arg)
            is_allay = True
        elif not arg.startswith('-'):
            if is_allay:
                allay.append(arg)
            else:
                extension.append(arg)
        else:
            extension.append(arg)
            is_allay = False

    return allay, extension


def parse_allay_args():
    return command_parser.parse_args(split_args()[0])


def parse_extension_args():
    return command_parser.parse_args(split_args()[1])


def get_cli_settings():
    global registry

    cli_args = parse_allay_args()

    cli_settings = {}

    for k, v in cli_args.__dict__.items():
        if (registry[k]['default_value'] is v or v is None) and k in settings:
            continue

        key_parts = k.split('_')

        if key_parts[0] == 'allay' and key_parts[1] in ('remote', 'volume', 'service') and v:
            for individual_value in v:
                setting_key = key_parts[1] + 's'

                if setting_key not in cli_settings:
                    cli_settings[setting_key] = {}

                setting_type = k.split('_')[-1]

                if isinstance(individual_value, str):
                    setting_value = individual_value.split(':')

                    if len(setting_value) < 2:
                        logger.error("Malformed allay option for type "
                                     "\"{}\" (value={}).\n".format(k, individual_value) +
                                     "Volume options should be in the form of \"NAME:VALUE\"")

                    if setting_value[0] not in cli_settings[setting_key]:
                        cli_settings[setting_key][setting_value[0]] = {}

                    normalized_value = setting_value[1]

                    if setting_value[1].lower() in ('no', 'false', 'off'):
                        normalized_value = False
                    elif setting_value[1].lower() in ('yes', 'true', 'on'):
                        normalized_value = True

                    cli_settings[setting_key][setting_value[0]][setting_type] = normalized_value
        else:
            cli_settings[k] = v

    return cli_settings


def register(*args, **kwargs):
    command_parser_args = dict()
    allay_args = dict()

    for key, value in kwargs.items():
        if key.startswith('allay_'):
            allay_args[key] = value
        else:
            command_parser_args[key] = value

    if 'dest' in command_parser_args:
        if 'help' in command_parser_args:
            command_parser_args['help'] += ' [Config file key: ' + command_parser_args['dest'] + ']'
        else:
            command_parser_args['help'] = ' [Config file key: ' + command_parser_args['dest'] + ']'

    arg = command_parser.add_argument(*args, **command_parser_args)
    registry[arg.dest] = allay_args
    registry[arg.dest]['default_value'] = arg.default


def run():
    global registry

    if extension_manager.extension_is_loaded():
        if not extension_manager.run_extension():
            logger.error("The extension failed to run.")


def validate():
    for command in registry.keys():
        if 'allay_validation' in registry[command]:
            if isinstance(registry[command]['allay_validation'], dict):
                if ('requires_validation' in registry[command]['allay_validation'] and
                        not registry[command]['allay_validation']['requires_validation'](settings)):

                    continue

                if ('is_valid' in registry[command]['allay_validation'] and
                        not registry[command]['allay_validation']['is_valid'](settings)):

                    if 'invalid_message' in registry[command]['allay_validation']:
                        logger.warn('Command validation failed for "{0}"'.format(command))
                        logger.error(registry[command]['allay_validation']['invalid_message'], exit_code=1)

                    logger.error('Command validation failed for "{0}"'.format(command))

            elif not registry[command]['allay_validation']():
                logger.error('Command validation failed for "{0}"'.format(command))

command_parser = argparse.ArgumentParser()
registry = {}

register('-Ri', '--allay-remote-ip', nargs='*', dest='allay_remote_ip',
         help='Configure a remote alternative for a service. Format = remote:(ip or hostname)')
register('-Ra', '--allay-remote-active', nargs='*', dest='allay_remote_active',
         help='Turn on or off a given remote. Format = remote:(yes or no)')
register('-Rs', '--allay-remote-service', nargs='*', dest='allay_remote_service',
         help='Indicates which service this remote replaces. Format = remote:service')
register('-Sa', '--allay-service-active', nargs='*', dest='allay_service_active',
         help='Turn on or off a given service. Format = service:(yes or no)')
register('-Pr', '--allay-paths-project-root', dest='allay_paths_project_root',
         help='Configure the path in which to search for the Allay-enabled project.')
register('-Pc', '--allay-paths-config-root', dest='allay_paths_config_root',
         help='Configure the path in which to search for the Allay config files.')
register('-Pv', '--allay-paths-volumes-dir', dest='allay_paths_volumes_dir',
         help='Configure the path in where volumes are stored.')
register('-Le', '--allay-list-extension-requirements', dest='allay_list_extension_requirements', action='store_true',
         help='List the extensions required packages.')
register('-Lv', '--allay-list-volumes', dest='allay_list_volumes', action='store_true',
         help='List volume configuration.')
register('-Lc', '--allay-list-configuration', dest='allay_list_configuration', action='store_true',
         help='List full option configuration.')
register('-Vo', '--allay-volume-opts', nargs='*', dest='allay_volume_opts',
         help='Adjust volume opts. Format = volume:opts.')
register('-Vs', '--allay-volume-source', nargs='*', dest='allay_volume_source',
         help='Adjust volume source. Format = volume:source.')
register('-Vt', '--allay-volume-target', nargs='*', dest='allay_volume_target',
         help='Adjust volume target. Format = volume:target.')
