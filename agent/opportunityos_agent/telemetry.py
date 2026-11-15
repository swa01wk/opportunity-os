"""Agent tasks use the worker's OpenTelemetry provider (SPEC-08)."""


def init() -> None:
    """No-op: the worker entry point configures tracing before dispatching agent tasks."""
