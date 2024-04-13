import streamlit as st
import plotly.graph_objs as go

from utils.logger import log_decorator
from services.llm_service import LLMService
from services.state_service import StateService
from services.embeddings_service import EmbeddingsService
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
    _render_sidebar_settings()

    source_lang = st.selectbox(
        "Choose source language:", ["English", "Spanish", "French"]
    )
    difficulty = st.select_slider(
        "Select difficulty:", options=["Easy", "Medium", "Hard"]
    )

    state_service = StateService.instance()

    original = st.text_input("Enter text to embed:")

    attempts = []
    for i in range(1, 4):  # Three attempts for simplicity
        attempt = st.text_input(f"Attempt {i}", key=f"attempt_{i}")
        attempts.append(attempt)

    if st.button("Submit"):
        if not all(attempts):
            st.warning("Please fill in all attempts.")
        else:
            # ideal_translation = fetch_ideal_translation(generated_text, target_lang)
            # similarities = [calculate_cosine_similarity(attempt, ideal_translation) for attempt in attempts]

            # for i, sim in enumerate(similarities, 1):
            # 	st.write(f"Cosine similarity for Attempt {i}: {sim:.2f}")

            # st.write("Ideal Translation:")
            # st.info(ideal_translation)

            # # Generate and display t-SNE plot
            # embeddings = [generate_embedding(text) for text in [generated_text, ideal_translation] + attempts]
            # tsne_plot = generate_tsne_plot(embeddings)
            # st.pyplot(tsne_plot)

            emb = EmbeddingsService.get(
                EmbeddingsGetRequest(
                    llm_id=state_service.embeddings_llm.id,
                    texts=[original] + attempts,
                )
            ).embeddings

            sim = EmbeddingsService.similarities(
                EmbeddingsSimilaritiesRequest(embeddings=emb)
            ).similarities

            st.write(sim)

            reduced_2d = EmbeddingsService.reduce(
                EmbeddingsReduceRequest(embeddings=emb, target_dims=2)
            ).reduced_embeddings

            plot_2d_embeddings_with_plotly(reduced_2d)

            reduced_3d = EmbeddingsService.reduce(
                EmbeddingsReduceRequest(embeddings=emb, target_dims=3)
            ).reduced_embeddings

            plot_3d_embeddings_with_plotly(reduced_3d)


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
