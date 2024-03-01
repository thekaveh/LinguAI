#!/bin/bash

# Navigate to the correct directory (adjust as necessary)
cd /path/to/your/db

# Generate the dump
docker exec -i db pg_dump -U linguai_db_user -d linguai_db --no-owner > ./snapshot/linguai_db_ss.sql

# Wait a moment to ensure the file write completes
sleep 5

# Read the dump file, remove unwanted line, add the CREATE ROLE statement, and save to a new file
sed '/failed to get console mode for stdout: The handle is invalid./d' ./snapshot/linguai_db_ss.sql | sed '1s/^/CREATE ROLE linguai_app WITH LOGIN PASSWORD '\''linguai_app_pass'\'';\n/' > ./snapshot/linguai_db_ss_utf8.sql

# Remove the original SQL file
rm ./snapshot/linguai_db_ss.sql