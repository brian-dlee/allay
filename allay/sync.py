import datetime
import os
import re
import shutil

from allay.config import settings
from allay.environment import get_volume_source
from allay import logger
import magnet

sftp_downloader = None


def check_database_update_connectivity():
    global sftp_downloader

    try:
        sftp_downloader.initialize_client()
    except Exception as e:
        # :todo add check for exception corresponding with lack of permissions
        logger.error(
            '\nCannot connect to remote database to update schemas.\n',
            'Attempted to connect over SSH to {0} as user {1}.\n'.format(
                settings['database_synchronize_settings']['host'],
                settings['database_synchronize_settings']['user']) +
            '\nERROR: {0}'.format(e))

    return True


def check_local_schema_files(schema_dir, schemas, max_age_in_seconds):
    schema_files_to_update = set()

    for schema_name in schemas:
        schema_file_name = schema_name + '.sql.gz'
        schema_file_path = os.path.join(schema_dir, schema_file_name)

        if not os.path.exists(schema_file_path):
            logger.warn(
                " - No database schema exists for the database "
                "`{0}`.".format(schema_name)
            )
            schema_files_to_update.add(schema_file_path)
            continue

        if file_is_older_than(schema_file_path, max_age_in_seconds):
            logger.warn(
                ' - Found old schema for the database '
                '`{0}`. Queuing update.'.format(schema_name)
            )
            schema_files_to_update.add(schema_file_path)

    return list(schema_files_to_update)


def file_is_older_than(path, age_in_seconds):
    file_mtime = int(os.path.getmtime(path))
    timestamp = datetime.datetime.fromtimestamp(
        file_mtime + int(age_in_seconds)
    )

    return timestamp < datetime.datetime.now()


def initialize_sftp_downloader():
    global sftp_downloader

    private_key_file = os.path.expanduser(os.path.join('~', '.ssh', 'id_rsa'))
    host = settings['database_synchronize_settings']['host']
    user = settings['database_synchronize_settings']['user']
    conn_string = user + '@' + host

    try:
        sftp_downloader = magnet.SFTPDownloader(
            user, host, private_key_file,
            callback=magnet.SFTPDownloader.display_percent_complete)
    except Exception as e:
        logger.warn(
            'Failed to initialize SFTPDownloader '
            'to ' + conn_string + '.\n\n'

            'Try `ssh ' + conn_string + '` from the command line to ensure '
            'this connection is configured.\n\n'

            'If you\'ve never connected to this server via SSH before then '
            'you may just need to connect manually to accept the remote '
            'server\'s identity.\n\n'

            'Otherwise, you may need your public key installed on the server. '
            'If the user account "' + user + '" has a password, then you can '
            'use a tool like `ssh-copy-id ' + conn_string + '` to add '
            'your public key to the server. If that is not an option, you '
            'need to ask someone with admin level access to ' + host + ' to '
            'install your public key for you. Your public key trying to be '
            'used for authentication is at ' + private_key_file + '. The '
            'contents of this file needs to be appended to '
            '.ssh/authorized_keys in the "' + user + '" user\'s home '
            'directory.\n'
        )
        logger.error('ERROR: {0}'.format(e))


def has_all_settings_defined():
    return (
        'database_synchronize_settings' in settings and
        'host' in settings['database_synchronize_settings'] and
        'user' in settings['database_synchronize_settings'] and
        'schemas' in settings['database_synchronize_settings'] and
        'schema-volume' in settings['database_synchronize_settings'] and
        'database-volume' in settings['database_synchronize_settings']
    )


def get_schema_list():
    schema_string = settings['database_synchronize_settings']['schemas']

    return [
        s.strip() for s in schema_string.split(',')
    ]


def check_and_get_volume_settings():
    def volume_error_string(setting_name, value):
        return (
            "The volume specified in the database synchronization settings "
            "for " + setting_name + " does not have a valid value. "
            "The value is " + value + " and no volume named " + value + " is "
            "defined in the volume settings."
        )

    sync_settings = settings['database_synchronize_settings']
    result = {}

    for s in ('schema-volume', 'database-volume'):
        parts = sync_settings[s].split(':')
        volume = parts[0]

        if volume not in settings['volumes']:
            logger.error(volume_error_string(s, sync_settings[s]))

        path = get_volume_source(volume)

        if len(parts) > 1:
            path = os.path.join(path, parts[1])

        result[s.replace('-volume', '')] = {
            "source_path": path,
            "volume": volume
        }

    return result


def sync_is_enabled():
    return has_all_settings_defined()


def sync():
    initialize_sftp_downloader()

    volume_settings = check_and_get_volume_settings()
    schemas = get_schema_list()

    data_dir = volume_settings['database']['source_path']
    schema_dir = volume_settings['schema']['source_path']

    max_age_in_days = int(settings['database_synchronize_settings'].get(
        'schema_file_max_age',
        1
    ))

    max_age_in_seconds = max_age_in_days * 24 * 60 * 60

    logger.log("Checking local schema files.")

    schema_files_to_update = check_local_schema_files(
        schema_dir,
        schemas,
        max_age_in_seconds
    )

    if len(schema_files_to_update) > 0:
        if not check_database_update_connectivity():
            return False

        schemas_updated = update_schema_files(
            schema_dir,
            schema_files_to_update
        )

        if schemas_updated > 0:
            if os.path.exists(data_dir):
                shutil.rmtree(data_dir)

        return True
    else:
        logger.log(' - All database schemas are up to date.')
        return True


def update_schema_files(schema_dir, schema_file_to_update):
    global sftp_downloader

    if not os.path.exists(schema_dir):
        os.makedirs(schema_dir)

    logger.log("Downloading missing/outdated schemas from remote system.")

    schemas_updated = 0

    for number, schema_file_path in enumerate(schema_file_to_update):
        schema_name_search = re.search(
            '([a-z_]+).sql(.gz)?',
            os.path.basename(schema_file_path)
        )

        if not schema_name_search:
            logger.warn(
                "Failed to parse database name from "
                "{0}. Skipping.\n".format(schema_file_path)
            )
            continue

        schema_name = schema_name_search.group(1)

        logger.log(
            "[{0}/{1}] Downloading database schema {2} from server.".format(
                number + 1,
                len(schema_file_to_update),
                schema_name
            )
        )

        try:
            sftp_downloader.get_file(
                'database-schemas/{0}.sql.gz'.format(schema_name),
                schema_file_path
            )
        except Exception as e:
            # :todo Add appropriate error handling
            logger.warn(
                "\rFailed to downloaded {0} database schema.".format(
                    schema_name
                )
            )
            logger.warn(str(e))
        else:
            logger.log(
                "\rSuccessfully downloaded {0} database schema to {1}.".format(
                    schema_name,
                    schema_file_path
                )
            )
            schemas_updated += 1

    return schemas_updated
