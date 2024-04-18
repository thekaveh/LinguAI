from logging import disable
import streamlit as st
import plotly.graph_objs as go

from utils.logger import log_decorator
from services.llm_service import LLMService
from services.state_service import StateService
from services.embeddings_service import EmbeddingsService
from services.embeddings_quiz_service import EmbeddingsQuizService
from models.embeddings_quiz import EmbeddingsQuizRequest, EmbeddingsQuizResponse
from models.embeddings import (
    EmbeddingsGetRequest,
    EmbeddingsGetResponse,
    EmbeddingsReduceRequest,
    EmbeddingsReduceResponse,
    EmbeddingsSimilaritiesRequest,
    EmbeddingsSimilaritiesResponse,
)


@log_decorator
def render():
    state_service = StateService.instance()

    _render_sidebar_settings()

    with st.form(key="embeddings_quiz_gen_form"):
        col_src_lang, col_dst_lang, col_diff = st.columns([1, 1, 1])

        with col_src_lang:
            src_lang = st.selectbox(
                "Choose source language:", ["English", "Spanish", "French"]
            )

        with col_dst_lang:
            dst_lang = st.selectbox(
                "Choose target language:", ["English", "Spanish", "French"]
            )

        with col_diff:
            difficulty = st.select_slider(
                "Select difficulty:", options=["Easy", "Medium", "Hard"]
            )

        if "embeddings_quiz_response" not in st.session_state:
            st.session_state.embeddings_quiz_response = None

        _, col_gen_btn, _ = st.columns([2, 1, 2])

        with col_gen_btn:
            if st.form_submit_button(
                "Generate Quiz", type="primary", use_container_width=True
            ):
                st.session_state.embeddings_quiz_response = (
                    EmbeddingsQuizService.generate(
                        EmbeddingsQuizRequest(
                            llm_id=state_service.embeddings_llm.id,
                            llm_temperature=state_service.content_temperature,
                            source_lang=src_lang,
                            target_lang=dst_lang,
                            difficulty=difficulty,
                        )
                    )
                )

    st.write(st.session_state.embeddings_quiz_response)

    if (
        "embeddings_quiz_response" in st.session_state
        and st.session_state.embeddings_quiz_response
    ):
        if "attempts" not in st.session_state:
            st.session_state.attempts = [""]

        with st.form(key="embeddings_quiz_attempts_form"):
            st.text_input(
                "Question",
                value=st.session_state.embeddings_quiz_response.source_question,
                disabled=True,
            )

            if st.session_state.show_answer:
                st.text_input(
                    "Ideal Answer",
                    value=st.session_state.embeddings_quiz_response.target_question,
                    disabled=True,
                )
            else:
                st.text_input(
                    "Ideal Answer",
                    value="Answer hidden until you submit your attempts",
                    disabled=True,
                )

            for i, attempt in enumerate(st.session_state.attempts):
                st.session_state.attempts[i] = st.text_area(
                    f"Attempt {i+1}", value=attempt, key=f"attempt_{i}"
                )

            all_attempts_filled = all(
                attempt.strip() for attempt in st.session_state.attempts
            )

            _, col_add_attempt, col_submit_attempt, _ = st.columns([1, 1, 1, 1])

            # with col_add_attempt:
            #     if len(st.session_state.attempts) < 5 and st.form_submit_button(
            #         "Add Attempt"
            #     ):
            #         st.session_state.attempts.append("")

            with col_submit_attempt:
                if st.form_submit_button(
                    "Submit All Attempts", disabled=not all_attempts_filled
                ):
                    st.session_state.show_answer = (
                        True  # Reveal the answer upon submission
                    )
                    st.success("Attempts submitted successfully!")

            # if st.form_submit_button("Submit", disabled=not all(attempts)):
            #     emb = EmbeddingsService.get(
            #         EmbeddingsGetRequest(
            #             llm_id=state_service.embeddings_llm.id,
            #             texts=[
            #                 st.session_state.embeddings_quiz_response.target_question
            #             ]
            #             + st.session_state.attempts,
            #         )
            #     ).embeddings

            #     sim = EmbeddingsService.similarities(
            #         EmbeddingsSimilaritiesRequest(embeddings=emb)
            #     ).similarities

            #     st.write(sim)

            #     reduced_2d = EmbeddingsService.reduce(
            #         EmbeddingsReduceRequest(embeddings=emb, target_dims=2)
            #     ).reduced_embeddings

            #     plot_2d_embeddings_with_plotly(reduced_2d)

            #     reduced_3d = EmbeddingsService.reduce(
            #         EmbeddingsReduceRequest(embeddings=emb, target_dims=3)
            #     ).reduced_embeddings

            #     plot_3d_embeddings_with_plotly(reduced_3d)


