import streamlit as st
from utils.logger import log_decorator
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
import plotly.graph_objs as go


@log_decorator
def render():
    st.title("Polyglot Puzzle!")

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
                    model=state_service.model,
                    texts=[original] + attempts,
                )
            ).embeddings

            sim = EmbeddingsService.similarities(
                EmbeddingsSimilaritiesRequest(embeddings=emb)
            ).similarities

            st.write(sim)

            reduced = EmbeddingsService.reduce(
                EmbeddingsReduceRequest(embeddings=emb, target_dims=3)
            ).reduced_embeddings

            st.write(reduced)

            plot_3d_embeddings_with_plotly(reduced)


def plot_3d_embeddings_with_plotly(embeddings):
    x, y, z = zip(*embeddings)

    trace = go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode="markers",
        marker=dict(
            size=5,
            color=z,  # Color based on the z-value for depth. Can change to other values or a constant for uniform color.
            colorscale="Viridis",  # Other color scales: Cividis, Magma, Plasma, etc.
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

    st.plotly_chart(
        fig, use_container_width=True
    )  # This will make the plot use the full width of the container
