from session.memory import extract_display_name
from session.router import QuestionType
from session.store import MessageRecord, SessionRecord


def enrich_query_with_history(question: str, messages: list[MessageRecord]) -> str:
    last_textbook_question = None
    for message in reversed(messages):
        if message.role != "user":
            continue
        if message.question_type in (None, QuestionType.TEXTBOOK_RAG.value):
            last_textbook_question = message.content
            break

    if not last_textbook_question:
        return question

    lowered = question.lower()
    if any(token in lowered for token in ("that", "this", "it", "more about", "elaborate")):
        return f"{question}\n\nContext from earlier in this session: {last_textbook_question}"
    return question


def build_name_statement_answer(name: str) -> str:
    return (
        f"Nice to meet you, {name}. I am GlyGen Tutor for Essentials of Glycobiology. "
        "Ask me any glycobiology question from the textbook."
    )


def build_name_question_answer(
    session: SessionRecord,
    messages: list[MessageRecord],
) -> tuple[str, bool]:
    name = session.user_display_name or extract_name_from_history(messages)
    if name:
        return f"Your name is {name}.", True
    return "You have not told me your name in this session yet.", False


def extract_name_from_history(messages: list[MessageRecord]) -> str | None:
    for message in messages:
        if message.role != "user":
            continue
        name = extract_display_name(message.content)
        if name:
            return name
    return None
