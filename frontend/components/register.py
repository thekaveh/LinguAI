import streamlit as st
import asyncio
from typing import List
from concurrent.futures import ThreadPoolExecutor
import re
import json

from utils.logger import log_decorator
from services.topic_service import TopicService
from services.language_service import LanguageService
from schema.user import UserCreate
from schema.user_topic import UserTopicBase
from services.user_service import UserService
from schema.language import Language
from schema.user_language import UserLanguage
from schema.topic import Topic
from services.state_service import StateService

@log_decorator
def load_quiz_questions(language):
    try:
        with open(f"./starter_quizzes/{language.lower()}_quiz.json", "r", encoding="utf-8") as file:
            quiz = json.load(file)
        return quiz[language]
    except FileNotFoundError:
        st.error(f"The quiz for {language} could not be found.")
        return []

@log_decorator
def render_quiz():
    if st.session_state.quiz_started and not st.session_state.quiz_submitted:
        if 0 <= st.session_state.current_language_index < len(st.session_state.selected_languages):
            language = st.session_state.selected_languages[st.session_state.current_language_index]
            st.title(f"Starter Quiz: {language}")
            questions = load_quiz_questions(language)
            
            # Start a form for the quiz
            with st.form(key=f"{language}_quiz_form"):
                total_points = 0
                for question in questions:
                    st.write(question["question"])
                    options = question["options"]
                    # Use None for index to ensure no option is preselected
                    answer = st.radio("Choose an option:", options, key=f"option_{questions.index(question)}", index=None)
                    if answer == question["answer"]:
                        total_points += question["points"]
                
                submitted = st.form_submit_button("Submit Quiz")
            
            if submitted:
                skill_level = determine_skill_level(total_points)
                st.success(f"Your current skill level for {language} is: {skill_level}")
                
                # Set quiz as submitted to prevent resubmission
                st.session_state.quiz_submitted = True
                handle_quiz_completion()
        else:
            # Reset quiz state when all quizzes are completed
            reset_quiz_state()


def handle_quiz_completion():
    if st.session_state.current_language_index < len(st.session_state.selected_languages) - 1:
        if st.button("Next Language Quiz"):
            # Increase the index to move to the next language quiz
            st.session_state.current_language_index += 1
            # Reset quiz_submitted flag for the next quiz
            st.session_state.quiz_submitted = False
            # Rerun the app to update the page with the next quiz
            st.experimental_rerun()
    else:
        st.info("You have completed all quizzes. Thank you!")
        # Reset quiz state for a potential new registration or quiz session
        reset_quiz_state()


def reset_quiz_state():
    st.session_state.quiz_started = False
    st.session_state.current_language_index = 0
    st.session_state.selected_languages = []
    st.session_state.quiz_submitted = False

def determine_skill_level(total_points):
    if total_points <= 10:
        return "Beginner"
    elif total_points <= 20:
        return "Intermediate"
    else:
        return "Advanced"

@log_decorator
def fetch_topics_sync():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    topics = loop.run_until_complete(TopicService.list())
    loop.close()
    return topics


@log_decorator
def fetch_topic_combo_options():
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(fetch_topics_sync)
        topics = future.result()
    # Assuming topics is a list of Topic objects, extract the topic_name for each
    return [topic.topic_name for topic in topics]

@log_decorator
def _fetch_languages_sync():
    # Wrapper function to call the async function synchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(LanguageService.list())
    loop.close()
    return result

@log_decorator
def _fetch_languages():
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_fetch_languages_sync)
        return future.result()

@log_decorator
def _render_language_dropdown(languages):
    options = [""] + [language.language_name for language in languages]
    selected_option_index = st.selectbox("Select Base Language*", range(len(options)), format_func=lambda x: options[x])
    
    if selected_option_index > 0:
        selected_base_language = languages[selected_option_index - 1]
    else:
        selected_base_language = None
    if selected_base_language:
        return selected_base_language.language_name
    else:
        return ""

