import os
import re


def load(project_root=None):
    paths = {}

    if project_root:
        paths['allay_paths_project_root'] = project_root

    paths['allay_paths_vcs_root'] = None

    path = paths['allay_paths_project_root'] if project_root else os.path.abspath(os.getcwd())

    while not os.path.exists(os.path.join(path, '.git')) and not re.match('^((\w:)?\\\\|/)$', path):
        path = os.path.dirname(path)

    if os.path.exists(os.path.join(path, '.git')):
        paths['allay_paths_vcs_root'] = os.path.join(path, '.git')

    if not project_root:
        if paths['allay_paths_vcs_root']:
            paths['allay_paths_project_root'] = os.path.dirname(paths['allay_paths_vcs_root'])
        else:
            paths['allay_paths_project_root'] = os.path.abspath(os.getcwd())

    paths['allay_paths_config_root'] = os.path.join(paths['allay_paths_project_root'], '.allay')
    paths['allay_paths_volumes_dir'] = os.path.join(paths['allay_paths_project_root'], 'Docker', 'volumes')

    return paths
