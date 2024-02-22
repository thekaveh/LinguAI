-- Create a new database user
CREATE ROLE cs5934_app_user WITH LOGIN PASSWORD 'cs5934_app_user_password';

-- Create a new schema
CREATE SCHEMA cs5934_app_schema;

-- Grant privileges to the user for the schema
-- GRANT USAGE ON SCHEMA cs5934_app_schema TO cs5934_app_user;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA cs5934_app_schema TO cs5934_app_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA cs5934_app_schema TO cs5934_app_user;



-- Grant privileges to create, modify tables, select tables
-- GRANT CREATE, CONNECT ON DATABASE cs5934_postgresqldb TO cs5934_app_user;
-- GRANT USAGE ON SCHEMA public TO cs5934_app_user;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public
   --  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO cs5934_app_user;

-- Deny delete of records and tables
-- REVOKE DELETE ON ALL TABLES IN SCHEMA public FROM cs5934_app_user;
-- REVOKE TRUNCATE ON ALL TABLES IN SCHEMA public FROM cs5934_app_user;

-- Grant for insert, modify, select
-- GRANT INSERT, UPDATE, SELECT ON ALL TABLES IN SCHEMA public TO cs5934_app_user;

-- Delete can only be done at db admin level
-- No need to explicitly deny delete, as it's already revoked above