def _render_sidebar_settings():
    state_service = StateService.instance()

    st.sidebar.write("---")

    with st.sidebar.expander("⚙️", expanded=True):
        embeddings_llms = LLMService.get_embeddings()
        new_embeddings_llm = st.selectbox(
            key="embeddings_llm",
            disabled=not embeddings_llms,
            label="Embeddings Model:",
            help="Embeddings Generation LLM Engine",
            format_func=lambda llm: llm.display_name(),
            options=embeddings_llms if embeddings_llms else ["No LLMs available!"],
            index=0
            if not (embeddings_llms or state_service.embeddings_llm)
            else embeddings_llms.index(
                next(
                    (
                        llm
                        for llm in embeddings_llms
                        if llm.id == state_service.embeddings_llm.id
                    ),
                    embeddings_llms[0],
                )
            ),
        )
        state_service.embeddings_llm = (
            new_embeddings_llm if new_embeddings_llm != "No LLMs available!" else None
        )

        content_llms = LLMService.get_content()
        new_content_llm = st.selectbox(
            key="content_llm",
            disabled=not content_llms,
            label="Large Language Model:",
            help="Content Generation LLM Engine",
            format_func=lambda llm: llm.display_name(),
            options=content_llms if content_llms else ["No LLMs available!"],
            index=0
            if not (content_llms or state_service.content_llm)
            else content_llms.index(
                next(
                    (
                        llm
                        for llm in content_llms
                        if llm.id == state_service.content_llm.id
                    ),
                    content_llms[0],
                )
            ),
        )
        state_service.content_llm = (
            new_content_llm if new_content_llm != "No LLMs available!" else None
        )

        new_content_temperature = st.slider(
            step=0.1,
            min_value=0.0,
            max_value=1.0,
            label="Creativity:",
            key="content_temperature",
            value=state_service.content_temperature,
            help="Content Generation LLM Engine Temperature",
        )
        state_service.content_temperature = new_content_temperature


def plot_2d_embeddings_with_plotly(embeddings):
    x, y = zip(*embeddings)

    trace = go.Scatter(
        x=x,
        y=y,
        mode="markers",
        marker=dict(
            size=5,
            color=y,
            colorscale="Viridis",
            opacity=0.8,
        ),
    )

    layout = go.Layout(
        margin=dict(l=0, r=0, b=0, t=0),
        title="2D Embeddings Visualization",
        scene=dict(
            xaxis=dict(title="X Axis"),
            yaxis=dict(title="Y Axis"),
        ),
    )
    fig = go.Figure(data=[trace], layout=layout)

    st.plotly_chart(fig, use_container_width=True)


def plot_3d_embeddings_with_plotly(embeddings):
    x, y, z = zip(*embeddings)

    trace = go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode="markers",
        marker=dict(
            size=5,
            color=z,
            colorscale="Viridis",
            opacity=0.8,
        ),
    )

    layout = go.Layout(
        margin=dict(l=0, r=0, b=0, t=0),
        title="3D Embeddings Visualization",
        scene=dict(
            xaxis=dict(title="X Axis"),
            yaxis=dict(title="Y Axis"),
            zaxis=dict(title="Z Axis"),
        ),
    )
    fig = go.Figure(data=[trace], layout=layout)

    st.plotly_chart(fig, use_container_width=True)
