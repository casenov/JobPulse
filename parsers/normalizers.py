"""
Data Normalizer — Cleans and enriches raw vacancy data.

Responsibilities:
- Strip HTML tags
- Detect work format (remote/onsite/hybrid)
- Detect experience level (junior/middle/senior)
- Normalize salary currency
- Extract tech skills
"""

import re

REMOTE_KEYWORDS = ["remote", "удалённо", "удаленно", "из любой точки", "дистанционно", "wfh"]
HYBRID_KEYWORDS = ["гибрид", "hybrid", "частично удалённо"]
ONSITE_KEYWORDS = ["офис", "office", "on-site", "на месте"]

LEVEL_MAP = {
    "intern": ["intern", "стажёр", "стажер", "trainee"],
    "junior": ["junior", "джуниор", "джун", "начинающий", "jr."],
    "middle": ["middle", "мидл", "mid-level"],
    "senior": ["senior", "сеньор", "senior engineer", "sr."],
    "lead": ["lead", "team lead", "тимлид", "principal"],
}

TECH_SKILLS = [
    "python", "django", "fastapi", "flask", "postgresql", "mysql", "redis",
    "celery", "docker", "kubernetes", "git", "linux", "rest api", "graphql",
    "react", "vue", "typescript", "javascript", "go", "rust", "java",
    "spring", "kafka", "rabbitmq", "aws", "gcp", "azure", "nginx",
    "elasticsearch", "mongodb", "sqlalchemy", "pytest", "ci/cd",
]

HTML_TAG_RE = re.compile(r"<[^>]+>")
MULTIPLE_SPACES_RE = re.compile(r"\s{2,}")


def strip_html(text: str) -> str:
    """Remove HTML tags and normalize whitespace."""
    text = HTML_TAG_RE.sub(" ", text or "")
    text = MULTIPLE_SPACES_RE.sub(" ", text)
    return text.strip()


def detect_work_format(text: str) -> str:
    """Detect remote/hybrid/onsite from title + description."""
    text_lower = text.lower()
    if any(kw in text_lower for kw in HYBRID_KEYWORDS):
        return "hybrid"
    if any(kw in text_lower for kw in REMOTE_KEYWORDS):
        return "remote"
    if any(kw in text_lower for kw in ONSITE_KEYWORDS):
        return "onsite"
    return "not_specified"


def detect_experience_level(text: str) -> str:
    """Detect experience level from title + description."""
    text_lower = text.lower()
    for level, keywords in LEVEL_MAP.items():
        if any(kw in text_lower for kw in keywords):
            return level
    return "not_specified"


def extract_skills(text: str) -> list[str]:
    """Extract known tech skills mentioned in the text."""
    text_lower = text.lower()
    return [skill for skill in TECH_SKILLS if skill in text_lower]


CURRENCY_MAP = {
    "руб": "RUB", "р.": "RUB", "₽": "RUB", "rub": "RUB",
    "usd": "USD", "$": "USD",
    "eur": "EUR", "€": "EUR",
    "kzt": "KZT", "₸": "KZT",
}


def normalize_currency(raw: str) -> str:
    """Map various currency strings to ISO 4217."""
    if not raw:
        return "RUB"
    raw_lower = raw.lower().strip()
    for key, iso in CURRENCY_MAP.items():
        if key in raw_lower:
            return iso
    return raw.upper()[:10]
