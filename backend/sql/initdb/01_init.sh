#!/bin/bash
# Creates the test database alongside the default clear_case database.
# Runs automatically when the postgres container is first initialised.
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE clear_case_test;
EOSQL
