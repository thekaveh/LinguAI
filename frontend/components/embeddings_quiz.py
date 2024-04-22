import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objs as go
from typing import Optional, List

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


class EmbeddingsQuizViewModel:
    def __init__(self, state_service: StateService) -> None:
        self._state_service = state_service

        self._current_src_lang = None
        self._current_dst_lang = None
        self._current_difficulty = None

        self._embeddings_quiz: Optional[EmbeddingsGetResponse] = None

        self._attempts: List[str] = [""]

        self._data = None
        self._data_2d = None
        self._data_3d = None

    @property
    def src_langs(self):
        return ["English", "Spanish", "French"]

    @property
    def current_src_lang(self):
        if self._current_src_lang is None:
            self._current_src_lang = self.src_langs[0]
        return self._current_src_lang

    @current_src_lang.setter
    def current_src_lang(self, value):
        self._current_src_lang = value

    @property
    def dst_langs(self):
        return ["English", "Spanish", "French"]

    @property
    def current_dst_lang(self):
        if self._current_dst_lang is None:
            self._current_dst_lang = self.dst_langs[0]
        return self._current_dst_lang

    @current_dst_lang.setter
    def current_dst_lang(self, value):
        self._current_dst_lang = value

    @property
    def difficulties(self):
        return ["Easy", "Medium", "Hard"]

    @property
    def current_difficulty(self):
        if self._current_difficulty is None:
            self._current_difficulty = self.difficulties[0]
        return self._current_difficulty

    @current_difficulty.setter
    def current_difficulty(self, value):
        self._current_difficulty = value

    @property
    def embeddings_quiz(self):
        return self._embeddings_quiz

    def generate_embeddings_quiz(self):
        self._embeddings_quiz = EmbeddingsQuizService.generate(
            request=EmbeddingsQuizRequest(
                src_lang=self.current_src_lang,
                dst_lang=self.current_dst_lang,
                difficulty=self.current_difficulty,
                llm_id=self._state_service.content_llm.id,
                llm_temperature=self._state_service.content_temperature,
            )
        )

    def has_embeddings_quiz(self):
        return self._embeddings_quiz is not None

    def clear_embeddings_quiz(self):
        self._data = None
        self._data_2d = None
        self._data_3d = None
        self._attempts = [""]
        self._embeddings_quiz = None

    @property
    def attempts(self):
        return self._attempts

    def can_add_attempt(self):
        return (
            self.has_embeddings_quiz()
            and len(self.attempts) > 0
            and len(self.attempts) < 5
            and all(attempt.strip() != "" for attempt in self.attempts)
        )

    def add_attempt(self):
        if self.can_add_attempt():
            self._attempts.append("")

    def can_submit(self):
        return (
            self.has_embeddings_quiz()
            and len(self.attempts) > 0
            and all(attempt.strip() != "" for attempt in self.attempts)
        )

    def submit(self):
        if self.can_submit():
            texts = [self._embeddings_quiz.dst_lang_question] + self.attempts

            embeddings = EmbeddingsService.get(
                EmbeddingsGetRequest(
                    llm_id=self._state_service.embeddings_llm.id,
                    texts=texts,
                )
            ).embeddings

            similarities = EmbeddingsService.similarities(
                EmbeddingsSimilaritiesRequest(embeddings=embeddings)
            ).similarities

            colors = [_similarity_to_color(sim) for sim in similarities]

            self._data = list(zip(texts, embeddings, similarities, colors))
            self._data.sort(key=lambda x: x[2], reverse=True)

            sorted_embeddings = [x[1] for x in self._data]

            reduced_2d = EmbeddingsService.reduce(
                EmbeddingsReduceRequest(embeddings=sorted_embeddings, target_dims=2)
            ).reduced_embeddings

            reduced_3d = EmbeddingsService.reduce(
                EmbeddingsReduceRequest(embeddings=sorted_embeddings, target_dims=3)
            ).reduced_embeddings

            self._data_2d = [
                (text, coord, sim, color)
                for ((text, _, sim, color), coord) in zip(self._data, reduced_2d)
            ]
            self._data_3d = [
                (text, coord, sim, color)
                for ((text, _, sim, color), coord) in zip(self._data, reduced_3d)
            ]

    @property
    def is_submitted(self):
        return self._data and self._data_2d and self._data_3d

    @property
    def data(self):
        return self._data

    @property
    def data_2d(self):
        return self._data_2d

    @property
    def data_3d(self):
        return self._data_3d

    @staticmethod
    def instance():
        if "embeddings_quiz_view_model" not in st.session_state:
            st.session_state["embeddings_quiz_view_model"] = EmbeddingsQuizViewModel(
                state_service=StateService.instance()
            )
        return st.session_state["embeddings_quiz_view_model"]


