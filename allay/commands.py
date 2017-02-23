import argparse
import sys

import allay.extension_manager
import allay.logger
from allay.settings import settings as allay_settings

command_parser = None
cli_settings = {}
registry = {}


def parse_commands_from_cli():
    global cli_settings

    cli_settings = command_parser.parse_args(sys.argv[1:])


def initialize():
    global command_parser

    command_parser = argparse.ArgumentParser()
    # command_parser.add_argument('-P', '--allay-project-path', dest='allay_project_path',
    #                             help='Configure the path in which to search for the Allay-enabled project.')


def register(*args, **kwargs):
    global command_parser

    command_parser_args = dict()
    allay_args = dict()

    for key, value in kwargs.items():
        if key.startswith('allay_'):
            allay_args[key] = value
        else:
            command_parser_args[key] = value

    arg = command_parser.add_argument(*args, **command_parser_args)
    registry[arg.dest] = allay_args
    registry[arg.dest]['default_value'] = arg.default


def run():
    global registry

    if allay.extension_manager.extension_is_loaded():
        if not allay.extension_manager.run_extension():
            allay.logger.error("The extension failed to run.")


def validate():
    global registry

    for command in registry.keys():
        if 'allay_validation' in registry[command]:
            if isinstance(registry[command]['allay_validation'], dict):
                if ('requires_validation' in registry[command]['allay_validation'] and
                        not registry[command]['allay_validation']['requires_validation'](allay_settings)):

                    continue

                if ('is_valid' in registry[command]['allay_validation'] and
                        not registry[command]['allay_validation']['is_valid'](allay_settings)):

                    if 'invalid_message' in registry[command]['allay_validation']:
                        allay.logger.warn('Command validation failed for "{0}"'.format(command))
                        allay.logger.error(registry[command]['allay_validation']['invalid_message'], exit_code=1)

                    allay.logger.error('Command validation failed for "{0}"'.format(command))

            elif not registry[command]['allay_validation']():
                allay.logger.error('Command validation failed for "{0}"'.format(command))
