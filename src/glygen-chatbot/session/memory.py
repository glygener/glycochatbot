import re

NAME_STATEMENT_PATTERNS = [
    re.compile(r"\bmy name is\s+([A-Za-z][A-Za-z'-]{0,30})(?:\s+and\b|[.,!?]|$)", re.I),
    re.compile(r"\bi am\s+([A-Za-z][A-Za-z'-]{0,30})(?:\s+and\b|[.,!?]|$)", re.I),
    re.compile(r"\bi'm\s+([A-Za-z][A-Za-z'-]{0,30})(?:\s+and\b|[.,!?]|$)", re.I),
    re.compile(r"\bcall me\s+([A-Za-z][A-Za-z'-]{0,30})(?:\s+and\b|[.,!?]|$)", re.I),
]

NAME_QUESTION_PATTERNS = [
    re.compile(r"\bwhat(?:'s| is) my name\b", re.I),
    re.compile(r"\bwho am i\b", re.I),
    re.compile(r"\bdo you know my name\b", re.I),
]

RECAP_PATTERNS = [
    re.compile(r"\bwhat did i ask\b", re.I),
    re.compile(r"\bwhat have i asked\b", re.I),
    re.compile(r"\bmy (?:previous|earlier|last) question\b", re.I),
    re.compile(r"\bwhat was my (?:first|last) question\b", re.I),
    re.compile(r"\bquestions? i asked\b", re.I),
    re.compile(r"\bconversation history\b", re.I),
]

FOLLOW_UP_PATTERNS = [
    re.compile(r"\btell me more\b", re.I),
    re.compile(r"\bmore about (?:that|this|it)\b", re.I),
    re.compile(r"\bexplain (?:that|this|it) (?:more|further)\b", re.I),
    re.compile(r"\belaborate\b", re.I),
]

GLYCO_KEYWORDS = {
    "glycan", "glycobiology", "glycoprotein", "glycolipid", "glycosylation",
    "sialic", "fucose", "mannose", "glcnac", "galnac", "lectin", "oligosaccharide",
    "monosaccharide", "polysaccharide", "ncbi", "essentials of glycobiology",
    "n-linked", "o-linked", "glycogen", "heparin", "chondroitin",
}

OUT_OF_SCOPE_PATTERNS = [
    re.compile(r"\bwrite (?:me )?(?:code|a script|python|javascript)\b", re.I),
    re.compile(r"\bweather\b", re.I),
    re.compile(r"\bstock price\b", re.I),
    re.compile(r"\bfootball\b", re.I),
    re.compile(r"\brecipe\b", re.I),
]


def extract_display_name(message: str) -> str | None:
    for pattern in NAME_STATEMENT_PATTERNS:
        match = pattern.search(message)
        if match:
            return match.group(1).strip().rstrip(".,!?")
    return None


def is_name_statement(message: str) -> bool:
    return extract_display_name(message) is not None


def is_name_question(message: str) -> bool:
    return any(pattern.search(message) for pattern in NAME_QUESTION_PATTERNS)


def is_recap_question(message: str) -> bool:
    return any(pattern.search(message) for pattern in RECAP_PATTERNS)


def is_follow_up(message: str) -> bool:
    return any(pattern.search(message) for pattern in FOLLOW_UP_PATTERNS)


def is_likely_glyco_topic(message: str) -> bool:
    lowered = message.lower()
    return any(keyword in lowered for keyword in GLYCO_KEYWORDS)


def is_out_of_scope(message: str) -> bool:
    if is_likely_glyco_topic(message):
        return False
    if is_name_statement(message) or is_name_question(message) or is_recap_question(message):
        return False
    return any(pattern.search(message) for pattern in OUT_OF_SCOPE_PATTERNS)


def build_recap_answer(questions: list[str]) -> str:
    if not questions:
        return "You have not asked any questions in this session yet."
    if len(questions) == 1:
        return f'You have asked one question so far: "{questions[0]}"'
    lines = [f"{index}. {question}" for index, question in enumerate(questions, start=1)]
    return "Here are the questions you have asked in this session:\n" + "\n".join(lines)
