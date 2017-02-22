
import os
import sys

import allay.commands
import allay.env
import allay.extension_manager
import allay.logger
import allay.paths
import allay.settings


def run():
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        if not os.path.exists(sys.argv[1]):
            allay.logger.error('Project root specified ({0}) does not exist'.format(sys.argv[1]), exit_code=1)
        allay.paths.paths['project_root'] = os.path.abspath(sys.argv[1])
        sys.argv = sys.argv[0:1] + sys.argv[2:]

    allay.commands.initialize()
    allay.paths.initialize()

    allay.env.load_config()
    allay.settings.load_config()

    if allay.extension_manager.check_for_extension():
        allay.extension_manager.load_extension()

    allay.commands.parse_commands_from_cli()

    allay.settings.import_settings(allay.commands.cli_settings)

    allay.commands.validate()
    allay.commands.run()

    allay.settings.explain()

    allay.env.write_docker_compose()

    print "Successully updated docker-compose.yaml"
    print "The environment is ready. Run docker-compose up to use it."
