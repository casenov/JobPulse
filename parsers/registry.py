"""
ParserRegistry — Plugin-based registry for all parsers.
New parsers register themselves automatically on import.
"""

from parsers.base import BaseParser


class ParserRegistry:
    _registry: dict[str, type[BaseParser]] = {}

    @classmethod
    def register(cls, parser_class: type[BaseParser]) -> type[BaseParser]:
        """
        Decorator to register a parser.

        Usage:
            @ParserRegistry.register
            class HHParser(BaseParser):
                source_slug = "hh"
        """
        slug = parser_class.source_slug
        if not slug:
            raise ValueError(f"{parser_class.__name__} must define source_slug")
        cls._registry[slug] = parser_class
        return parser_class

    @classmethod
    def get(cls, slug: str) -> type[BaseParser]:
        if slug not in cls._registry:
            raise KeyError(f"Parser '{slug}' is not registered. Available: {list(cls._registry)}")
        return cls._registry[slug]

    @classmethod
    def all(cls) -> dict[str, type[BaseParser]]:
        return dict(cls._registry)

    @classmethod
    def slugs(cls) -> list[str]:
        return list(cls._registry.keys())


# Auto-import all parsers so they register themselves
def autodiscover():
    """Call this once at startup to load all parser modules."""
    from parsers.sources import hh  # noqa: F401
    from parsers.sources import telegram_channels  # noqa: F401
