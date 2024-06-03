from dataclasses import dataclass
from datetime import datetime
from typing import Self
from zoneinfo import ZoneInfo

__all__ = ('Period',)


@dataclass(frozen=True, slots=True)
class Period:
    start: datetime
    end: datetime

    @classmethod
    def today(cls, timezone: ZoneInfo | None = None) -> Self:
        now = datetime.now(timezone)
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return cls(start=start, end=now)
