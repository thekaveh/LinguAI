-- Connect to the database
--\c cs5934_postgresqldb cs5934_app_user

-- Create tables in the cs5934_app_user schema

-- Create an enum type for user types
CREATE TYPE cs5934_app_schema.UserType AS ENUM ('external', 'admin');

-- Create an enum type for skill levels
CREATE TYPE cs5934_app_schema.SkillLevel AS ENUM ('beginner', 
    'intermediate', 
    'advanced', 
    'expert', 
    'master'
);


-- Create the Users table
CREATE TABLE cs5934_app_schema.Users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(100) NOT NULL,
    user_type cs5934_app_schema.UserType NOT NULL  -- Enum column for user type
);

-- UserAssessment table
CREATE TABLE cs5934_app_schema.UserAssessment (
    assessment_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES cs5934_app_schema.Users(user_id),
    assessment_date DATE,
    skill_level cs5934_app_schema.SkillLevel NOT NULL  -- Enum column for skill level
);

-- UserPerformance table
CREATE TABLE cs5934_app_schema.UserPerformance (
    performance_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES cs5934_app_schema.Users(user_id),
    performance_date DATE,
    accuracy FLOAT,
    completion_time INTERVAL
);

-- Persona table
CREATE TABLE cs5934_app_schema.Persona (
    persona_id SERIAL PRIMARY KEY,
    persona_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

-- UserPersona table
CREATE TABLE cs5934_app_schema.UserPersona (
    user_id INTEGER REFERENCES cs5934_app_schema.Users(user_id),
    persona_id INTEGER REFERENCES cs5934_app_schema.Persona(persona_id),
    PRIMARY KEY (user_id, persona_id)
);
-- Create an enum type for prompt types
CREATE TYPE cs5934_app_schema.PromptType AS ENUM (
    'Instructional',
    'Feedback',
    'Reminder',
    'Engagement',
    'Error',
    'Confirmation',
    'Custom'
);

-- LLMPrompt table - aka system prompt
CREATE TABLE cs5934_app_schema.LLMPrompt (
    prompt_id SERIAL PRIMARY KEY,
    prompt_text TEXT NOT NULL,
    prompt_type cs5934_app_schema.PromptType NOT NULL
);

-- UserPrompt table
CREATE TABLE cs5934_app_schema.UserPrompt (
    prompt_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES cs5934_app_schema.Users(user_id),
    prompt_text TEXT NOT NULL,
    prompt_type cs5934_app_schema.PromptType NOT NULL
);

GRANT USAGE ON SCHEMA cs5934_app_schema TO cs5934_app_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA cs5934_app_schema TO cs5934_app_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA cs5934_app_schema TO cs5934_app_user;

-- Grant privileges to create, modify tables, select tables
-- GRANT CREATE, CONNECT ON DATABASE cs5934_postgresqldb TO cs5934_app_user;
-- GRANT USAGE ON SCHEMA public TO cs5934_app_user;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public
   -- GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO cs5934_app_user;

-- Deny delete of records and tables
-- REVOKE DELETE ON ALL TABLES IN SCHEMA public FROM cs5934_app_user;
-- REVOKE TRUNCATE ON ALL TABLES IN SCHEMA public FROM cs5934_app_user;

-- Grant for insert, modify, select
-- GRANT INSERT, UPDATE, SELECT ON ALL TABLES IN SCHEMA public TO cs5934_app_user;
