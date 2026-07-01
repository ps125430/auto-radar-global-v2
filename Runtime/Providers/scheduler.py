"""Asia/Taipei Real Ocean schedule registration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True, slots=True)
class ScheduleEntry:
    trigger_id: str
    hour: int
    minute: int
    purpose: str


class RealOceanScheduler:
    """Register approved jobs; callers explicitly control scheduler start."""

    TIMEZONE = "Asia/Taipei"
    PLAN = (
        ScheduleEntry("us_close", 6, 0, "US market close"),
        ScheduleEntry("macro", 7, 0, "Macro refresh"),
        ScheduleEntry("taiwan_preopen", 8, 30, "Taiwan pre-open"),
        ScheduleEntry("taiwan_close", 15, 10, "Taiwan close"),
    )

    def __init__(
        self,
        runner: Callable[[str], object],
        *,
        scheduler: Any | None = None,
    ) -> None:
        self.runner = runner
        if scheduler is None:
            try:
                from apscheduler.schedulers.background import (
                    BackgroundScheduler,
                )
            except ModuleNotFoundError as exc:
                raise RuntimeError(
                    "apscheduler dependency is required to start scheduling"
                ) from exc
            scheduler = BackgroundScheduler(timezone=self.TIMEZONE)
        self.scheduler = scheduler

    def register(self) -> None:
        for entry in self.PLAN:
            self.scheduler.add_job(
                self.runner,
                "cron",
                args=(entry.trigger_id,),
                hour=entry.hour,
                minute=entry.minute,
                id=f"real_ocean_{entry.trigger_id}",
                replace_existing=True,
            )

    def start(self) -> None:
        if not self.scheduler.running:
            self.register()
            self.scheduler.start()
