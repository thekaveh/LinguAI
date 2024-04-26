import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objs as go
from typing import Optional, List

from utils.logger import log_decorator

from services.llm_service import LLMService
from services.state_service import StateService
from services.language_service import LanguageService
from services.embeddings_service import EmbeddingsService
from services.notification_service import NotificationService
from services.embeddings_quiz_service import EmbeddingsQuizService

from models.llm import LLM
from models.embeddings_quiz import EmbeddingsQuizRequest
from models.embeddings import (
    EmbeddingsGetRequest,
    EmbeddingsGetResponse,
    EmbeddingsReduceRequest,
    EmbeddingsSimilaritiesRequest,
)


class PolyglotPuzzleViewModel:
    def __init__(self) -> None:
        self.reinitialize()

    @log_decorator
    def reinitialize(self) -> None:
        self._src_langs = None
        self._dst_langs = None
        self._difficulties = None
        self._structured_content_llms = None

        self._embeddings_llm = None

        self._current_puzzle_request: Optional[EmbeddingsQuizRequest] = None
        self._current_puzzle_response: Optional[EmbeddingsGetResponse] = None

        self._attempts: List[str] = ["", ""]

        self._data = None
        self._data_2d = None
        self._data_3d = None

    @property
    def src_langs(self):
        if self._src_langs is None:
            self._src_langs = [
                lang.language_name for lang in LanguageService.list_sync()
            ]

        return self._src_langs

    @property
    def dst_langs(self):
        if self._dst_langs is None:
            self._dst_langs = [
                lang.language_name for lang in LanguageService.list_sync()
            ]

        return self._dst_langs

    @property
    def difficulties(self):
        if self._difficulties is None:
            self._difficulties = ["Easy", "Medium", "Hard"]

        return self._difficulties

    @property
    def structured_content_llms(self):
        if self._structured_content_llms is None:
            self._structured_content_llms = LLMService.get_structured_content()

        return self._structured_content_llms

    @property
    def current_puzzle_request(self):
        if self._current_puzzle_request is None:
            self._current_puzzle_request = EmbeddingsQuizRequest(
                llm_temperature=0.0,
                src_lang=self.src_langs[0],
                dst_lang=self.dst_langs[0],
                difficulty=self.difficulties[0],
                llm_id=LLMService.get_structured_content()[0].id,
            )

        return self._current_puzzle_request

    def has_puzzle_response(self):
        return self._current_puzzle_response is not None

    @property
    def current_puzzle_response(self):
        return self._current_puzzle_response

    def generate_puzzle_response(self):
        self._current_puzzle_response = EmbeddingsQuizService.generate(
            request=self.current_puzzle_request
        )

    def clear(self):
        self._data = None
        self._data_2d = None
        self._data_3d = None
        self._attempts = ["", ""]
        self._current_puzzle_response = None

    @property
    def attempts(self):
        return self._attempts

    def can_add_attempt(self):
        return (
            self.has_puzzle_response()
            and len(self.attempts) >= 2
            and len(self.attempts) <= 10
            and all(attempt.strip() != "" for attempt in self.attempts)
        )

    def add_attempt(self):
        if self.can_add_attempt():
            self._attempts.append("")

    @property
    def embeddings_llm(self):
        if self._embeddings_llm is None:
            self._embeddings_llm = LLMService.get_embeddings()[0]

        return self._embeddings_llm

    @embeddings_llm.setter
    def embeddings_llm(self, value: LLM) -> None:
        if value != self._embeddings_llm:
            self._embeddings_llm = value

            NotificationService.success(
                f"Embeddings LLM changed to **{value.display_name()}**"
            )

        return self._embeddings_llm

    @property
    def current_structured_content_llm(self):
        return next(
            (
                llm
                for llm in self.structured_content_llms
                if llm.id == self.current_puzzle_request.llm_id
            ),
            self.structured_content_llms[0],
        )

    @current_structured_content_llm.setter
    def current_structured_content_llm(self, value: LLM) -> None:
        if value.id != self.current_puzzle_request.llm_id:
            self.current_puzzle_request.llm_id = value.id

            NotificationService.success(
                f"Structured Content LLM changed to **{value.display_name()}**"
            )

    @property
    def current_structured_content_temperature(self) -> float:
        return self.current_puzzle_request.llm_temperature

    @current_structured_content_temperature.setter
    def current_structured_content_temperature(self, value: float) -> None:
        if value != self.current_puzzle_request.llm_temperature:
            self.current_puzzle_request.llm_temperature = value

            NotificationService.success(
                f"Structured Content Temperature changed to **{value}**"
            )

    def can_submit(self):
        return (
            self.has_puzzle_response()
            and len(self.attempts) >= 2
            and all(attempt.strip() != "" for attempt in self.attempts)
        )

    def submit(self):
        if self.can_submit():
            texts = [self.current_puzzle_response.dst_lang_question] + self.attempts

            embeddings = EmbeddingsService.get(
                EmbeddingsGetRequest(
                    texts=texts,
                    llm_id=self.embeddings_llm.id,
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
        if "polyglot_puzzle_view_model" not in st.session_state:
            st.session_state["polyglot_puzzle_view_model"] = PolyglotPuzzleViewModel()

        return st.session_state["polyglot_puzzle_view_model"]


@log_decorator
def render():
    state_service = StateService.instance()

    if state_service.tour_mode != None:
        state_service.last_visited = 5
        with state_service.tour_mode.container():
            st.markdown("This is our polyglot puzzle page!")
            st.markdown(
                "On this page, you can assess your language skills by typing in your answers to translation questions and seeing your accuracy!"
            )

            st.markdown("Let's continue with the tour!")
            st.write("")

            col1, col2 = st.columns([1, 1], gap="large")

            with col1:
                st.button(
                    f"Next Stop: Profile",
                    key="switch_button",
                    type="primary",
                    use_container_width=True,
                )

            with col2:
                exit_tour = st.button("Exit Tour", use_container_width=True)
            if exit_tour:
                state_service.tour_mode = None

            st.markdown(
                """
                <span style="font-size: x-small; font-style: italic;">Note: please use the "exit tour" button instead of the 'X' to exit out of the tour!</span>
                """,
                unsafe_allow_html=True,
            )

    vm = PolyglotPuzzleViewModel.instance()

    _render_sidebar_settings()

    full_intro = "Embeddings are a powerful tool in natural language processing, representing words, phrases, or entire sentences as high-dimensional vectors. In LinguAI, embeddings are used to quantify and compare the semantic similarity between your translation attempts and an ideal translation. By converting the text into numerical vectors, the app utilizes algorithms to measure the closeness of meanings, effectively ranking each attempt based on how semantically close it is to the target translation. Furthermore, to make these comparisons more intuitive and visually engaging, the app employs t-SNE dimensionality reduction technique to project these high-dimensional vectors onto 2D or 3D spaces. This visualization not only aids in understanding the quality of translations but also helps learners see the nuances of language use and translation accuracy in a more interactive and comprehendible way."

    sentences = full_intro.split(". ")
    head_intro = ". ".join(sentences[:2]) + "."
    tail_intro = ". ".join(sentences[2:])

    st.markdown(head_intro, unsafe_allow_html=True)

    with st.expander("Read more..."):
        st.markdown(tail_intro, unsafe_allow_html=True)

    with st.container(border=True):
        col_src_lang, col_dst_lang, col_diff = st.columns([1, 1, 1])

        with col_src_lang:
            vm.current_puzzle_request.src_lang = st.selectbox(
                label="Choose source language:",
                options=vm.src_langs,
                index=vm.src_langs.index(vm.current_puzzle_request.src_lang),
            )

        with col_dst_lang:
            vm.current_puzzle_request.dst_lang = st.selectbox(
                label="Choose target language:",
                options=vm.dst_langs,
                index=vm.dst_langs.index(vm.current_puzzle_request.dst_lang),
            )

        with col_diff:
            vm.current_puzzle_request.difficulty = st.select_slider(
                label="Select difficulty:",
                options=vm.difficulties,
                value=vm.current_puzzle_request.difficulty,
            )

        col_gen_btn, col_clear_btn = st.columns([2, 1])

        with col_gen_btn:
            if st.button(
                type="primary",
                use_container_width=True,
                label="Generate Polyglot Puzzle",
            ):
                vm.generate_puzzle_response()
                st.rerun()

        with col_clear_btn:
            if st.button(
                type="primary",
                use_container_width=True,
                label="Clear",
                disabled=not vm.has_puzzle_response(),
            ):
                vm.clear()
                st.rerun()

    if vm.has_puzzle_response():
        with st.container(border=True):
            st.text_input(
                disabled=True,
                label="Source Language Question",
                value=vm.current_puzzle_response.src_lang_question,
            )

            st.text_input(
                disabled=True,
                type="password",
                label="Ideal Translation",
                value=vm.current_puzzle_response.dst_lang_question,
                # if vm.is_submitted
                # else "●" * len(vm.current_puzzle_response.dst_lang_question),
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

    notice = "Note: This visualization simplifies complex, high-dimensional data into a 2D format for demonstration purposes. Please note that it cannot fully capture the intricacies of the original data. Use this tool as a general guide to understand translation similarities and differences visually."
    st.markdown(
        f'<p style="color:grey; font-size:11px;">{notice}</p>', unsafe_allow_html=True
    )


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

    notice = "Note: This visualization simplifies complex, high-dimensional data into a 3D format for demonstration purposes. Please note that it cannot fully capture the intricacies of the original data. Use this tool as a general guide to understand translation similarities and differences visually."
    st.markdown(
        f'<p style="color:grey; font-size:11px;">{notice}</p>', unsafe_allow_html=True
    )


def _render_sidebar_settings():
    vm = PolyglotPuzzleViewModel.instance()

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
            if not (embeddings_llms or vm.embeddings_llm)
            else embeddings_llms.index(
                next(
                    (llm for llm in embeddings_llms if llm.id == vm.embeddings_llm.id),
                    embeddings_llms[0],
                )
            ),
        )
        vm.embeddings_llm = (
            new_embeddings_llm if new_embeddings_llm != "No LLMs available!" else None
        )

        new_structured_content_llm = st.selectbox(
            key="structured_content_llm",
            disabled=not vm.structured_content_llms,
            label="Structured Large Language Model:",
            help="Structured Content Generation LLM Engine",
            format_func=lambda llm: llm.display_name(),
            options=vm.structured_content_llms
            if vm.structured_content_llms
            else ["No LLMs available!"],
            index=0
            if not (vm.structured_content_llms or vm.current_structured_content_llm)
            else vm.structured_content_llms.index(vm.current_structured_content_llm),
        )
        vm.current_structured_content_llm = (
            new_structured_content_llm
            if new_structured_content_llm != "No LLMs available!"
            else None
        )

        vm.current_structured_content_temperature = st.slider(
            step=0.1,
            min_value=0.0,
            max_value=1.0,
            label="Creativity:",
            key="structured_content_temperature",
            value=vm.current_structured_content_temperature,
            help="Structured Content Generation LLM Engine Temperature",
        )
