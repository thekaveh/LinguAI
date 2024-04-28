import json
import asyncio
import streamlit as st
from datetime import datetime
from utils.logger import log_decorator

from services.state_service import StateService
from services.user_service import UserService
from services.language_service import LanguageService
from schema.user_assessment import UserAssessmentCreate


def get_user_by_username_sync(username):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    user_details = loop.run_until_complete(
        UserService.get_user_id_by_username(username)
    )
    loop.close()
    return user_details


def get_language_sync(language_name):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    language_details = loop.run_until_complete(
        LanguageService.get_language_by_name(language_name)
    )
    loop.close()
    return language_details


def load_quiz_questions(language):
    try:
        with open(
            f"./starter_quizzes/{language.lower()}_quiz.json", "r", encoding="utf-8"
        ) as file:
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
    result = loop.run_until_complete(
        UserService.create_user_assessment(user_id, assessment_data)
    )
    loop.close()
    return result


def render():
    """
    Renders the language assessment page.

    This function initializes session state for managing quiz progress and displays the language assessment page.
    Users can select a language to assess their skills and increase their skill level.
    The function handles the quiz submission and updates the user's skill level based on the assessment results.

    Returns:
        None
    """
    # Initialize session state for managing quiz progress
    if "quiz_started" not in st.session_state:
        st.session_state["quiz_started"] = False
    if "selected_language" not in st.session_state:
        st.session_state["selected_language"] = ""
    if "quiz_submitted" not in st.session_state:
        st.session_state["quiz_submitted"] = False
    if "total_points" not in st.session_state:
        st.session_state["total_points"] = 0
    if "display_quiz" not in st.session_state:
        st.session_state["display_quiz"] = True

    state_service = StateService.instance()

    # Tour mode
    if state_service.tour_mode != None:
        state_service.last_visited = 7
        with state_service.tour_mode.container():
            st.markdown("### 📝 Welcome to the Language Assessment Page!")
            st.markdown(
                "This is your personal language testing ground! On this page, you can assess your language skills and increase your skill level. It's like a personal language exam that helps you understand your strengths and areas for improvement. 🎯"
            )

            st.markdown(
                "Take the assessment, see your results, and use the feedback to guide your learning journey. Remember, every assessment is a step towards language mastery! 🏆"
            )

            st.markdown("🎉 Congratulations! We've completed the tour! 🎉")
            st.write("")

            col1, col2 = st.columns([1, 1], gap="large")

            with col1:
                st.button(f"Restart Tour", key='switch_button', use_container_width=True)

            with col2:
                exit_tour = st.button("Exit Tour", use_container_width=True)
            
            if exit_tour:
                state_service.tour_mode = None
            
            st.markdown("""
                <span style="font-size: x-small; font-style: italic;">Note: please use the "exit tour" button instead of the 'X' to exit out of the tour!</span>
                """,
                unsafe_allow_html=True
            )

    user = asyncio.run(UserService.get_user_by_username(state_service.username))
    current_user_languages = [language for language in user.learning_languages]
    user_id = get_user_by_username_sync(user.username)

    st.write("##### Take Language Assessments to Increase Your Skill Level!")
    language = st.selectbox("Select Language to Assess", options=current_user_languages)

    if st.button("Start Assessment"):
        st.session_state["quiz_started"] = True
        st.session_state["selected_language"] = language

    if st.session_state["quiz_started"]:
        questions = load_quiz_questions(st.session_state["selected_language"])
        with st.form(
            key=f"{st.session_state['selected_language']}_quiz_form",
            clear_on_submit=True,
        ):
            total_points = 0
            for i, question in enumerate(questions):
                st.write(question["question"])
                options = question["options"]
                answer = st.radio(
                    "Choose an option:",
                    options,
                    key=f"{language}_question_{i}",
                    index=None,
                )
                if answer == question["answer"]:
                    total_points += question["points"]

            submit = st.form_submit_button("Submit Quiz")
            if submit:
                st.session_state["quiz_submitted"] = True
                st.session_state["quiz_started"] = False
                st.session_state["total_points"] = total_points

    if st.session_state.get("quiz_submitted"):
        skill_level = determine_skill_level(st.session_state["total_points"])
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

        st.session_state["quiz_submitted"] = False
        st.session_state["total_points"] = 0
