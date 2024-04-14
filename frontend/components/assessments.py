import streamlit as st
import asyncio
import json
from utils.logger import log_decorator
from datetime import datetime
from services.state_service import StateService
from services.user_service import UserService
from services.language_service import LanguageService
from schema.user_assessment import UserAssessmentCreate

@log_decorator
def load_quiz_questions(language):
    try:
        with open(f"./starter_quizzes/{language.lower()}_quiz.json", "r", encoding="utf-8") as file:
            quiz = json.load(file)
        return quiz[language]
    except FileNotFoundError:
        st.error(f"The quiz for {language} could not be found.")
        return []

def get_user_by_username_sync(username):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    user_details = loop.run_until_complete(UserService.get_user_id_by_username(username))
    loop.close()
    return user_details

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

def clear_quiz_state(language):
    if f'{language}_quiz_submitted' in st.session_state:
        del st.session_state[f'{language}_quiz_submitted']
    if f'{language}_skill_level' in st.session_state:
        del st.session_state[f'{language}_skill_level']
    # Clear any question states for the language
    for key in list(st.session_state.keys()):
        if key.startswith("question_"):
            del st.session_state[key]
    st.experimental_rerun()

def render_quiz(language, user_id):
    questions = load_quiz_questions(language)
    if questions:
        if st.session_state.get(f'{language}_quiz_submitted', False):
            skill_level = st.session_state.get(f'{language}_skill_level', "Not determined")
            st.success(f"Your current skill level for {language} is: {skill_level}")
            clear_quiz_state(language)
        
        form_key = f"{language}_quiz_form"
        with st.form(key=form_key):
            total_points = 0
            for i, question in enumerate(questions):
                st.write(question["question"])
                options = question["options"]
                answer = st.radio("Choose an option:", options, key=f"question_{i}", index=None)
                if answer == question["answer"]:
                    total_points += question["points"]
            
            submitted = st.form_submit_button("Submit Quiz")
                                
        if submitted:
            # Calculate and temporarily store skill level for current language
            skill_level = determine_skill_level(total_points)
            st.session_state[f'{language}_skill_level'] = skill_level
            st.session_state[f'{language}_quiz_submitted'] = True
            
            # update the backend with the new assessment 
            language_details = get_language_sync(language)
            language_id = language_details.language_id
            
            assessment_data = UserAssessmentCreate(
                user_id=user_id,
                language_id=language_id,
                assessment_date=datetime.today(),
                assessment_type="Repeated",
                skill_level=skill_level.lower(),
                strength="Retake of diagnostic quiz",
                weakness="Retake of diagnostic quiz",
                language=language_details,
            )
            
            # create_user_assessment_sync(user_id, assessment_data)
            create_user_assessment_sync(user_id, assessment_data)
                            
            # Use rerun to refresh the page to show the skill level
            st.experimental_rerun()

def render():
    state_service = StateService.instance()
    user = asyncio.run(UserService.get_user_by_username(state_service.username))
    current_user_languages = [language for language in user.learning_languages]
    user_id = get_user_by_username_sync(user.username)
    
    st.write("##### Take Language Assessments to Increase Your Skill Level!")
    
    selected_language = st.selectbox("Select Language to Assess", options=current_user_languages)
    
    if st.button(f"Start {selected_language} Assessment"):
        if 'quiz_attempt' not in st.session_state:
            st.session_state['quiz_attempt'] = 0
        render_quiz(selected_language, user_id)
            
    