from typing import List
from app.models.schema.content_gen import ContentGenReq, ContentGenRes
from app.models.schema.user import User
from app.models.schema.topic import Topic
from app.models.schema.content import Content
from app.models.common.chat_message import ChatMessage
from app.models.common.chat_request import ChatRequest
from app.core.config import Config


class ContentGenerationService:
    def generate_content(self, request: ContentGenReq) -> ContentGenRes:
        
        prompt= self.generate_prompt(request)
        messages = [ChatMessage(sender="system", text=prompt,images=None)]
        persona = Config.DEFAULT_PERSONA
        temperature = float(Config.DEFAULT_TEMPERATURE)
        model = Config.DEFAULT_LANGUAGE_TRANSLATION_MODEL

        # Create the ChatRequest object
        chat_request = ChatRequest(
            model=model,
            messages=messages,
            persona=persona,
            temperature=temperature
        )       
        
        
        # TODO:Placeholder text generation, replace with actual content generation logic
        text = f"Generated content for {request.content.content_name} in {request.language.language_name}"

        return ContentGenRes(generated_content=text)

    def generate_prompt(self, request: ContentGenReq) -> str:
        # Generate prompt based on the request
        prompt = f"Generate content for the following topics: {', '.join(request.user_topics)} "
        prompt += f"in {request.language.language_name} language. "
        prompt += f"The content should be about {request.content.content_name}."
        return prompt
    
    