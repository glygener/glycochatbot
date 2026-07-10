import json
import os

from fastapi import HTTPException

from api.formatting import best_source, format_display_answer
from api.schemas import ChatResponse, MessageItem, SessionMessagesResponse, rag_to_chat
from generation.schemas import RAGResponse
from query.config import RAGConfig
from RAG.pipeline import RAGPipeline
from session.helpers import (
    build_name_question_answer,
    build_name_statement_answer,
    enrich_query_with_history,
    extract_display_name,
    extract_name_from_history,
)
from session.memory import build_recap_answer, is_name_statement
from session.router import QuestionType, classify_question
from session.store import SessionStore


class ChatOrchestrator:
    def __init__(self, rag: RAGPipeline, store: SessionStore) -> None:
        self.rag = rag
        self.store = store
        self.config = rag.config

    def chat(self, session_id: str, question: str) -> ChatResponse:
        session = self.store.get_session(session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found.")

        question = question.strip()
        question_type = classify_question(question)
        prior_messages = self.store.get_messages(session_id)

        self.store.add_message(
            session_id,
            role="user",
            content=question,
            question_type=question_type.value,
        )

        if question_type == QuestionType.SESSION_NAME:
            response = self._handle_name(session_id, question, prior_messages)
        elif question_type == QuestionType.SESSION_RECAP:
            response = self._handle_recap(session_id, question)
        elif question_type == QuestionType.OUT_OF_SCOPE:
            response = self._handle_out_of_scope(session_id, question)
        else:
            response = self._handle_textbook(session_id, question, prior_messages)

        response = self._prepare_display_response(response)
        citations = [source.model_dump() for source in response.sources]
        self.store.add_message(
            session_id,
            role="assistant",
            content=response.answer,
            question_type=response.question_type,
            citations=citations,
        )
        return response

    @staticmethod
    def _prepare_display_response(response: ChatResponse) -> ChatResponse:
        trimmed_sources = best_source(response.sources)
        display_answer = format_display_answer(response.answer, trimmed_sources)
        return response.model_copy(update={
            "answer": display_answer,
            "sources": trimmed_sources,
        })

    def _handle_name(
        self,
        session_id: str,
        question: str,
        prior_messages: list,
    ) -> ChatResponse:
        if is_name_statement(question):
            name = extract_display_name(question)
            if not name:
                rag = self._refusal("I could not parse the name from your message.")
                return rag_to_chat(session_id, question, QuestionType.SESSION_NAME.value, rag)

            self.store.update_display_name(session_id, name)
            return ChatResponse(
                session_id=session_id,
                question=question,
                question_type=QuestionType.SESSION_NAME.value,
                answer=build_name_statement_answer(name),
                confidence="high",
                in_scope=True,
                sources=[],
            )

        session = self.store.get_session(session_id)
        assert session is not None
        answer, found = build_name_question_answer(session, prior_messages)

        if found and not session.user_display_name:
            name = extract_name_from_history(prior_messages)
            if name:
                self.store.update_display_name(session_id, name)

        return ChatResponse(
            session_id=session_id,
            question=question,
            question_type=QuestionType.SESSION_NAME.value,
            answer=answer,
            confidence="high" if found else "medium",
            in_scope=True,
            sources=[],
        )

    def _handle_recap(self, session_id: str, question: str) -> ChatResponse:
        questions = self.store.get_user_questions(session_id)
        if questions and questions[-1].strip().lower() == question.strip().lower():
            questions = questions[:-1]
        answer = build_recap_answer(questions)
        return ChatResponse(
            session_id=session_id,
            question=question,
            question_type=QuestionType.SESSION_RECAP.value,
            answer=answer,
            confidence="high",
            in_scope=True,
            sources=[],
        )

    def _handle_out_of_scope(self, session_id: str, question: str) -> ChatResponse:
        rag = RAGResponse(
            answer=(
                "I can only help with Essentials of Glycobiology textbook questions "
                "and this chat session. Please ask a glycobiology question from the course material."
            ),
            confidence="insufficient",
            in_scope=False,
            sources=[],
            refusal_reason="Question is outside glycobiology textbook scope.",
        )
        return rag_to_chat(session_id, question, QuestionType.OUT_OF_SCOPE.value, rag)

    def _handle_textbook(
        self,
        session_id: str,
        question: str,
        prior_messages: list,
    ) -> ChatResponse:
        name = extract_display_name(question)
        if name:
            self.store.update_display_name(session_id, name)

        enriched = enrich_query_with_history(question, prior_messages)
        rag_response = self.rag.ask(enriched)
        return rag_to_chat(
            session_id,
            question,
            QuestionType.TEXTBOOK_RAG.value,
            rag_response,
        )

    @staticmethod
    def _refusal(reason: str) -> RAGResponse:
        return RAGResponse(
            answer=reason,
            confidence="insufficient",
            in_scope=False,
            sources=[],
            refusal_reason=reason,
        )

    def get_session_messages(self, session_id: str) -> SessionMessagesResponse:
        session = self.store.get_session(session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found.")

        items: list[MessageItem] = []
        for message in self.store.get_messages(session_id):
            sources = []
            if message.citations_json:
                sources = json.loads(message.citations_json)
            items.append(
                MessageItem(
                    id=message.id,
                    role=message.role,
                    content=message.content,
                    question_type=message.question_type,
                    sources=sources,
                    created_at=message.created_at,
                )
            )

        return SessionMessagesResponse(
            session_id=session_id,
            user_display_name=session.user_display_name,
            messages=items,
        )

    def get_status(self) -> dict:
        config: RAGConfig = self.config
        return {
            "embedding_model": config.embedding_model,
            "reranker_model": config.reranker_model,
            "llm_model": config.llm_model,
            "collection_name": config.collection_name,
            "chroma_dir": str(config.chroma_dir),
            "chroma_host": os.getenv("CHROMA_HOST"),
        }
