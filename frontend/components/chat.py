import asyncio
import streamlit as st

from schema.chat import ChatMessage
from utils.logger import log_decorator
from utils.image_utils import ImageUtils
from services.llm_service import LLMService
from services.chat_service import ChatService
from services.state_service import StateService
from services.persona_service import PersonaService
from services.text_to_speech_service import TextToSpeechService


@log_decorator
def render():
    """
    Renders the chat page.

    This function is responsible for rendering the chat page, where users can interact with the chatbot
    to practice their language skills and upload visual images to ask questions about. It also handles
    the tour mode functionality, allowing users to navigate through the tour and exit the tour.

    Returns:
        None
    """
    state_service = StateService.instance()

    if state_service.tour_mode != None:
        state_service.last_visited = 1
        with state_service.tour_mode.container():
            st.markdown("### 🗣️ Welcome to the Chat Page!")
            st.markdown(
                "This is where the magic happens! Our chat page is your personal language practice playground. You can interact with our AI chatbot to practice your language skills. 🤖"
            )

            st.markdown(
                "But that's not all! You can also upload visual images and ask questions about them. It's a great way to learn new vocabulary and concepts. 🖼️"
            )

            st.markdown("Ready to continue the journey? Let's go! 🚀")
            st.write("")

            col1, col2 = st.columns([1, 1], gap="large")

            with col1:
                st.button(
                    f"Next Stop: Content Reading",
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

    def _render_chat_messages():
        """
        Renders the chat messages.

        This function is responsible for rendering the chat messages on the chat page. It iterates through
        the chat messages stored in the state service and displays them along with any uploaded images.

        Returns:
            None
        """
        messages = state_service.chat_messages
        n = len(messages)

        for idx, message in enumerate(messages):
            if idx < n - 1 or message.text:
                with st.chat_message(message.sender):
                    st.markdown(message.text)

                    if message.images:
                        for image in message.images:
                            st.image(image, caption="Uploaded Image")

    _render_chat_messages()

    if prompt := st.chat_input(
        "Ask a question...",
        disabled=(state_service.chat_persona is None)
        or (state_service.content_llm is None),
    ):
        if (
            state_service.chat_messages
            and state_service.chat_messages[-1].sender == "user"
        ):
            new_user_chat_message = state_service.chat_messages[-1]
            new_user_chat_message.set_text(prompt)
        else:
            new_user_chat_message = ChatMessage(sender="user", text=prompt)
            state_service.chat_append_message(chat_message=new_user_chat_message)

        with st.chat_message(new_user_chat_message.sender):
            st.markdown(new_user_chat_message.text)

            if new_user_chat_message.images:
                for image in new_user_chat_message.images:
                    st.image(image, caption="Uploaded Image")

        with st.chat_message("ai"):
            response_message_placeholder = st.empty()

            async def _achat_on_changed(chunk: str):
                response_message_placeholder.markdown(chunk)

            async def _achat_on_completed(new_ai_chat_message: ChatMessage):
                state_service.chat_append_message(new_ai_chat_message)
                state_service.chat_increment_file_upload_key()

                if state_service.content_tts:
                    audio_data = await TextToSpeechService.agenerate(
                        lang="en",
                        text=new_ai_chat_message.text,
                    )
                    audio_html = f'<audio src="{audio_data.audio}" controls="controls" autoplay="autoplay" type="audio/mpeg"/>'
                    st.markdown(audio_html, unsafe_allow_html=True)

            asyncio.run(
                ChatService.achat(
                    llm_id=state_service.content_llm.id,
                    on_changed_fn=_achat_on_changed,
                    on_completed_fn=_achat_on_completed,
                    messages=state_service.chat_messages,
                    temperature=state_service.content_temperature,
                    persona=state_service.chat_persona.persona_name,
                )
            )

    @log_decorator
    def _file_uploader_on_change():
        """
        Handles the file uploader on change event.

        This function is called when the user uploads images using the file uploader. It retrieves the
        uploaded images and adds them to the current user chat message.

        Returns:
            None
        """
        if uploaded_images := st.session_state[
            f"file_uploader_{state_service.chat_file_upload_key}"
        ]:
            if (
                state_service.chat_messages
                and state_service.chat_messages[-1].sender == "user"
            ):
                new_user_chat_message = state_service.chat_messages[-1]
            else:
                new_user_chat_message = ChatMessage(sender="user")
                state_service.chat_append_message(chat_message=new_user_chat_message)

            for uploaded_image in uploaded_images:
                if (
                    uploaded_image_to_base64_image_url
                    := ImageUtils.uploaded_image_to_base64_image_url(uploaded_image)
                ):
                    new_user_chat_message.append_image(
                        uploaded_image_to_base64_image_url
                    )

    st.sidebar.write("---")

    with st.sidebar.expander("💬", expanded=True):
        vision_llms = LLMService.get_vision()
        st.file_uploader(
            label="Attach images:",
            accept_multiple_files=True,
            type=["png", "jpg", "jpeg"],
            on_change=_file_uploader_on_change,
            disabled=(state_service.chat_persona is None)
            or (state_service.content_llm is None)
            or not any(
                (llm for llm in vision_llms if llm.id == state_service.content_llm.id)
            ),
            key=f"file_uploader_{state_service.chat_file_upload_key}",
        )

        if st.button(label="Clear Chat", use_container_width=True, type="primary"):
            state_service.chat_clear_messages()
            st.rerun()

    with st.sidebar.expander("⚙️", expanded=True):
        content_llms = LLMService.get_content()
        cur_content_llm = next(
            (llm for llm in content_llms if llm.id == state_service.content_llm.id),
            content_llms[0],
        )
        new_content_llm = st.selectbox(
            key="content_llm",
            disabled=not content_llms,
            label="Large Language Model:",
            help="Content Generation LLM Engine",
            format_func=lambda llm: llm.display_name(),
            options=content_llms if content_llms else ["No LLMs available!"],
            index=0
            if not (content_llms or state_service.content_llm)
            else content_llms.index(cur_content_llm),
        )
        state_service.content_llm = (
            new_content_llm if new_content_llm != "No LLMs available!" else None
        )
        if cur_content_llm != new_content_llm:
            st.rerun()

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

        chat_personas = PersonaService.get_all()
        new_chat_persona = st.selectbox(
            label="Persona:",
            key="chat_persona",
            disabled=not chat_personas,
            help="Content Generation Persona",
            format_func=lambda persona: persona.persona_name,
            options=chat_personas if chat_personas else ["No personas available!"],
            index=0
            if not (chat_personas or state_service.chat_persona)
            else chat_personas.index(
                next(
                    (
                        persona
                        for persona in chat_personas
                        if persona.persona_id == state_service.chat_persona.persona_id
                    ),
                    content_llms[0],
                )
            ),
        )
        state_service.chat_persona = (
            new_chat_persona if new_chat_persona != "No personas available!" else None
        )

        new_content_tts = st.checkbox(
            key="content_tts",
            label="Voiceover",
            value=state_service.content_tts,
            help="Content Generation Text-to-Speech",
        )
        state_service.content_tts = new_content_tts
