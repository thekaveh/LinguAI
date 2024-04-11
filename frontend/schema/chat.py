from typing import List, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    sender: str = Field(..., title="Sender")
    text: str = Field("", title="Text")
    images: Optional[List[str]] = Field(None, title="Base64 Images")

    def set_text(self, text: str):
        self.text = text

    def append_image(self, image: str):
        if self.images is None:
            self.images = []

        self.images.append(image)

    def to_dict(self):
        ret = [{"type": "text", "text": self.text}]

        if self.images:
            ret.extend([{"type": "image_url", "image_url": url} for url in self.images])

        return ret


class ChatRequest(BaseModel):
    llm_id: int

    messages: List[ChatMessage]

    persona: str = "Neutral"
    temperature: float = 0.0
