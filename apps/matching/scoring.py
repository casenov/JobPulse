"""
Matching Engine — Score-based vacancy ↔ filter matcher.

Algorithm:
    score = keyword_score * 0.5
          + location_score * 0.2
          + salary_score   * 0.2
          + experience_score * 0.1

All sub-scores are normalized to [0.0, 1.0].
"""

import logging
from dataclasses import dataclass

from apps.filters.models import UserFilter
from apps.vacancies.models import Vacancy

logger = logging.getLogger(__name__)

WEIGHTS = {
    "keyword": 0.50,
    "location": 0.20,
    "salary": 0.20,
    "experience": 0.10,
}

MIN_SCORE_THRESHOLD = 0.3  # matches below this are ignored


@dataclass
class ScoreResult:
    total: float
    keyword: float
    location: float
    salary: float
    experience: float

    def to_dict(self):
        return {
            "score": round(self.total, 4),
            "keyword_score": round(self.keyword, 4),
            "location_score": round(self.location, 4),
            "salary_score": round(self.salary, 4),
            "experience_score": round(self.experience, 4),
        }


def score_keywords(vacancy: Vacancy, user_filter: UserFilter) -> float:
    """
    Check keyword match against title + description.
    Returns 1.0 if at least one keyword matches, 0.0 if none.
    Also returns 0.0 if excluded keywords are found.
    """
    if not user_filter.keywords:
        return 1.0  # no keywords = all vacancies match

    text = f"{vacancy.title} {vacancy.description}".lower()

    # Exclusions first — hard reject
    for kw in user_filter.excluded_keywords:
        if kw.lower() in text:
            return 0.0

    matched = sum(1 for kw in user_filter.keywords if kw.lower() in text)
    return min(1.0, matched / max(len(user_filter.keywords), 1))


def score_location(vacancy: Vacancy, user_filter: UserFilter) -> float:
    """
    Check location match.
    Remote vacancies always match.
    """
    from apps.vacancies.models import WorkFormat

    if vacancy.work_format == WorkFormat.REMOTE:
        return 1.0

    if not user_filter.locations:
        return 1.0  # no location preference = all match

    vacancy_location = (vacancy.location_normalized or vacancy.location_raw or "").lower()
    for loc in user_filter.locations:
        if loc.lower() in vacancy_location:
            return 1.0
    return 0.0


def score_salary(vacancy: Vacancy, user_filter: UserFilter) -> float:
    """
    Check if vacancy salary meets minimum requirement.
    """
    if not user_filter.salary_min:
        return 1.0  # no preference

    if not vacancy.salary_from and not vacancy.salary_to:
        return 0.5  # salary not disclosed — neutral

    vacancy_max = vacancy.salary_to or vacancy.salary_from or 0
    if vacancy_max >= user_filter.salary_min:
        return 1.0

    # Partial score if close (within 20%)
    ratio = vacancy_max / user_filter.salary_min
    return max(0.0, ratio)


def score_experience(vacancy: Vacancy, user_filter: UserFilter) -> float:
    """
    Check experience level match.
    """
    from apps.vacancies.models import ExperienceLevel

    if not user_filter.experience_level:
        return 1.0  # no preference

    if vacancy.experience_level == ExperienceLevel.NOT_SPECIFIED:
        return 0.5  # unknown = neutral

    if vacancy.experience_level == user_filter.experience_level:
        return 1.0

    return 0.0


def compute_score(vacancy: Vacancy, user_filter: UserFilter) -> ScoreResult:
    """
    Compute overall match score between a vacancy and a user filter.
    """
    kw = score_keywords(vacancy, user_filter)
    loc = score_location(vacancy, user_filter)
    sal = score_salary(vacancy, user_filter)
    exp = score_experience(vacancy, user_filter)

    total = (
        kw * WEIGHTS["keyword"]
        + loc * WEIGHTS["location"]
        + sal * WEIGHTS["salary"]
        + exp * WEIGHTS["experience"]
    )

    return ScoreResult(
        total=round(total, 4),
        keyword=kw,
        location=loc,
        salary=sal,
        experience=exp,
    )
