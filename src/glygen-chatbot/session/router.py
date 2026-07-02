from enum import Enum

from session.memory import (
    is_follow_up,
    is_name_question,
    is_name_statement,
    is_out_of_scope,
    is_recap_question,
    is_likely_glyco_topic,
)


class QuestionType(str, Enum):
    SESSION_NAME = "session_name"
    SESSION_RECAP = "session_recap"
    TEXTBOOK_RAG = "textbook_rag"
    OUT_OF_SCOPE = "out_of_scope"


def classify_question(question: str) -> QuestionType:
    if is_recap_question(question):
        return QuestionType.SESSION_RECAP
    if is_likely_glyco_topic(question):
        return QuestionType.TEXTBOOK_RAG
    if is_name_statement(question) or is_name_question(question):
        return QuestionType.SESSION_NAME
    if is_out_of_scope(question):
        return QuestionType.OUT_OF_SCOPE
    if is_follow_up(question):
        return QuestionType.TEXTBOOK_RAG
    return QuestionType.TEXTBOOK_RAG