def render():
    # Initialize session state for managing quiz progress
    if 'quiz_started' not in st.session_state:
        st.session_state['quiz_started'] = False
    if 'current_language_index' not in st.session_state:
        st.session_state['current_language_index'] = 0
    if 'selected_languages' not in st.session_state:
        st.session_state['selected_languages'] = []
    if 'quiz_submitted' not in st.session_state:
        st.session_state['quiz_submitted'] = False
    
    if not st.session_state.quiz_started:
        state_service = StateService.instance()
        states = {
        "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
        "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
        "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
        "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
        "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
        "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
        "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
        "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
        "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
        "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
        "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
        "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
        "WI": "Wisconsin", "WY": "Wyoming"
        }


        with st.form(key='register_form'):
            st.subheader("Register")

            # Split the form into columns
            col1, col2 = st.columns(2)

            # Column 1: Personal Details
            with col1:
                first_name = st.text_input("First Name*", placeholder="Your first name", max_chars=20)
                last_name = st.text_input("Last Name*", placeholder="Your last name", max_chars=20)
                middle_name = st.text_input("Middle Name", placeholder="Your middle name (optional)", max_chars=20)
                preferred_name = st.text_input("Preferred Name", placeholder="What should we call you?", max_chars=20)
                email = st.text_input("Email*", placeholder="Enter your email")
                
            # Column 2: Account & Security
            with col2:
                username = st.text_input("Username*", placeholder="Choose a username", max_chars=20)
                password = st.text_input("Password*", placeholder="Create a password", type="password", max_chars=20)
                confirm_password = st.text_input("Confirm Password*", placeholder="Confirm your password", type="password", max_chars=20)
                age = st.selectbox("Age*", options=list(range(15, 66)), index=0)
                gender = st.selectbox("Gender*", options=["", "Male", "Female", "Nonbinary", "Prefer not to say"])            


            st.write("")        
            # Optional Information
            st.write("---")
            st.write("")
    
            col3, col4 = st.columns(2)
            with col3:
                st.markdown("#### Additional Information")            
                discovery_method = st.text_input("How did you learn about us?", placeholder="e.g., School, Friend, Online Ad", max_chars=100)
                day_time_phone = st.text_input("Day Time Mobile Phone", placeholder="+1 234 567 8900")
                st.write("")
                st.markdown("##### Select Languages and Topics")
                language_list= _fetch_languages()
                language_names = [language.language_name for language in language_list]
                selected_languages = st.multiselect("Choose Languages:", options=language_names)  
                
                topic_names = [topic.topic_name for topic in fetch_topics_sync()]
                selected_topics = st.multiselect("Choose topics:", options=topic_names)          

                
                
            with col4:
                st.markdown("")
                st.markdown("")
                st.markdown("")
                st.markdown("")
                selected_base_language=_render_language_dropdown(_fetch_languages())

                motivation = st.text_area("Your Motivation to Use the Platform", height=172, placeholder="Share what motivates you to use this platform", max_chars=100)

                contact_preference_entry = st.selectbox("Contact Preference:", options=["", "Email", "Mobile"])
                if (contact_preference_entry == "Mobile"):
                    contact_preference = "mobile_phone"
                else:
                    contact_preference = "email"
            
            submit_button = st.form_submit_button(label='Register')

            if submit_button:
                # Validate form
                errors = validate_registration_form(motivation, middle_name, first_name, last_name, username, password, confirm_password, email, age,selected_base_language)

                # Display errors or success message
                if errors:
                    st.error("\n".join(errors))
                else:
                    user_language_list= create_user_language_list(selected_languages, language_list)
                    user_create = create_user_create_object(preferred_name, age, gender, discovery_method, motivation, contact_preference, first_name, last_name, middle_name, day_time_phone, email, username, password, selected_base_language, user_language_list, selected_topics)
                    user_create_in_db= asyncio.run(UserService.create_user(user_create))
                    st.success("Registration Successful!, Login to the Platform from the sidebar.")
                    st.session_state.quiz_started = True
                    st.session_state.selected_languages = selected_languages
                    st.experimental_rerun()
                    #home.render()
                    #st.experimental_rerun()
    else:
        render_quiz()

def create_user_language_list(selected_languages: List[str], language_list: List[Language]) -> List[UserLanguage]:
    user_languages = []
    for language_name in selected_languages:
        user_languages.append(language_name)
    return user_languages

def create_user_create_object(preferred_name, age, gender, discovery_method, motivation, contact_preference, first_name, last_name, middle_name, day_time_phone,email, username, password, base_language, user_language_list, selected_topics):
    # Create UserTopicBase objects for each selected topic
    user_topics = [UserTopicBase(user_id=0, topic_name=topic) for topic in selected_topics]
    #st.write(" learning_languages: ", user_language_list)
    return UserCreate(
        username=username,
        email=email,
        user_type="external",
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        preferred_name=preferred_name,
        age=age,
        gender=gender,
        discovery_method=discovery_method,
        motivation=motivation,
        mobile_phone=day_time_phone,
        landline_phone=day_time_phone, # set to the same as mobile phone 
        contact_preference=contact_preference,
        base_language=base_language,        
        learning_languages=user_language_list,
        user_topics=user_topics,  
        password_hash=password
    )


def validate_registration_form(motivation, middle_name, first_name, last_name, username, password, confirm_password, email, age, selected_base_language):
    errors = []

    # name validation regex pattern 
    name_pattern = r"^[A-Za-z-' ]+$"
    if not re.match(name_pattern, first_name):
        errors.append("First Name can only contain letters, hyphens, apostrophes, and spaces.")
    if not re.match(name_pattern, last_name):
        errors.append("Last Name can only contain letters, hyphens, apostrophes, and spaces.")
    # if not re.match(name_pattern, middle_name):
    #     errors.append("Middle Name can only contain letters, hyphens, apostrophes, and spaces.")
    if not re.match(name_pattern, username):
        errors.append("Username can only contain letters, hyphens, apostrophes, and spaces.")
    if len(motivation) > 100:
        errors.append("Motivation cannot exceed 100 characters.")
        
    if not first_name:
        errors.append("First Name is required. \n")

    if not last_name:
        errors.append("Last Name is required. \n")

    if not username:
        errors.append("Username is required. \n")

    if not password:
        errors.append("Password is required. \n")

    if not selected_base_language:
        errors.append("Base Language is required. \n")

    if password != confirm_password:
        errors.append("Passwords do not match. \n")

    if not email:
        errors.append("Email is required. \n")
    elif not re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email):
        errors.append("Invalid email format. \n")

    if not age:
        errors.append("Age is required.")

    return errors

