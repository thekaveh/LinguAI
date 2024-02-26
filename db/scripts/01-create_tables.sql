-- Create an enum type for user types
CREATE TYPE user_type AS ENUM ('external', 'admin');

-- Create an enum type for skill levels
CREATE TYPE skill_level AS ENUM (
    'beginner', 
    'intermediate', 
    'advanced', 
    'expert', 
    'master'
);

-- Create the users table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(100) NOT NULL,
    user_type user_type NOT NULL
);

-- user_assessment table
CREATE TABLE user_assessment (
    assessment_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    assessment_date DATE,
    skill_level skill_level NOT NULL
);

-- user_performance table
CREATE TABLE user_performance (
    performance_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    performance_date DATE,
    accuracy FLOAT,
    completion_time INTERVAL
);

-- persona table
CREATE TABLE persona (
    persona_id SERIAL PRIMARY KEY,
    persona_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

-- user_persona table
CREATE TABLE user_persona (
    user_id INTEGER REFERENCES users(user_id),
    persona_id INTEGER REFERENCES persona(persona_id),
    PRIMARY KEY (user_id, persona_id)
);

-- Create an enum type for prompt types
CREATE TYPE prompt_type AS ENUM (
    'Instructional',
    'Feedback',
    'Reminder',
    'Engagement',
    'Error',
    'Confirmation',
    'Custom'
);

-- llm_prompt table - aka system prompt
CREATE TABLE llm_prompt (
    prompt_id SERIAL PRIMARY KEY,
    prompt_text TEXT NOT NULL,
    prompt_type prompt_type NOT NULL
);

-- user_prompt table
CREATE TABLE user_prompt (
    prompt_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    prompt_text TEXT NOT NULL,
    prompt_type prompt_type NOT NULL
);

-- Create a new database user
CREATE ROLE linguai_app WITH LOGIN PASSWORD 'linguai_app_pass';

-- Grant permissions to the newly created user
GRANT USAGE ON SCHEMA public TO linguai_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO linguai_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO linguai_app;