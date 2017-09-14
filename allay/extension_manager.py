import os
import sys

from config import get_config_root
import logger
import config


def extension_is_loaded():
    return _extension is not None


def check_for_extension():
    found = False
    config_root = get_config_root()

    if os.path.exists(os.path.join(config_root, 'extension.py')):
        config.settings['allay_paths_extension'] = os.path.join(config_root, 'extension.py')
        found = True

    if os.path.exists(os.path.join(config_root, 'extension', '__init__.py')):
        config.settings['allay_paths_extension'] = os.path.join(config_root, 'extension', '__init__.py')
        found = True

    if found:
        logger.log('Found extension at {0}'.format(config.settings['allay_paths_extension']))

    return found


def load_extension():
    global _extension

    sys.path.append(get_config_root())

    import extension
    _extension = extension


def run_extension():
    return _extension.main()

_extension = None
