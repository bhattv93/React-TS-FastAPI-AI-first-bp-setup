"""Fakes that stand in for infrastructure in unit tests."""

from typing import Any


class FakeSession:
    """Minimal stand-in for ``AsyncSession`` that records or fails ``execute``."""

    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.executed: list[Any] = []

    async def execute(self, statement: Any) -> None:
        """Record the statement, or raise when configured to fail."""
        if self.fail:
            raise RuntimeError("database is down")
        self.executed.append(statement)
