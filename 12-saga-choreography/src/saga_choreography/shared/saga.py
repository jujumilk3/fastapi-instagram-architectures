from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from saga_choreography.models.tables import SagaLog


@dataclass
class SagaStep:
    name: str
    action: Callable
    compensation: Callable | None = None


class SagaExecutor:
    async def execute(
        self,
        saga_id: str,
        saga_type: str,
        steps: list[SagaStep],
        context: dict[str, Any],
        db: AsyncSession,
    ) -> dict[str, Any]:
        completed: list[SagaStep] = []
        try:
            for step in steps:
                await self._log_step(db, saga_id, saga_type, step.name, "started")
                result = await step.action(context)
                if result is not None:
                    context[f"{step.name}_result"] = result
                await self._log_step(db, saga_id, saga_type, step.name, "completed")
                completed.append(step)
        except Exception:
            for comp_step in reversed(completed):
                if comp_step.compensation:
                    await self._log_step(db, saga_id, saga_type, comp_step.name, "compensating")
                    try:
                        await comp_step.compensation(context)
                    except Exception:
                        await self._log_step(db, saga_id, saga_type, comp_step.name, "compensation_failed")
                    else:
                        await self._log_step(db, saga_id, saga_type, comp_step.name, "compensated")
            raise
        return context

    async def _log_step(
        self,
        db: AsyncSession,
        saga_id: str,
        saga_type: str,
        step_name: str,
        status: str,
    ) -> None:
        log_entry = SagaLog(
            saga_id=saga_id,
            saga_type=saga_type,
            step_name=step_name,
            status=status,
        )
        db.add(log_entry)
        await db.flush()


saga_executor = SagaExecutor()
