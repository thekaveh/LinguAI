import asyncio
import streamlit as st

from schema.chat import ChatMessage
from utils.logger import log_decorator
from utils.image_utils import ImageUtils
from services.llm_service import LLMService
from services.chat_service import ChatService
from services.state_service import StateService


@log_decorator
def render():
    state_service = StateService.instance()

    vision_models = asyncio.run(LLMService.list_vision_models())

    st.title(f"Chat")
    st.write(f"Persona: {state_service.persona} - Model: {state_service.model}")

    def _render_chat_messages():
        state_service = StateService.instance()

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
        disabled=(state_service.persona is None) or (state_service.model is None),
    ):
        if (
            state_service.chat_messages
            and state_service.chat_messages[-1].sender == "user"
        ):
            new_user_chat_message = state_service.chat_messages[-1]
            new_user_chat_message.set_text(prompt)
        else:
            new_user_chat_message = ChatMessage(sender="user", text=prompt)
            state_service.append_chat_message(chat_message=new_user_chat_message)

        with st.chat_message(new_user_chat_message.sender):
            st.markdown(new_user_chat_message.text)

            if new_user_chat_message.images:
                for image in new_user_chat_message.images:
                    st.image(image, caption="Uploaded Image")

        with st.chat_message("ai"):
            response_message_placeholder = st.empty()

            def _achat_on_next(chunk: str):
                response_message_placeholder.markdown(chunk)

            def _achat_on_completed(new_ai_chat_message: ChatMessage):
                state_service.append_chat_message(new_ai_chat_message)
                state_service.increment_chat_file_upload_key()

            asyncio.run(
                ChatService.achat(
                    model=state_service.model,
                    persona=state_service.persona,
                    messages=state_service.chat_messages,
                    temperature=state_service.temperature,
                    on_next_fn=lambda chunk: _achat_on_next(chunk),
                    on_completed_fn=lambda chat_message: _achat_on_completed(
                        chat_message
                    ),
                )
            )

    @log_decorator
    def _file_uploader_on_change():
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
                state_service.append_chat_message(chat_message=new_user_chat_message)

            for uploaded_image in uploaded_images:
                if uploaded_image_to_base64_image_url := ImageUtils.uploaded_image_to_base64_image_url(
                    uploaded_image
                ):
                    new_user_chat_message.append_image(
                        uploaded_image_to_base64_image_url
                    )

    st.sidebar.file_uploader(
        label="Attach images:",
        accept_multiple_files=True,
        type=["png", "jpg", "jpeg"],
        on_change=_file_uploader_on_change,
        disabled=(state_service.persona is None)
        or (state_service.model is None)
        or (state_service.model not in vision_models),
        key=f"file_uploader_{state_service.chat_file_upload_key}",
    )
