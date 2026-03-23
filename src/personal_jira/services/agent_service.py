from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.config import settings
from personal_jira.models.agent import Agent, AgentTask, AgentStatus, TaskResult
from personal_jira.models.work_log import WorkLog
from personal_jira.models.code_artifact import CodeArtifact, ArtifactType

TASK_DEADLINE_MINUTES = 30


class AgentService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def claim_task(self, agent_id: UUID, issue_id: UUID) -> Optional[AgentTask]:
        existing = await self._session.execute(
            select(AgentTask).where(
                AgentTask.issue_id == issue_id,
                AgentTask.result == TaskResult.IN_PROGRESS,
            )
        )
        if existing.scalar_one_or_none() is not None:
            return None

        task = AgentTask(
            agent_id=agent_id,
            issue_id=issue_id,
            result=TaskResult.IN_PROGRESS,
            deadline=datetime.now(timezone.utc) + timedelta(minutes=TASK_DEADLINE_MINUTES),
        )
        self._session.add(task)

        agent = await self._session.get(Agent, agent_id)
        if agent:
            agent.status = AgentStatus.BUSY

        await self._session.commit()
        await self._session.refresh(task)
        return task

    async def fail_task(self, task_id: UUID, error_message: str) -> AgentTask:
        task = await self._session.get(AgentTask, task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")
        task.result = TaskResult.FAILED
        task.error_message = error_message
        task.attempt_count = (task.attempt_count or 0) + 1 if task.attempt_count and task.attempt_count > 1 else 1

        agent = await self._session.get(Agent, task.agent_id)
        if agent:
            agent.status = AgentStatus.IDLE

        await self._session.commit()
        await self._session.refresh(task)
        return task

    async def retry_task(self, task_id: UUID) -> Optional[AgentTask]:
        old_task = await self._session.get(AgentTask, task_id)
        if old_task is None:
            raise ValueError(f"Task {task_id} not found")

        if old_task.attempt_count >= settings.MAX_RETRY_ATTEMPTS:
            return None

        new_task = AgentTask(
            agent_id=old_task.agent_id,
            issue_id=old_task.issue_id,
            result=TaskResult.IN_PROGRESS,
            attempt_count=old_task.attempt_count + 1,
            deadline=datetime.now(timezone.utc) + timedelta(minutes=TASK_DEADLINE_MINUTES),
        )
        self._session.add(new_task)

        agent = await self._session.get(Agent, old_task.agent_id)
        if agent:
            agent.status = AgentStatus.BUSY

        await self._session.commit()
        await self._session.refresh(new_task)
        return new_task

    async def add_work_log(
        self,
        task_id: UUID,
        summary: str,
        llm_calls: int = 0,
        tokens_used: int = 0,
    ) -> WorkLog:
        task = await self._session.get(AgentTask, task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")

        log = WorkLog(
            issue_id=task.issue_id,
            agent_id=task.agent_id,
            agent_task_id=task.id,
            summary=summary,
            llm_calls=llm_calls,
            tokens_used=tokens_used,
        )
        self._session.add(log)
        await self._session.commit()
        await self._session.refresh(log)
        return log

    async def get_work_logs(self, task_id: UUID) -> list[WorkLog]:
        result = await self._session.execute(
            select(WorkLog).where(WorkLog.agent_task_id == task_id)
        )
        return list(result.scalars().all())

    async def add_artifact(
        self,
        task_id: UUID,
        file_path: str,
        content: str,
        artifact_type: ArtifactType,
    ) -> CodeArtifact:
        task = await self._session.get(AgentTask, task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")

        artifact = CodeArtifact(
            issue_id=task.issue_id,
            agent_task_id=task.id,
            file_path=file_path,
            content=content,
            artifact_type=artifact_type,
        )
        self._session.add(artifact)
        await self._session.commit()
        await self._session.refresh(artifact)
        return artifact

    async def get_artifacts(self, task_id: UUID) -> list[CodeArtifact]:
        result = await self._session.execute(
            select(CodeArtifact).where(CodeArtifact.agent_task_id == task_id)
        )
        return list(result.scalars().all())

    async def submit_for_review(self, task_id: UUID, summary: str) -> AgentTask:
        task = await self._session.get(AgentTask, task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")
        task.result = TaskResult.IN_REVIEW
        task.summary = summary
        await self._session.commit()
        await self._session.refresh(task)
        return task

    async def approve_review(self, task_id: UUID, feedback: str) -> AgentTask:
        task = await self._session.get(AgentTask, task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")
        task.result = TaskResult.APPROVED
        task.feedback = feedback

        agent = await self._session.get(Agent, task.agent_id)
        if agent:
            agent.status = AgentStatus.IDLE

        await self._session.commit()
        await self._session.refresh(task)
        return task

    async def reject_review(self, task_id: UUID, feedback: str) -> AgentTask:
        task = await self._session.get(AgentTask, task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")
        task.result = TaskResult.CHANGES_REQUESTED
        task.feedback = feedback
        task.review_count = (task.review_count or 0) + 1
        await self._session.commit()
        await self._session.refresh(task)
        return task

    async def get_expired_tasks(self) -> list[AgentTask]:
        now = datetime.now(timezone.utc)
        result = await self._session.execute(
            select(AgentTask).where(
                AgentTask.deadline < now,
                AgentTask.result == TaskResult.IN_PROGRESS,
            )
        )
        return list(result.scalars().all())

    async def timeout_expired_tasks(self) -> list[AgentTask]:
        expired = await self.get_expired_tasks()
        for task in expired:
            task.result = TaskResult.TIMED_OUT
            agent = await self._session.get(Agent, task.agent_id)
            if agent:
                agent.status = AgentStatus.IDLE
        await self._session.commit()
        return expired

    async def get_agent_metrics(self, agent_id: UUID) -> dict:
        tasks_result = await self._session.execute(
            select(AgentTask).where(AgentTask.agent_id == agent_id)
        )
        tasks = list(tasks_result.scalars().all())

        total = len(tasks)
        successful = sum(1 for t in tasks if t.result == TaskResult.APPROVED)
        failed = sum(1 for t in tasks if t.result == TaskResult.FAILED)

        logs_result = await self._session.execute(
            select(WorkLog).where(WorkLog.agent_id == agent_id)
        )
        logs = list(logs_result.scalars().all())
        total_llm_calls = sum(log.llm_calls or 0 for log in logs)
        total_tokens = sum(log.tokens_used or 0 for log in logs)

        review_rounds = [t.review_count for t in tasks if t.review_count and t.review_count > 0]
        avg_review = sum(review_rounds) / len(review_rounds) if review_rounds else 0.0

        return {
            "total_tasks": total,
            "successful_tasks": successful,
            "failed_tasks": failed,
            "success_rate": successful / total if total > 0 else 0.0,
            "total_llm_calls": total_llm_calls,
            "total_tokens_used": total_tokens,
            "avg_review_rounds": avg_review,
        }
