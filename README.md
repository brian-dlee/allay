# Allay - Alleviate environmental pain

# Installation

**Requirements**
- Python 2 (2.7 or greater) - https://www.python.org/downloads/
- pip - https://pip.pypa.io/en/stable/installing/ or using brew (MacOS Users) `brew install python` - https://brew.sh/
- Docker Toolbox or Docker for Windows/Mac - https://docs.docker.com/engine/installation/

> *Prerequisite*

> Install magnet: `pip install git+https://github.com/brian-dlee/magnet.git#egg=magnet`

```bash
pip install git+https://github.com/brian-dlee/allay.git#egg=allay
```

# Configuring database synchronization

1. Ensure you have a volume configured to store database files and database schema files in `volumes.yml`.
2. In `settings.yml`, add a section for `dbsync`. All of the settings specified below are required.
```yml
dbsync:
  user: allay
  host: mydbhost.com
  schemas: schema1,schema2
  schemas-volume: VOLUME_NAME[:OPTIONAL_PATH]
  database-volume: VOLUME_NAME[:OPTIONAL_PATH]
```
  * Optional properties include:
    * (integer) `schema_file_max_age` Determines when a schema is deemed old (in days)
    * (string)  `remote_path` Determines where to look for database schema files (default is `$HOME/database-schemas`)
3. Configure your server
  * Create a user account to use for database synchronization
  * Configure user to write database SQL dumps to your desired location. Default is `$HOME/database-schemas`.
  * Schema files should be named according the schema they represent
  * A schema file for `schema1` will be stored at `$HOME/database-schemas/schema1.sql.gz`
  * Setup key access for your user to access the new user account. Currently, this only supports the use of the default key at `~/.ssh/id_rsa.pub`

All set! The next time allay runs it will try to connect to your host using the configured user account, run a comparison between the files currently found in the schemas-volume director and the corresponding files on the server and download them over SSH.

Next, you should ensure your database container is equipped to ingest these schema files on initialization.

**WARNING: When allay downloads new schemas is deletes the contents of the database data directory to force the ingestion of the newly downloaded files.**
