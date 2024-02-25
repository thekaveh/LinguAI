-- Insert sample data into Users table
INSERT INTO cs5934_app_schema.Users (username, email, password_hash, user_type)
VALUES
    ('ironman', 'ironman@example.com', 'password_hash_ironman', 'external'),
    ('captainamerica', 'captainamerica@example.com', 'password_hash_captainamerica', 'external'),
    ('blackwidow', 'blackwidow@example.com', 'password_hash_blackwidow', 'external'),
    ('thor', 'thor@example.com', 'password_hash_thor', 'external'),
    ('hulk', 'hulk@example.com', 'password_hash_hulk', 'external');

-- Insert sample data into UserAssessment table
INSERT INTO cs5934_app_schema.UserAssessment (user_id, assessment_date, skill_level)
VALUES
    (1, '2023-01-01', 'expert'),
    (2, '2023-01-05', 'advanced'),
    (3, '2023-01-10', 'intermediate'),
    (4, '2023-01-15', 'beginner'),
    (5, '2023-01-20', 'master');

-- Insert sample data into Persona table
INSERT INTO cs5934_app_schema.Persona (persona_name, description)
VALUES
    ('Iron Man', 'Genius, billionaire, playboy, philanthropist.'),
    ('Captain America', 'Super-soldier and leader of the Avengers.'),
    ('Black Widow', 'Master spy and former assassin.'),
    ('Thor', 'God of Thunder and prince of Asgard.'),
    ('Hulk', 'Gamma-irradiated scientist with immense strength.');

-- Insert sample data into UserPersona table
INSERT INTO cs5934_app_schema.UserPersona (user_id, persona_id)
VALUES
    (1, 1),  -- Iron Man
    (2, 2),  -- Captain America
    (3, 3),  -- Black Widow
    (4, 4),  -- Thor
    (5, 5);  -- Hulk

-- Insert sample data into LLMPrompt table (System Prompts)
INSERT INTO cs5934_app_schema.LLMPrompt (prompt_text, prompt_type)
VALUES
    ('Welcome to the language learning assistance app!', 'Instructional'),
    ('Congratulations! You completed today''s lesson.', 'Feedback'),
    ('Don''t forget to review your vocabulary.', 'Reminder'),
    ('Earn bonus points by participating in our language challenges!', 'Engagement'),
    ('Oops! Something went wrong. Please try again later.', 'Error'),
    ('Are you sure you want to delete this item?', 'Confirmation'),
    ('Personalized recommendations based on your progress.', 'Custom');

-- Insert sample data into UserPrompt table (User-Specific Prompts)
INSERT INTO cs5934_app_schema.UserPrompt (user_id, prompt_text, prompt_type)
VALUES
    (1, 'You''ve been doing great with your vocabulary!', 'Custom'),
    (2, 'Time for your daily practice session!', 'Reminder'),
    (3, 'Try using the new words you learned in a sentence.', 'Instructional'),
    (4, 'You''re making progress! Keep it up!', 'Feedback'),
    (5, 'Remember to take breaks during your study sessions.', 'Reminder');