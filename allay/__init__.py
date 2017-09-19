from dict_utils import deep_merge
from yaml_util import explain
from environment import env
from config import settings
import commands
import environment
import extension_manager
import logger
import paths
import config


def run():
    cli_args = commands.parse_allay_args()
    deep_merge(settings, paths.load(cli_args.allay_paths_project_root))

    environment.load_files()
    config.load_files()

    if extension_manager.check_for_extension():
        extension_manager.load_extension()
        commands.parse_extension_args()

    # Since extensions can register arguments we need to reprocess cli args
    deep_merge(settings, commands.get_cli_settings())

    environment.configure_services()
    environment.configure_volumes()
    environment.configure_networking()

    if settings.get('allay_list_volumes', False):
        explain('Volume Configuration', settings['volumes'])
        exit()

    if settings.get('allay_list_configuration', False):
        explain('Configuration', settings)
        exit()

    commands.validate()
    commands.run()

    environment.write_docker_compose()

    logger.log("Successully updated docker-compose.yml")
    logger.log("The environment is ready. Run docker-compose up to use it.")
