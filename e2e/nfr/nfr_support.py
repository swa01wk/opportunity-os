"""Helpers for the SPEC-01a static checks (T-31)."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read_env_file(path: Path) -> dict[str, str]:
    pairs = {}
    for line in path.read_text().splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            key, _, value = line.partition("=")
            pairs[key.strip()] = value.strip()
    return pairs


def interpolate(text: str, values: dict[str, str]) -> str:
    """Resolve Compose-style ${NAME}, ${NAME:-x} and ${NAME:?msg} from the given values."""
    return re.sub(
        r"\$\{([A-Z0-9_]+)(?::[-?][^}]*)?\}", lambda m: values.get(m.group(1), m.group(0)), text
    )
