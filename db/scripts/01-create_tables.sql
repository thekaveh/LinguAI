-- Create an enum type for user types
CREATE TYPE user_type AS ENUM ('external', 'admin');

-- Create an enum type for skill levels
CREATE TYPE skill_level_type AS ENUM (
    'beginner', 
    'intermediate', 
    'advanced', 
    'expert', 
    'master'
);

CREATE TYPE language_type AS ENUM (
    'English',  'Mandarin', 'Spanish', 'German', 'French'
);

-- Create an enum type for prompt types
CREATE TYPE prompt_type AS ENUM (
    'instructional',
    'feedback',
    'reminder',
    'engagement',
    'error',
    'confirmation',
    'custom'
);

-- Create an enum type for topics
CREATE TYPE topic_type AS ENUM (
    'sports', 'nutrition', 'movies', 'education','finance','technology','history', 'business',  'culture','writing', 'reading', 'fashion', 
    'politics','art','music', 'travel','math', 'science','health & wellness','pronounciation', 'vocabulary', 'grammer', 'speaking'
);

-- Create an enum type for content preferences
CREATE TYPE content_preference_type AS ENUM (
    'story', 'dialogue', 'fake article', 'tutorial', 'poetry', 'news report', 'biography', 'essay'
);

CREATE TABLE users (
    -- User identification
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,

    -- Authentication
    password_hash VARCHAR(100) NOT NULL,

    -- Personal information
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),

    -- Contact information
    mobile_phone VARCHAR(20),
    landline_phone VARCHAR(20),
    contact_preference VARCHAR(50), 

    -- User settings and preferences
    user_type VARCHAR(100) NOT NULL, 
    base_language VARCHAR(100), 
    learning_languages VARCHAR[] 
);

-- address table
CREATE TABLE addresses (
    address_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    address_type VARCHAR(50),
    street VARCHAR(255),
    door_number VARCHAR(50),
    city VARCHAR(100),
    state VARCHAR(100),
    zip VARCHAR(20),
    country VARCHAR(100),
    CONSTRAINT fk_user
        FOREIGN KEY(user_id) 
        REFERENCES users(user_id)
        ON DELETE CASCADE
);

-- user_assessment table
CREATE TABLE user_assessment (
    assessment_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    assessment_date DATE,
    skill_level_type VARCHAR(100) NOT NULL
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

-- llm_prompt table - aka system prompt
CREATE TABLE llm_prompt (
    prompt_id SERIAL PRIMARY KEY,
    prompt_text TEXT NOT NULL,
    prompt_type VARCHAR(100) NOT NULL -- Changed to VARCHAR
);

-- user_prompt table
CREATE TABLE user_prompt (
    prompt_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    prompt_text TEXT NOT NULL,
    prompt_type VARCHAR(100) NOT NULL -- Changed to VARCHAR
);

-- Create the topics table
CREATE TABLE topics (
    topic_id SERIAL PRIMARY KEY,
    topic_name VARCHAR(100) UNIQUE NOT NULL
);

-- Create a junction table for users and their topics of interest
CREATE TABLE user_topics (
    user_id INT NOT NULL,
    topic_id INT NOT NULL,
    PRIMARY KEY (user_id, topic_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id)
);

-- Create the achievements table
CREATE TABLE achievements (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);


--GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE achievements TO linguai_app;


-- Create a new database user
CREATE ROLE linguai_app WITH LOGIN PASSWORD 'linguai_app_pass';

-- Grant permissions to the newly created user
GRANT USAGE ON SCHEMA public TO linguai_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO linguai_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO linguai_app;