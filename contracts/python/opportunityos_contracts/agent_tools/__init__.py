"""Agent task, execution and tool contracts (agent-tools/, ADR-021)."""

from opportunityos_contracts.agent_tools.execution import (
    AgentResult,
    ContextEnvelope,
    TaskContract,
    TaskType,
)
from opportunityos_contracts.agent_tools.task_io import DiagnosticEchoInput, DiagnosticEchoOutput
from opportunityos_contracts.agent_tools.tasks import TaskDefinition, TasksManifest

__all__ = [
    "AgentResult",
    "ContextEnvelope",
    "DiagnosticEchoInput",
    "DiagnosticEchoOutput",
    "TaskContract",
    "TaskDefinition",
    "TaskType",
    "TasksManifest",
]
