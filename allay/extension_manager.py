import os
import pip
import re
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


def check_requirements():
    packages = {}
    missing = []

    for package in pip.get_installed_distributions():
        packages[package.project_name] = package.version

    for (name, version, source) in _requirements:
        if name not in packages:
            missing.append((name, version, source))
            continue

        if not version or not packages[name]:
            continue

        op_search = re.search('^([<>=]+)(.+)', version)
        comparison = '__eq__'

        if op_search:
            op = op_search.group(1)
            version = op_search.group(2)

            if op == '>':
                comparison = '__gt__'
            elif op == '>=':
                comparison = '__ge__'
            elif op == '<=':
                comparison = '__le__'
            elif op == '<':
                comparison = '__lt__'

        if not getattr(packages[name], comparison)(version):
            missing.append((name, version, source))

    if len(missing) == 0:
        return True

    logger.error(
        'The following packages are not installed.\nInstall the extension requirements and rerun allay.\n' +
        '\n'.join([
            n + (v if v else '') + (': pip install ' + s if s else '') for (n, v, s) in missing
        ]) + '\n'
    )


def load_extension():
    global _extension

    sys.path.append(get_config_root())

    import extension
    _extension = extension


def require(name, version=None, source=None):
    name_version = name

    if version:
        name_version += version

    if source:
        source += '#egg=' + name

    _requirements.append((name, version, source))


def run_extension():
    if config.settings.get('allay_list_extension_requirements', False):
        logger.log('Extension requires:\n  ' + '\n  '.join(
            [n + (v if v else '') + (' ({0})'.format(s) if s else '') for (n, v, s) in _requirements]))
        logger.log('pip install', *[s if s else (n + (v if v else '')) for (n, v, s) in _requirements])
        exit()

    return check_requirements() and _extension.main()

_extension = None
_requirements = []
