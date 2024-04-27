from fastapi import APIRouter

from app.api.v1.endpoints import (
    chat,
    llm,
    persona,
    user,
    content,
    topic,
    content_gen,
    prompt,
    rewrite_content,
    skill_level,
    language,
    review_writing,
    text_to_speech,
    user_content,
    embeddings,
    polyglot_puzzle,
)

router = APIRouter()

router.include_router(llm.router, prefix="/v1", tags=["v1"])
router.include_router(chat.router, prefix="/v1", tags=["v1"])
router.include_router(persona.router, prefix="/v1", tags=["v1"])
router.include_router(user.router, prefix="/v1", tags=["v1"])
router.include_router(content.router, prefix="/v1", tags=["v1"])
router.include_router(topic.router, prefix="/v1", tags=["v1"])
router.include_router(content_gen.router, prefix="/v1", tags=["v1"])
router.include_router(prompt.router, prefix="/v1", tags=["v1"])
router.include_router(rewrite_content.router, prefix="/v1", tags=["v1"])
router.include_router(skill_level.router, prefix="/v1", tags=["v1"])
router.include_router(language.router, prefix="/v1", tags=["v1"])
router.include_router(review_writing.router, prefix="/v1", tags=["v1"])
router.include_router(text_to_speech.router, prefix="/v1", tags=["v1"])
router.include_router(user_content.router, prefix="/v1", tags=["v1"])
router.include_router(embeddings.router, prefix="/v1", tags=["v1"])
router.include_router(polyglot_puzzle.router, prefix="/v1", tags=["v1"])

"""
This module defines the router for the API endpoints in the v1 version.

The router includes various sub-routers for different endpoints, such as chat, llm, persona, user, content, topic, etc.

Example usage:
    from app.api.v1.router import router

    app.include_router(router, prefix="/api")

"""
