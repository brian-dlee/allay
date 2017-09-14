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
        if registry[k]['default_value'] is v and k in settings:
            continue

        if k.startswith('allay_volume_') and v:
            if 'volumes' not in cli_settings:
                cli_settings['volumes'] = {}

            vol_setting_type = k.split('_')[-1]
            vol_setting = v.split(':')

            if len(vol_setting) < 2:
                logger.error("Malformed volume option for type "
                             "\"{}\" (value={}).\n".format(vol_setting_type, v) +
                             "Volume options should be in the form of \"VOLUME_NAME:VALUE\"")

            if vol_setting[0] not in cli_settings['volumes']:
                cli_settings['volumes'][vol_setting[0]] = {}

            cli_settings['volumes'][vol_setting[0]][vol_setting_type] = vol_setting[1]
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

register('-Pr', '--allay-paths-project-root', dest='allay_paths_project_root',
         help='Configure the path in which to search for the Allay-enabled project.')
register('-Pc', '--allay-paths-config-root', dest='allay_paths_config_root',
         help='Configure the path in which to search for the Allay config files.')
register('-Pv', '--allay-paths-volumes-dir', dest='allay_paths_volumes_dir',
         help='Configure the path in where volumes are stored.')
register('-Lv', '--allay-list-volumes', dest='allay_list_volumes', action='store_true',
         help='List volume configuration.')
register('-Vo', '--allay-volume-opts', dest='allay_volume_opts',
         help='Adjust volume opts. Format = volume:opts.')
register('-Vs', '--allay-volume-source', dest='allay_volume_source',
         help='Adjust volume source. Format = volume:source.')
register('-Vt', '--allay-volume-target', dest='allay_volume_target',
         help='Adjust volume target. Format = volume:target.')
register('-Vd', '--allay-host-volumes-dir', dest='allay_host_volumes_dir',
         help='Adjust volume target. Format = volume:target.')
