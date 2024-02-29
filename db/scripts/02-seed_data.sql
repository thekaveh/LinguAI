-- Insert sample data into Users table
INSERT INTO users (
    username, 
    email, 
    password_hash, 
    user_type, 
    first_name, 
    last_name, 
    middle_name, 
    mobile_phone, 
    landline_phone, 
    contact_preference, 
    base_language, 
    learning_languages
)
VALUES
    ('ironman123', 'ironman@example.com', 'password_hash_ironman', 'external', 'Tony', 'Stark', '', '123-456-7890', '', 'email', 'English', '{}'),
    ('captainamerica123', 'captainamerica@example.com', 'password_hash_captainamerica', 'external', 'Steve', 'Rogers', '', '234-567-8901', '', 'mobile_phone', 'English', '{}'),
    ('blackwidow123', 'blackwidow@example.com', 'password_hash_blackwidow', 'external', 'Natasha', 'Romanoff', '', '345-678-9012', '', 'email', 'Russian', '{}'),
    ('thor123', 'thor@example.com', 'password_hash_thor', 'external', 'Thor', 'Odinson', '', '456-789-0123', '', 'email', 'Asgardian', '{}'),
    ('hulk123', 'hulk@example.com', 'password_hash_hulk', 'external', 'Bruce', 'Banner', '', '567-890-1234', '', 'mobile_phone', 'English', '{}');

-- Insert sample data into Addresses table
INSERT INTO addresses (user_id, address_type, street, door_number, city, state, zip, country)
VALUES
    (1, 'shipping', '10880 Malibu Point', '10880', 'Malibu', 'California', '90265', 'USA'),
    (1, 'billing', '200 Park Avenue', '200', 'New York', 'New York', '10166', 'USA'),
    (2, 'shipping', '890 Fifth Avenue', '890', 'Manhattan', 'New York', '10021', 'USA'),
    (3, 'shipping', 'Red Room Academy', '', 'Volgograd', '', '', 'Russia'),
    (4, 'shipping', 'Asgard Palace', '', 'Asgard', '', '', 'Asgard'),
    (5, 'billing', '177A Bleecker Street', '', 'New York', 'New York', '10012', 'USA');


-- Insert sample data into UserAssessment table
INSERT INTO user_assessment (user_id, assessment_date, skill_level_type)
VALUES
    (1, '2023-01-01', 'expert'),
    (2, '2023-01-05', 'advanced'),
    (3, '2023-01-10', 'intermediate'),
    (4, '2023-01-15', 'beginner'),
    (5, '2023-01-20', 'master');

-- Insert sample data into Persona table
INSERT INTO persona (persona_name, description)
VALUES
    ('Iron Man', 'Genius, billionaire, playboy, philanthropist.'),
    ('Captain America', 'Super-soldier and leader of the Avengers.'),
    ('Black Widow', 'Master spy and former assassin.'),
    ('Thor', 'God of Thunder and prince of Asgard.'),
    ('Hulk', 'Gamma-irradiated scientist with immense strength.');

-- Insert sample data into UserPersona table
INSERT INTO user_persona (user_id, persona_id)
VALUES
    (1, 1),  -- Iron Man
    (2, 2),  -- Captain America
    (3, 3),  -- Black Widow
    (4, 4),  -- Thor
    (5, 5);  -- Hulk

-- Insert sample data into LLMPrompt table (System Prompts)
INSERT INTO llm_prompt (prompt_text, prompt_type)
VALUES
    ('Welcome to the language learning assistance app!', 'Instructional'),
    ('Congratulations! You completed today''s lesson.', 'Feedback'),
    ('Don''t forget to review your vocabulary.', 'Reminder'),
    ('Earn bonus points by participating in our language challenges!', 'Engagement'),
    ('Oops! Something went wrong. Please try again later.', 'Error'),
    ('Are you sure you want to delete this item?', 'Confirmation'),
    ('Personalized recommendations based on your progress.', 'Custom');

-- Insert sample data into UserPrompt table (User-Specific Prompts)
INSERT INTO user_prompt (user_id, prompt_text, prompt_type)
VALUES
    (1, 'You''ve been doing great with your vocabulary!', 'Custom'),
    (2, 'Time for your daily practice session!', 'Reminder'),
    (3, 'Try using the new words you learned in a sentence.', 'Instructional'),
    (4, 'You''re making progress! Keep it up!', 'Feedback'),
    (5, 'Remember to take breaks during your study sessions.', 'Reminder');