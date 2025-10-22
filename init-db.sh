#!/bin/sh
# Exit immediately if a command exits with a non-zero status.
set -e


echo "Creating databases: $POSTGRES_LEADS_DB, $POSTGRES_BUILDER_DB"

# to run the CREATE DATABASE commands for the other databases.
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE $POSTGRES_LEADS_DB;
    CREATE DATABASE $POSTGRES_BUILDER_DB;
EOSQL

echo "Databases created successfully."

