CREATE ROLE linguai_app WITH LOGIN PASSWORD 'linguai_app_pass';
--
-- PostgreSQL database dump
--

-- Dumped from database version 16.2 (Debian 16.2-1.pgdg110+2)
-- Dumped by pg_dump version 16.2 (Debian 16.2-1.pgdg110+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: content_preference_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.content_preference_type AS ENUM (
    'story',
    'dialogue',
    'fake article',
    'tutorial',
    'poetry',
    'news report',
    'biography',
    'essay'
);


--
-- Name: language_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.language_type AS ENUM (
    'English',
    'Mandarin',
    'Spanish',
    'German',
    'French'
);


--
-- Name: prompt_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.prompt_type AS ENUM (
    'instructional',
    'feedback',
    'reminder',
    'engagement',
    'error',
    'confirmation',
    'custom'
);


--
-- Name: skill_level_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.skill_level_type AS ENUM (
    'beginner',
    'intermediate',
    'advanced',
    'expert',
    'master'
);


--
-- Name: topic_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.topic_type AS ENUM (
    'sports',
    'nutrition',
    'movies',
    'education',
    'finance',
    'technology',
    'history',
    'business',
    'culture',
    'writing',
    'reading',
    'fashion',
    'politics',
    'art',
    'music',
    'travel',
    'math',
    'science',
    'health & wellness',
    'pronounciation',
    'vocabulary',
    'grammer',
    'speaking'
);


--
-- Name: user_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.user_type AS ENUM (
    'external',
    'admin'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: achievements; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.achievements (
    id integer NOT NULL,
    name character varying(50) NOT NULL
);


--
-- Name: achievements_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.achievements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: achievements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.achievements_id_seq OWNED BY public.achievements.id;


--
-- Name: addresses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.addresses (
    address_id integer NOT NULL,
    user_id integer NOT NULL,
    address_type character varying(50),
    street character varying(255),
    door_number character varying(50),
    city character varying(100),
    state character varying(100),
    zip character varying(20),
    country character varying(100)
);


--
-- Name: addresses_address_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.addresses_address_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: addresses_address_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.addresses_address_id_seq OWNED BY public.addresses.address_id;


--
-- Name: content; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.content (
    content_id integer NOT NULL,
    content_name character varying(100) NOT NULL
);


--
-- Name: content_content_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.content_content_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: content_content_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.content_content_id_seq OWNED BY public.content.content_id;


--
-- Name: language; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.language (
    language_id integer NOT NULL,
    language_name character varying(255) NOT NULL
);


--
-- Name: language_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.language_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: language_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.language_id_seq OWNED BY public.language.language_id;


--
-- Name: llm_prompt; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.llm_prompt (
    prompt_id integer NOT NULL,
    prompt_text text NOT NULL,
    prompt_type character varying(100) NOT NULL
);


--
-- Name: llm_prompt_prompt_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.llm_prompt_prompt_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: llm_prompt_prompt_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.llm_prompt_prompt_id_seq OWNED BY public.llm_prompt.prompt_id;


--
-- Name: persona; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.persona (
    persona_id integer NOT NULL,
    persona_name character varying(100) NOT NULL,
    description text
);


--
-- Name: persona_persona_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.persona_persona_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: persona_persona_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.persona_persona_id_seq OWNED BY public.persona.persona_id;


--
-- Name: topic; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.topic (
    topic_id integer NOT NULL,
    topic_name character varying(255) NOT NULL
);


--
-- Name: topic_topic_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.topic_topic_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: topic_topic_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.topic_topic_id_seq OWNED BY public.topic.topic_id;


--
-- Name: user_assessment; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_assessment (
    assessment_id integer NOT NULL,
    user_id integer,
    assessment_date date,
    skill_level character varying(100) NOT NULL,
    language_id integer
);


--
-- Name: user_assessment_assessment_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_assessment_assessment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_assessment_assessment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_assessment_assessment_id_seq OWNED BY public.user_assessment.assessment_id;


--
-- Name: user_performance; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_performance (
    performance_id integer NOT NULL,
    user_id integer,
    performance_date date,
    accuracy double precision,
    completion_time interval
);


--
-- Name: user_performance_performance_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_performance_performance_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_performance_performance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_performance_performance_id_seq OWNED BY public.user_performance.performance_id;


--
-- Name: user_persona; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_persona (
    user_id integer NOT NULL,
    persona_id integer NOT NULL
);


--
-- Name: user_prompt; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_prompt (
    prompt_id integer NOT NULL,
    user_id integer,
    prompt_text text NOT NULL,
    prompt_type character varying(100) NOT NULL
);


--
-- Name: user_prompt_prompt_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_prompt_prompt_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_prompt_prompt_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_prompt_prompt_id_seq OWNED BY public.user_prompt.prompt_id;


--
-- Name: user_topics; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_topics (
    user_id integer,
    topic_name character varying(255)
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    username character varying(100) NOT NULL,
    email character varying(100) NOT NULL,
    password_hash character varying(100) NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    middle_name character varying(100),
    mobile_phone character varying(20),
    landline_phone character varying(20),
    contact_preference character varying(50),
    user_type character varying(100) NOT NULL,
    base_language character varying(100),
    learning_languages character varying[]
);


--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- Name: achievements id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.achievements ALTER COLUMN id SET DEFAULT nextval('public.achievements_id_seq'::regclass);


--
-- Name: addresses address_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.addresses ALTER COLUMN address_id SET DEFAULT nextval('public.addresses_address_id_seq'::regclass);


--
-- Name: content content_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.content ALTER COLUMN content_id SET DEFAULT nextval('public.content_content_id_seq'::regclass);


--
-- Name: language language_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.language ALTER COLUMN language_id SET DEFAULT nextval('public.language_id_seq'::regclass);


--
-- Name: llm_prompt prompt_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.llm_prompt ALTER COLUMN prompt_id SET DEFAULT nextval('public.llm_prompt_prompt_id_seq'::regclass);


--
-- Name: persona persona_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.persona ALTER COLUMN persona_id SET DEFAULT nextval('public.persona_persona_id_seq'::regclass);


--
-- Name: topic topic_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.topic ALTER COLUMN topic_id SET DEFAULT nextval('public.topic_topic_id_seq'::regclass);


--
-- Name: user_assessment assessment_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_assessment ALTER COLUMN assessment_id SET DEFAULT nextval('public.user_assessment_assessment_id_seq'::regclass);


--
-- Name: user_performance performance_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_performance ALTER COLUMN performance_id SET DEFAULT nextval('public.user_performance_performance_id_seq'::regclass);


--
-- Name: user_prompt prompt_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_prompt ALTER COLUMN prompt_id SET DEFAULT nextval('public.user_prompt_prompt_id_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- Data for Name: achievements; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.achievements (id, name) FROM stdin;
1	Vocabulary Master
2	Grammar Guru
3	Conversation Conqueror
4	Listening Legend
5	Reading Rockstar
6	Writing Wizard
7	Pronunciation Pro
8	Culture Connoisseur
9	Daily Diligence
10	Weekly Warrior
11	Monthly Master
12	Level-Up Luminary
13	Completionist
14	Speedy Learner
15	Persistent Learner
\.


--
-- Data for Name: addresses; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.addresses (address_id, user_id, address_type, street, door_number, city, state, zip, country) FROM stdin;
1	1	shipping	10880 Malibu Point	10880	Malibu	California	90265	USA
2	1	billing	200 Park Avenue	200	New York	New York	10166	USA
3	2	shipping	890 Fifth Avenue	890	Manhattan	New York	10021	USA
4	3	shipping	Red Room Academy		Volgograd			Russia
5	4	shipping	Asgard Palace		Asgard			Asgard
6	5	billing	177A Bleecker Street		New York	New York	10012	USA
\.


--
-- Data for Name: content; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.content (content_id, content_name) FROM stdin;
1	story
2	dialogue
3	fake article
4	tutorial
5	poetry
6	news report
7	biography
8	essay
\.


--
-- Data for Name: language; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.language (language_id, language_name) FROM stdin;
1	English
2	Mandarin
3	Spanish
4	German
5	French
\.


--
-- Data for Name: llm_prompt; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.llm_prompt (prompt_id, prompt_text, prompt_type) FROM stdin;
1	Welcome to the language learning assistance app!	Instructional
2	Congratulations! You completed today's lesson.	Feedback
3	Don't forget to review your vocabulary.	Reminder
4	Earn bonus points by participating in our language challenges!	Engagement
5	Oops! Something went wrong. Please try again later.	Error
6	Are you sure you want to delete this item?	Confirmation
7	Personalized recommendations based on your progress.	Custom
\.


--
-- Data for Name: persona; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.persona (persona_id, persona_name, description) FROM stdin;
1	Iron Man	Genius, billionaire, playboy, philanthropist.
2	Captain America	Super-soldier and leader of the Avengers.
3	Black Widow	Master spy and former assassin.
4	Thor	God of Thunder and prince of Asgard.
5	Hulk	Gamma-irradiated scientist with immense strength.
\.


--
-- Data for Name: topic; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.topic (topic_id, topic_name) FROM stdin;
1	sports
2	nutrition
3	movies
4	education
5	finance
6	technology
7	history
8	business
9	culture
10	writing
11	reading
12	fashion
13	politics
14	art
15	music
16	travel
17	math
18	science
19	health & wellness
20	pronunciation
21	vocabulary
22	grammar
23	speaking
\.


--
-- Data for Name: user_assessment; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_assessment (assessment_id, user_id, assessment_date, skill_level, language_id) FROM stdin;
1	1	2024-03-01	intermediate	1
2	1	2024-03-01	intermediate	3
3	1	2024-03-01	intermediate	5
4	2	2024-03-01	intermediate	2
5	2	2024-03-01	intermediate	4
6	3	2024-03-01	intermediate	3
7	3	2024-03-01	intermediate	4
8	4	2024-03-01	beginner	5
9	5	2024-03-01	intermediate	1
10	5	2024-03-01	intermediate	2
\.


--
-- Data for Name: user_performance; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_performance (performance_id, user_id, performance_date, accuracy, completion_time) FROM stdin;
\.


--
-- Data for Name: user_persona; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_persona (user_id, persona_id) FROM stdin;
1	1
2	2
3	3
4	4
5	5
\.


--
-- Data for Name: user_prompt; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_prompt (prompt_id, user_id, prompt_text, prompt_type) FROM stdin;
1	1	You've been doing great with your vocabulary!	Custom
2	2	Time for your daily practice session!	Reminder
3	3	Try using the new words you learned in a sentence.	Instructional
4	4	You're making progress! Keep it up!	Feedback
5	5	Remember to take breaks during your study sessions.	Reminder
\.


--
-- Data for Name: user_topics; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_topics (user_id, topic_name) FROM stdin;
1	sports
1	nutrition
1	movies
1	technology
1	business
2	education
2	finance
2	writing
3	history
3	culture
3	art
4	reading
4	fashion
5	politics
5	music
5	math
5	science
5	health & wellness
5	vocabulary
5	grammar
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (user_id, username, email, password_hash, first_name, last_name, middle_name, mobile_phone, landline_phone, contact_preference, user_type, base_language, learning_languages) FROM stdin;
1	ironman123	ironman@example.com	password_hash_ironman	Tony	Stark		123-456-7890		email	external	English	{English,Spanish,French}
2	captainamerica123	captainamerica@example.com	password_hash_captainamerica	Steve	Rogers		234-567-8901		mobile_phone	external	English	{Mandarin,German}
3	blackwidow123	blackwidow@example.com	password_hash_blackwidow	Natasha	Romanoff		345-678-9012		email	external	Russian	{Spanish,German}
4	thor123	thor@example.com	password_hash_thor	Thor	Odinson		456-789-0123		email	external	Asgardian	{French}
5	hulk123	hulk@example.com	password_hash_hulk	Bruce	Banner		567-890-1234		mobile_phone	external	English	{English,Mandarin}
\.


--
-- Name: achievements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.achievements_id_seq', 15, true);


--
-- Name: addresses_address_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.addresses_address_id_seq', 6, true);


--
-- Name: content_content_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.content_content_id_seq', 8, true);


--
-- Name: language_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.language_id_seq', 5, true);


--
-- Name: llm_prompt_prompt_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.llm_prompt_prompt_id_seq', 7, true);


--
-- Name: persona_persona_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.persona_persona_id_seq', 5, true);


--
-- Name: topic_topic_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.topic_topic_id_seq', 23, true);


--
-- Name: user_assessment_assessment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.user_assessment_assessment_id_seq', 10, true);


--
-- Name: user_performance_performance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.user_performance_performance_id_seq', 1, false);


--
-- Name: user_prompt_prompt_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.user_prompt_prompt_id_seq', 5, true);


--
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_user_id_seq', 5, true);


--
-- Name: achievements achievements_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.achievements
    ADD CONSTRAINT achievements_name_key UNIQUE (name);


--
-- Name: achievements achievements_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.achievements
    ADD CONSTRAINT achievements_pkey PRIMARY KEY (id);


--
-- Name: addresses addresses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.addresses
    ADD CONSTRAINT addresses_pkey PRIMARY KEY (address_id);


--
-- Name: content content_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.content
    ADD CONSTRAINT content_pkey PRIMARY KEY (content_id);


--
-- Name: language language_language_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.language
    ADD CONSTRAINT language_language_name_key UNIQUE (language_name);


--
-- Name: language language_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.language
    ADD CONSTRAINT language_pkey PRIMARY KEY (language_id);


--
-- Name: llm_prompt llm_prompt_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.llm_prompt
    ADD CONSTRAINT llm_prompt_pkey PRIMARY KEY (prompt_id);


--
-- Name: persona persona_persona_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.persona
    ADD CONSTRAINT persona_persona_name_key UNIQUE (persona_name);


--
-- Name: persona persona_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.persona
    ADD CONSTRAINT persona_pkey PRIMARY KEY (persona_id);


--
-- Name: topic topic_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.topic
    ADD CONSTRAINT topic_pkey PRIMARY KEY (topic_id);


--
-- Name: topic topic_topic_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.topic
    ADD CONSTRAINT topic_topic_name_key UNIQUE (topic_name);


--
-- Name: user_assessment user_assessment_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_assessment
    ADD CONSTRAINT user_assessment_pkey PRIMARY KEY (assessment_id);


--
-- Name: user_performance user_performance_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_performance
    ADD CONSTRAINT user_performance_pkey PRIMARY KEY (performance_id);


--
-- Name: user_persona user_persona_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_persona
    ADD CONSTRAINT user_persona_pkey PRIMARY KEY (user_id, persona_id);


--
-- Name: user_prompt user_prompt_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_prompt
    ADD CONSTRAINT user_prompt_pkey PRIMARY KEY (prompt_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: addresses fk_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.addresses
    ADD CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: user_assessment user_assessment_language_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_assessment
    ADD CONSTRAINT user_assessment_language_id_fkey FOREIGN KEY (language_id) REFERENCES public.language(language_id);


--
-- Name: user_assessment user_assessment_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_assessment
    ADD CONSTRAINT user_assessment_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: user_performance user_performance_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_performance
    ADD CONSTRAINT user_performance_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: user_persona user_persona_persona_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_persona
    ADD CONSTRAINT user_persona_persona_id_fkey FOREIGN KEY (persona_id) REFERENCES public.persona(persona_id);


--
-- Name: user_persona user_persona_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_persona
    ADD CONSTRAINT user_persona_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: user_prompt user_prompt_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_prompt
    ADD CONSTRAINT user_prompt_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: user_topics user_topics_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_topics
    ADD CONSTRAINT user_topics_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: -
--

GRANT USAGE ON SCHEMA public TO linguai_app;


--
-- Name: TABLE achievements; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.achievements TO linguai_app;


--
-- Name: SEQUENCE achievements_id_seq; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON SEQUENCE public.achievements_id_seq TO linguai_app;


--
-- Name: TABLE addresses; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.addresses TO linguai_app;


--
-- Name: SEQUENCE addresses_address_id_seq; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON SEQUENCE public.addresses_address_id_seq TO linguai_app;


--
-- Name: TABLE content; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.content TO linguai_app;


--
-- Name: TABLE language; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.language TO linguai_app;


--
-- Name: TABLE llm_prompt; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.llm_prompt TO linguai_app;


--
-- Name: SEQUENCE llm_prompt_prompt_id_seq; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON SEQUENCE public.llm_prompt_prompt_id_seq TO linguai_app;


--
-- Name: TABLE persona; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.persona TO linguai_app;


--
-- Name: SEQUENCE persona_persona_id_seq; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON SEQUENCE public.persona_persona_id_seq TO linguai_app;


--
-- Name: TABLE topic; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.topic TO linguai_app;


--
-- Name: TABLE user_assessment; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.user_assessment TO linguai_app;


--
-- Name: TABLE user_performance; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.user_performance TO linguai_app;


--
-- Name: SEQUENCE user_performance_performance_id_seq; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON SEQUENCE public.user_performance_performance_id_seq TO linguai_app;


--
-- Name: TABLE user_persona; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.user_persona TO linguai_app;


--
-- Name: TABLE user_prompt; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.user_prompt TO linguai_app;


--
-- Name: SEQUENCE user_prompt_prompt_id_seq; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON SEQUENCE public.user_prompt_prompt_id_seq TO linguai_app;


--
-- Name: TABLE user_topics; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.user_topics TO linguai_app;


--
-- Name: TABLE users; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.users TO linguai_app;


--
-- Name: SEQUENCE users_user_id_seq; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON SEQUENCE public.users_user_id_seq TO linguai_app;


--
-- PostgreSQL database dump complete
--

