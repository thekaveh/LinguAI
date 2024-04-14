import streamlit as st
import asyncio
import json
from utils.logger import log_decorator
from datetime import datetime
from services.state_service import StateService
from services.user_service import UserService
from services.language_service import LanguageService
from schema.user_assessment import UserAssessmentCreate


def get_user_by_username_sync(username):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    user_details = loop.run_until_complete(UserService.get_user_id_by_username(username))
    loop.close()
    return user_details


def get_language_sync(language_name):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    language_details = loop.run_until_complete(LanguageService.get_language_by_name(language_name))
    loop.close()
    return language_details


def load_quiz_questions(language):
    try:
        with open(f"./starter_quizzes/{language.lower()}_quiz.json", "r", encoding="utf-8") as file:
            quiz = json.load(file)
        return quiz[language]
    except FileNotFoundError:
        st.error(f"The quiz for {language} could not be found.")
        return []


def determine_skill_level(total_points):
    if total_points <= 10:
        return "Beginner"
    elif total_points <= 20:
        return "Intermediate"
    else:
        return "Advanced"


def create_user_assessment_sync(user_id, assessment_data):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(UserService.create_user_assessment(user_id, assessment_data))
    loop.close()
    return result

def render():
     # Initialize session state for managing quiz progress
    if 'quiz_started' not in st.session_state:
        st.session_state['quiz_started'] = False
    if 'selected_language' not in st.session_state:
        st.session_state['selected_language'] = ""
    if 'quiz_submitted' not in st.session_state:
        st.session_state['quiz_submitted'] = False
    if 'total_points' not in st.session_state:
        st.session_state['total_points'] = 0
    if 'display_quiz' not in st.session_state:
        st.session_state['display_quiz'] = True

    
    state_service = StateService.instance()
    user = asyncio.run(UserService.get_user_by_username(state_service.username))
    current_user_languages = [language for language in user.learning_languages]
    user_id = get_user_by_username_sync(user.username)

    st.write("##### Take Language Assessments to Increase Your Skill Level!")
    language = st.selectbox("Select Language to Assess", options=current_user_languages)

    if st.button("Start Assessment"):
        st.session_state['quiz_started'] = True
        st.session_state['selected_language'] = language
        
    if st.session_state['quiz_started']:
        questions = load_quiz_questions(st.session_state['selected_language'])
        with st.form(key=f"{st.session_state['selected_language']}_quiz_form", clear_on_submit=True):
            total_points = 0
            for i, question in enumerate(questions):
                st.write(question["question"])
                options = question["options"]
                answer = st.radio("Choose an option:", options, key=f"{language}_question_{i}", index=None)
                if answer == question["answer"]:
                    total_points += question["points"]
            
            submit = st.form_submit_button("Submit Quiz")
            if submit:
                st.session_state['quiz_submitted'] = True
                st.session_state['quiz_started'] = False
                st.session_state['total_points'] = total_points
                
    if st.session_state.get('quiz_submitted'):
        skill_level = determine_skill_level(st.session_state['total_points'])
        st.success(f"Your new skill level for {language} is: {skill_level}")
        language_details = get_language_sync(language)
        language_id = language_details.language_id
                
        assessment_data = UserAssessmentCreate(
            user_id=user_id,
            language_id=language_id,
            assessment_date=datetime.today(),
            assessment_type="Retake",
            skill_level=skill_level.lower(),
            strength="Assessment retake",
            weakness="Assessment retake",
            language=language_details,
        )
        
        create_user_assessment_sync(user_id, assessment_data)

        st.session_state['quiz_submitted'] = False
        st.session_state['total_points'] = 0