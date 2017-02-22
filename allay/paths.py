import os
import re

paths = {}


def initialize():
    if 'project_root' not in paths:
        paths['project_root'] = os.path.abspath(os.getcwd())

    paths['allay_config_root'] = os.path.join(paths['project_root'], '.allay')
    paths['vcs_root'] = None

    path = paths['project_root']

    while not os.path.exists(os.path.join(path, '.git')) and not re.match('^((\w:)?\\\\|/)$', path):
        path = os.path.dirname(path)

    if os.path.exists(os.path.join(path, '.git')):
        paths['vcs_root'] = os.path.join(path, '.git')
