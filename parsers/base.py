"""
BaseParser — Abstract class for all parsers.
Every new source must implement this interface.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class VacancyDTO:
    """
    Data Transfer Object — normalized vacancy data.
    This is what every parser must return.
    """

    external_id: str
    title: str
    url: str
    source_slug: str

    description: str = ""
    company_name: str = ""
    company_meta: dict = field(default_factory=dict)

    location_raw: str = ""
    salary_from: Optional[int] = None
    salary_to: Optional[int] = None
    currency: str = "RUB"

    employment_type: str = "full_time"
    work_format: str = "not_specified"
    experience_level: str = "not_specified"

    skills: list = field(default_factory=list)
    published_at: Optional[datetime] = None

    def __post_init__(self):
        # Basic sanitization
        self.title = self.title.strip()[:500]
        self.url = self.url.strip()[:2048]
        self.company_name = self.company_name.strip()[:255]
        self.location_raw = self.location_raw.strip()[:500]


class BaseParser(ABC):
    """
    Abstract base parser.
    All parsers must implement fetch() and normalize().
    """

    source_slug: str  # must be defined in subclass

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}"
        )

    @abstractmethod
    def fetch(self, page: int = 0, **kwargs) -> list[dict]:
        """
        Fetch raw data from the source.
        Returns list of raw dicts (JSON/parsed HTML).
        """
        ...

    @abstractmethod
    def normalize(self, raw: dict) -> Optional[VacancyDTO]:
        """
        Normalize a single raw item into VacancyDTO.
        Returns None if the item should be skipped.
        """
        ...

    def get_total_pages(self) -> int:
        """
        Override if the source supports pagination.
        Returns 1 by default.
        """
        return 1

    def validate(self, dto: VacancyDTO) -> bool:
        """
        Basic validation. Override for source-specific rules.
        """
        return bool(dto.title and dto.url and dto.external_id)
