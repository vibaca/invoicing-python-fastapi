#!/bin/bash
set -e

# Create development and test databases if they don't exist.
# This script is executed by the official Postgres image during initialisation
# as the `postgres` user, so no password is required.

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
  CREATE DATABASE invoicing_dev;
  CREATE DATABASE invoicing_test;
EOSQL
