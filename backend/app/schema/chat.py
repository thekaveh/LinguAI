from typing import List, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """
    Represents a chat message.

    Attributes:
        sender (str): The sender of the message.
        text (str): The text content of the message.
        images (Optional[List[str]]): A list of base64 encoded images attached to the message.
    """

    sender: str = Field(..., title="Sender")
    text: str = Field("", title="Text")
    images: Optional[List[str]] = Field(None, title="Base64 Images")

    def set_text(self, text: str):
        """
        Sets the text content of the message.

        Args:
            text (str): The new text content.
        """
        self.text = text

    def append_image(self, image: str):
        """
        Appends an image to the list of images.

        Args:
            image (str): The base64 encoded image to append.
        """
        if self.images is None:
            self.images = []

        self.images.append(image)

    def to_dict(self, include_images=True):
        """
        Converts the chat message to a dictionary representation.

        Args:
            include_images (bool): Whether to include images in the dictionary representation.

        Returns:
            List[Dict[str, Union[str, List[str]]]]: The dictionary representation of the chat message.
        """
        ret = [{"type": "text", "text": self.text}]

        if self.images and include_images:
            ret.extend([{"type": "image_url", "image_url": url} for url in self.images])

        return ret


class ChatRequest(BaseModel):
    """
    Represents a chat request.

    Attributes:
        llm_id (int): The ID of the chat request.
        messages (List[ChatMessage]): The list of chat messages.
        persona (str, optional): The persona for the chat request. Defaults to "Neutral".
        temperature (float, optional): The temperature for generating responses. Defaults to 0.0.
    """
    llm_id: int
    messages: List[ChatMessage]
    persona: str = "Neutral"
    temperature: float = 0.0
