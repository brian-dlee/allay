import os
import sys

import allay.paths

_extension = None


def extension_is_loaded():
    return _extension is not None


def check_for_extension():
    found = False

    if os.path.exists(os.path.join(allay.paths.paths['allay_config_root'], 'extension.py')):
        allay.paths.paths['extension_path'] = os.path.join(allay.paths.paths['allay_config_root'], 'extension.py')
        found = True

    if os.path.exists(os.path.join(allay.paths.paths['allay_config_root'], 'extension', '__init__.py')):
        allay.paths.paths['extension_path'] = os.path.join(allay.paths.paths['allay_config_root'], 'extension', '__init__.py')
        found = True

    if found:
        allay.logger.log('Found extension at {0}'.format(allay.paths.paths['extension_path']))

    return found


def load_extension():
    global _extension

    sys.path.append(allay.paths.paths['allay_config_root'])

    import extension
    _extension = extension


def run_extension():
    return _extension.main()
