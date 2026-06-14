from __future__ import annotations
from dataclasses import dataclass, field, replace
from typing import Optional, Tuple
from pydantic import BaseModel


# --- wire DTOs ---

class PolyglotPuzzleRequest(BaseModel):
    src_lang: str
    dst_lang: str
    difficulty: str
    llm_id: int                  # backend uses int IDs
    llm_temperature: float = 0.0


class PolyglotPuzzleResponse(BaseModel):
    src_lang_question: str
    dst_lang_question: str


# --- VM-side aggregate model (used by PolyglotPuzzleVM) ---

@dataclass(frozen=True)
class PolyglotPuzzleModel:
    src_langs: Tuple[str, ...] = field(default_factory=tuple)
    dst_langs: Tuple[str, ...] = field(default_factory=tuple)
    difficulties: Tuple[str, ...] = ("Easy", "Medium", "Hard")
    request: Optional[PolyglotPuzzleRequest] = None
    response: Optional[PolyglotPuzzleResponse] = None
    embeddings_llm_id: Optional[int] = None
    structured_llms: Tuple[Tuple[int, str], ...] = field(default_factory=tuple)
    embeddings_llms: Tuple[Tuple[int, str], ...] = field(default_factory=tuple)

    @property
    def has_response(self) -> bool:
        return self.response is not None

    def with_response(self, r: PolyglotPuzzleResponse) -> "PolyglotPuzzleModel":
        return replace(self, response=r)

    def with_request(self, r: PolyglotPuzzleRequest) -> "PolyglotPuzzleModel":
        return replace(self, request=r)
