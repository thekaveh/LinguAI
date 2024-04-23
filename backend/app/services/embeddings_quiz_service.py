from sqlmodel import Session
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser

from app.utils.logger import log_decorator
from app.services.llm_service import LLMService
from app.models.embeddings_quiz import (
    EmbeddingsQuizRequest,
    EmbeddingsQuizResponse,
)


class EmbeddingsQuizService:
    @log_decorator
    def __init__(self, db_session: Session):
        self.db_session = db_session

    @log_decorator
    async def agenerate(self, request: EmbeddingsQuizRequest) -> EmbeddingsQuizResponse:
        assert request is not None, "message is required"
        assert request.llm_id is not None, "llm_id is required"
        assert request.llm_temperature is not None, "llm_temperature is required"
        assert request.src_lang is not None, "src_lang is required"
        assert request.dst_lang is not None, "dst_lang is required"
        assert request.difficulty is not None, "difficulty is required"

        llm_service = LLMService(self.db_session)
        runnable = llm_service.get_chat_runnable(
            llm_id=request.llm_id, temperature=request.llm_temperature
        )
        parser = PydanticOutputParser(pydantic_object=EmbeddingsQuizResponse)
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
					Answer the user query. Wrap the output in `json` tags\n{format_instructions}
                """,
                ),
                (
                    "human",
                    """
					Generate an interesting quiz question or sentence in the requested {src_lang} language (and designate it as 'src_lang_question') along with an ideal translation of generated quiz question in {dst_lang} language (and designate it as 'dst_lang_question') with the level of difficulty that is {difficulty}.

					Input Parameters:
					1. Source Language: Specifies the language in which the question should be initially presented. Possible values include English, Spanish, French, German, etc. In this case the source language is {src_lang}.
					2. Target Language: Specifies the language into which the question should be ideally translated. Possible values include English, Spanish, French, German, etc. In this case the target language is {dst_lang}.
					3. Difficulty: Specify the difficulty level of the question. Possible values are Easy, Medium, and Hard. In this case the difficulty level is {difficulty}.
					
					Output:
					1. 'src_lang_question' (Source Language Question): A question or sentence generated in the source language {src_lang} that is interesting and engaging, and prompts the learner to think about how to translate it into the target language.
					2. 'dst_lang_question' (Ideal Target Language Translation): The most accurate and natural translation of the generated 'src_lang_question' into the target language {dst_lang}, reflecting nuances and idiomatic usage appropriate for the target language.
					
					Below are some example input and outputs:
						1. Example 1:
							1.1. Input:
								+ src_lang: English
								+ dst_lang: French
								+ difficulty: Medium
		
							1.2. Output:
								+ src_lang_question: "How often do you travel to new places?"
								+ dst_lang_question: "À quelle fréquence voyagez-vous vers de nouveaux endroits?"
        
						2. Example 2:
							2.1. Input:
								+ src_lang: Spanish
								+ dst_lang: German
								+ difficulty: Hard
        
							2.2. Output:
								+ src_lang_question: "¿Cuántas veces viajas a los lugares nuevos?"
								+ dst_lang_question: "Wie oft fährt man zu neuen Orten?"
        
						3. Example 3:
							3.1. Input:
								+ src_lang: French
								+ dst_lang: Spanish
								+ difficulty: Easy

							3.2. Output:
								+ src_lang_question: "Quelles sont les différentes façons de dire 'bonjour' en français"
								+ dst_lang_question: "¿Cuáles son las diferentes formas

						4. Example 4:
							4.1. Input:
								+ src_lang: German
								+ dst_lang: French
								+ difficulty: Medium
        
							4.2. Output:
								+ src_lang_question: "Wie oft fahren Sie zu neuen Orten?"
								+ dst_lang_question: "À quelle fréquence ferrariez-vous vers de nouveaux endroits?"
        
						5. Example 5:
							5.1. Input:
								+ src_lang: English
								+ dst_lang: German
								+ difficulty: Medium
        
							5.2. Output:
								+ src_lang_question: "the pen is mightier than the sword."
								+ dst_lang_question: "Die Feder ist mächtiger als das Schwert."

					Requirements:
						+ The generated question designated as 'src_lang_question' in the {src_lang} source language should be strictly in {src_lang}, culturally neutral and should not require specific cultural knowledge to understand or translate.
						+ The generated question designated as 'src_lang_question' in the {src_lang} source language should be suitable for the chosen difficulty level {difficulty}, with Easy involving basic vocabulary and grammar, Medium involving more complex sentence structures or idiomatic expressions, and Hard involving advanced syntax or specialized vocabulary.
						+ The generated question designated as 'src_lang_question' in the {src_lang} source language should not exceed 25 words in the source language {src_lang} to keep it concise and focused.
						
						+ The generated ideal translation designated as 'dst_lang_question' in the {dst_lang} target language should be strictly in {dst_lang}, the most accurate and natural translation of the generated 'src_lang_question' into the target language {dst_lang}, reflecting nuances and idiomatic usage appropriate for the target language.
						+ The generated ideal translation designated as 'dst_lang_question' in the {dst_lang} target language should be suitable for the chosen difficulty level {difficulty}, with Easy involving basic vocabulary and grammar, Medium involving more complex sentence structures or idiomatic expressions, and Hard involving advanced syntax or specialized vocabulary.

					Wrap the output in `json` tags\n{format_instructions}
				""",
                ),
            ]
        ).partial(format_instructions=parser.get_format_instructions())

        chain = prompt | runnable | parser

        response = await chain.ainvoke(
            {
                "src_lang": request.src_lang,
                "dst_lang": request.dst_lang,
                "difficulty": request.difficulty,
            }
        )

        return response
