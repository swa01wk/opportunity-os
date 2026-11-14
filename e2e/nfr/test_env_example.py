"""T-31 static check for AC3 (NFR-06): .env.example covers the SECURITY.md inventory
with placeholders only, .env is git-ignored and make setup never overwrites it."""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

from nfr_support import read_env_file

SECRET_NAME = re.compile(r"PASSWORD|SECRET|_KEY|TOKEN")
SECRET_VALUE = [
    re.compile(p)
    for p in (
        r"sk-[A-Za-z0-9_-]{16,}",  # OpenAI-style keys
        r"AKIA[0-9A-Z]{16}",  # AWS access key IDs
        r"gh[pousr]_[A-Za-z0-9]{20,}",  # GitHub tokens
        r"xox[abprs]-",  # Slack tokens
        r"eyJ[A-Za-z0-9_-]{10,}\.",  # JWTs
        r"-----BEGIN",  # PEM keys
    )
]
OPAQUE = re.compile(r"^[A-Za-z0-9+/=_-]{32,}$")  # long random-looking values


def inventory_keys(security_md: str) -> set[str]:
    """Key names from the 'Inventory' bullet of SECURITY.md#secrets-and-credentials."""
    line = next(line for line in security_md.splitlines() if line.startswith("- **Inventory**"))
    keys = set(re.findall(r"`([A-Z][A-Z0-9_]+)`", line))
    groups = {
        "DB_PASSWORD_{}": r"per-service DB passwords \(([^)]*)\)",
        "STORAGE_ACCESS_KEY_{}": r"per-service storage keys \(([^)]*)\)",
        "STORAGE_SECRET_KEY_{}": r"per-service storage keys \(([^)]*)\)",
    }
    for template, pattern in groups.items():
        match = re.search(pattern, line)
        assert match, f"inventory wording changed: {pattern}"
        for name in re.findall(r"`([a-z_]+)`", match.group(1)):
            keys.add(template.format(name.upper()))
    if "YouTube OAuth client credentials" in line:
        keys |= {"YOUTUBE_OAUTH_CLIENT_ID", "YOUTUBE_OAUTH_CLIENT_SECRET"}
    return keys


@pytest.mark.t("T-31")
def test_env_example_holds_every_inventory_key(root: Path) -> None:
    expected = inventory_keys((root / "docs/architecture/SECURITY.md").read_text())
    assert len(expected) >= 20
    missing = expected - read_env_file(root / ".env.example").keys()
    assert not missing, f"missing from .env.example: {sorted(missing)}"


@pytest.mark.t("T-31")
def test_env_example_has_feature_flags_and_app_env(root: Path) -> None:
    env = read_env_file(root / ".env.example")
    assert env["APP_ENV"] == "dev"
    assert env["FEATURE_DIAGNOSTICS"] == "1"  # A-43


@pytest.mark.t("T-31")
def test_env_example_holds_no_real_secret(root: Path) -> None:
    for key, value in read_env_file(root / ".env.example").items():
        if SECRET_NAME.search(key):
            assert value == "" or value.startswith("change-me-"), f"{key} is not a placeholder"
        for pattern in SECRET_VALUE:
            assert not pattern.search(value), f"{key} looks like a real secret"
        if not value.startswith("change-me-"):
            assert not OPAQUE.match(value), f"{key} looks like a real secret"


@pytest.mark.t("T-31")
def test_dotenv_is_git_ignored(root: Path) -> None:
    lines = (root / ".gitignore").read_text().splitlines()
    assert ".env" in lines
    assert "!.env.example" in lines


@pytest.mark.t("T-31")
def test_setup_never_overwrites_an_existing_env(root: Path, tmp_path: Path) -> None:
    for name in ("Makefile", ".env.example", "infra/images.env"):
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(root / name, tmp_path / name)
    env = tmp_path / ".env"
    env.write_text("OPENAI_API_KEY=kept-by-the-owner\n")
    subprocess.run(["make", "-s", "_env-file"], cwd=tmp_path, check=True)
    assert env.read_text() == "OPENAI_API_KEY=kept-by-the-owner\n"

    env.unlink()
    subprocess.run(["make", "-s", "_env-file"], cwd=tmp_path, check=True)
    assert env.read_text() == (root / ".env.example").read_text()
