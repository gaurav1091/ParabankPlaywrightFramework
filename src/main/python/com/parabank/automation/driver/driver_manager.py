import threading
from typing import Any


class DriverManager:
    _storage = threading.local()

    @classmethod
    def set_playwright(cls, playwright: Any) -> None:
        cls._storage.playwright = playwright

    @classmethod
    def get_playwright(cls) -> Any | None:
        return getattr(cls._storage, "playwright", None)

    @classmethod
    def set_browser(cls, browser: Any) -> None:
        cls._storage.browser = browser

    @classmethod
    def get_browser(cls) -> Any | None:
        return getattr(cls._storage, "browser", None)

    @classmethod
    def set_context(cls, context: Any) -> None:
        cls._storage.context = context

    @classmethod
    def get_context(cls) -> Any | None:
        return getattr(cls._storage, "context", None)

    @classmethod
    def set_page(cls, page: Any) -> None:
        cls._storage.page = page

    @classmethod
    def get_page(cls) -> Any | None:
        return getattr(cls._storage, "page", None)

    @classmethod
    def clear_page(cls) -> None:
        if hasattr(cls._storage, "page"):
            del cls._storage.page

    @classmethod
    def clear_context(cls) -> None:
        if hasattr(cls._storage, "context"):
            del cls._storage.context

    @classmethod
    def clear_browser(cls) -> None:
        if hasattr(cls._storage, "browser"):
            del cls._storage.browser

    @classmethod
    def clear_playwright(cls) -> None:
        if hasattr(cls._storage, "playwright"):
            del cls._storage.playwright

    @classmethod
    def clear_all(cls) -> None:
        cls.clear_page()
        cls.clear_context()
        cls.clear_browser()
        cls.clear_playwright()
