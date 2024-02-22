#!/bin/bash

# Function to check if schema and tables exist
check_schema_and_tables_exist() {
    # Perform a query to check if the schema and tables exist
    # Example query: psql -U postgres -d your_database_name -c "\dt cs5934_app_user.*"
    # You may need to adjust the query based on your schema and database setup
    # If the schema or tables exist, return 0 (success); otherwise, return 1 (failure)
    psql -U postgres -d cs5934_postgresqldb -c "\dt cs5934_app_user.*" >/dev/null 2>&1
    return $?
}

# Main entrypoint logic
if ! check_schema_and_tables_exist; then
    # Execute schema creation, table creation, and data insertion scripts
    psql -U postgres -d cs5934_postgresqldb -f /docker-entrypoint-initdb.d/create_schema.sql
    psql -U postgres -d cs5934_postgresqldb -f /docker-entrypoint-initdb.d/create_tables.sql
    psql -U postgres -d cs5934_postgresqldb -f /docker-entrypoint-initdb.d/insert_initial_data.sql
fi

# Start the PostgreSQL service
exec "$@"