@log_decorator
def render():
    vm = EmbeddingsQuizViewModel.instance()

    _render_sidebar_settings()

    with st.container(border=True):
        col_src_lang, col_dst_lang, col_diff = st.columns([1, 1, 1])

        with col_src_lang:
            new_src_lang = st.selectbox(
                label="Choose source language:",
                options=vm.src_langs,
                index=vm.src_langs.index(vm.current_src_lang),
            )
            vm.current_src_lang = new_src_lang

        with col_dst_lang:
            new_dst_lang = st.selectbox(
                label="Choose target language:",
                options=vm.dst_langs,
                index=vm.dst_langs.index(vm.current_dst_lang),
            )
            vm.current_dst_lang = new_dst_lang
            print("dst_lang changed")

        with col_diff:
            new_difficulty = st.select_slider(
                label="Select difficulty:",
                options=vm.difficulties,
                value=vm.current_difficulty,
            )
            vm.current_difficulty = new_difficulty
            print("difficulty changed!")

        col_gen_btn, col_clear_btn = st.columns([2, 1])

        with col_gen_btn:
            if st.button(
                type="primary",
                use_container_width=True,
                label="Generate Embeddings Quiz",
            ):
                vm.generate_embeddings_quiz()
                st.rerun()

        with col_clear_btn:
            if st.button(
                type="primary",
                use_container_width=True,
                label="Clear",
                disabled=not vm.has_embeddings_quiz(),
            ):
                vm.clear_embeddings_quiz()
                st.rerun()

    if vm.has_embeddings_quiz():
        with st.container(border=True):
            st.text_input(
                disabled=True,
                label="Source Language Question",
                value=vm.embeddings_quiz.src_lang_question,
            )

            st.text_input(
                disabled=True,
                label="Ideal Answer",
                value=vm.embeddings_quiz.dst_lang_question
                if vm.is_submitted
                else "●" * len(vm.embeddings_quiz.dst_lang_question),
            )

            for i in range(len(vm.attempts)):
                vm.attempts[i] = st.text_input(
                    value=vm.attempts[i],
                    label=f"Attempt {i+1}",
                )

            col_add_attempt_btn, col_submit_btn = st.columns([1, 2])

            with col_add_attempt_btn:
                if st.button(
                    type="primary",
                    label="Add Attempt",
                    use_container_width=True,
                    disabled=not vm.can_add_attempt(),
                ):
                    vm.add_attempt()
                    st.rerun()

            with col_submit_btn:
                if st.button(
                    type="primary",
                    label="Submit",
                    use_container_width=True,
                    disabled=not vm.can_submit(),
                ):
                    vm.submit()
                    st.rerun()

    if vm.is_submitted:
        with st.container(border=True):
            df = pd.DataFrame(
                vm.data, columns=["Text", "Embeddings", "Similarity", "Color"]
            )
            df.drop(columns=["Embeddings"], inplace=True)

            def style_row(row):
                return f'<tr><td>{row["Text"]}</td><td style="background-color: {row["Color"]}">{row["Similarity"]:.2f}</td></tr>'

            header = "<tr><th>Text</th><th>Similarity</th></tr>"
            rows = "".join(df.apply(style_row, axis=1))
            table_html = f"<table>{header}{rows}</table>"
            st.markdown(table_html, unsafe_allow_html=True)

        with st.container(border=True):
            _plot_2d_data(vm.data_2d)

        with st.container(border=True):
            _plot_3d_data(vm.data_3d)


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


def _similarity_to_color(similarity):
    rich_red = np.array([194, 24, 7])
    yellow = np.array([255, 235, 59])
    rich_green = np.array([67, 160, 71])

    if similarity < 0.5:
        color = rich_red + (yellow - rich_red) * (similarity * 2)
    else:
        color = yellow + (rich_green - yellow) * ((similarity - 0.5) * 2)

    color = np.clip(color, 0, 255).astype(int)
    return f"rgb({color[0]}, {color[1]}, {color[2]})"


def _plot_2d_data(data_2d):
    texts, coords, similarities, colors = zip(*data_2d)
    x, y = zip(*coords)

    custom_colorscale = [
        [0.0, "rgb(194, 24, 7)"],
        [0.5, "rgb(255, 235, 59)"],
        [1.0, "rgb(67, 160, 71)"],
    ]

    trace = go.Scatter(
        x=x,
        y=y,
        mode="markers+text",
        marker=dict(
            size=12,
            color=colors,
            colorscale=custom_colorscale,
            colorbar=dict(
                title="Similarity",
                tickvals=[0, 0.5, 1],
                ticktext=["0", "0.5", "1"],
            ),
            cmin=0,
            cmax=1,
        ),
        text=[f"{sim:.2f}: {text[:25]}" for text, sim in zip(texts, similarities)],
        textposition="top center",
    )

    layout = go.Layout(
        title="2D Embeddings Visualization",
        xaxis=dict(title="Dimension 1"),
        yaxis=dict(title="Dimension 2"),
        hovermode="closest",
    )

    fig = go.Figure(data=[trace], layout=layout)
    st.plotly_chart(fig, use_container_width=True)


def _plot_3d_data(data_3d):
    texts, coords, similarities, colors = zip(*data_3d)
    x, y, z = zip(*coords)

    custom_colorscale = [
        [0.0, "rgb(194, 24, 7)"],
        [0.5, "rgb(255, 235, 59)"],
        [1.0, "rgb(67, 160, 71)"],
    ]

    trace = go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode="markers+text",
        marker=dict(
            size=5,
            color=colors,
            colorscale=custom_colorscale,
            colorbar=dict(
                title="Similarity",
                tickvals=[0, 0.5, 1],
                ticktext=["0", "0.5", "1"],
            ),
            cmin=0,
            cmax=1,
        ),
        text=[f"{sim:.2f}: {text[:25]}" for text, sim in zip(texts, similarities)],
        textposition="top center",
    )

    layout = go.Layout(
        title="3D Embeddings Visualization",
        scene=dict(
            xaxis=dict(title="Dimension 1"),
            yaxis=dict(title="Dimension 2"),
            zaxis=dict(title="Dimension 3"),
        ),
        hovermode="closest",
    )

    fig = go.Figure(data=[trace], layout=layout)
    st.plotly_chart(fig, use_container_width=True)
