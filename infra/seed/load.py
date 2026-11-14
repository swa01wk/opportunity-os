"""Idempotent synthetic seed: workspace, identities, brand kit v1, odd-squares project (SPEC-04)."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import uuid
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

WORKSPACE_ID = uuid.UUID("00000000-0000-4000-8000-000000000001")
PLACEHOLDER_MEMBER_ID = uuid.UUID("00000000-0000-4000-8000-000000000002")
BRAND_KIT_ID = uuid.UUID("00000000-0000-4000-8000-000000000023")
PROJECT_ID = uuid.UUID("00000000-0000-4000-8000-000000000010")

WORKSPACE_NAME = "Signal Motion (working name)"
PROJECT_TITLE = "Why Odd Numbers Build Perfect Squares"

# Placeholder house-style tokens (R-23); SHA-256 of canonical JSON for the row.
BRAND_KIT_TOKENS_V1: dict[str, Any] = {
    "schemaVersion": "0.1.0",
    "palette": {
        "color.canvas": "#070D1A",
        "color.layer.1": "#1F5FD6",
        "color.layer.2": "#00A383",
        "color.layer.3": "#FFE04A",
        "color.layer.4": "#E45A3C",
        "color.layer.5": "#9A7FEA",
    },
    "typography": {"family.sans": "Atkinson Hyperlegible Next"},
    "caption": {"placement": "bottom_safe"},
}

SERVICE_IDENTITIES: tuple[tuple[str, str], ...] = (
    ("oos-api", "service"),
    ("oos-worker", "service"),
    ("oos-render", "service"),
    ("oos-retention", "service"),
)


def _canonical_sha256(document: dict[str, Any]) -> str:
    raw = json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _refuse_production() -> None:
    if os.environ.get("APP_ENV") == "production":
        print("make seed: refused when APP_ENV=production", file=sys.stderr)
        raise SystemExit(1)


def _engine() -> Engine:
    url = os.environ.get("MIGRATE_DATABASE_URL") or os.environ.get("DATABASE_URL")
    if not url:
        print("seed: MIGRATE_DATABASE_URL or DATABASE_URL is required", file=sys.stderr)
        raise SystemExit(1)
    return create_engine(url)


def _upsert_workspace(conn) -> None:
    conn.execute(
        text(
            """
            INSERT INTO app.workspace (id, name, reporting_currency)
            VALUES (:id, :name, 'INR')
            ON CONFLICT (id) DO UPDATE
            SET name = EXCLUDED.name
            WHERE app.workspace.name IS DISTINCT FROM EXCLUDED.name
            """
        ),
        {"id": WORKSPACE_ID, "name": WORKSPACE_NAME},
    )


def _upsert_service_identities(conn) -> None:
    for ident, kind in SERVICE_IDENTITIES:
        conn.execute(
            text(
                """
                INSERT INTO app.service_identity (id, kind)
                VALUES (:id, :kind)
                ON CONFLICT (id) DO UPDATE
                SET kind = EXCLUDED.kind
                WHERE app.service_identity.kind IS DISTINCT FROM EXCLUDED.kind
                """
            ),
            {"id": ident, "kind": kind},
        )


def _upsert_brand_kit(conn) -> None:
    tokens = BRAND_KIT_TOKENS_V1
    sha = _canonical_sha256(tokens)
    conn.execute(
        text(
            """
            INSERT INTO app.brand_kit (id, workspace_id, name, head_version, row_version)
            VALUES (:id, :ws, 'House style v1', 1, 1)
            ON CONFLICT (id) DO UPDATE
            SET name = EXCLUDED.name,
                head_version = EXCLUDED.head_version,
                row_version = EXCLUDED.row_version
            WHERE app.brand_kit.name IS DISTINCT FROM EXCLUDED.name
               OR app.brand_kit.head_version IS DISTINCT FROM EXCLUDED.head_version
               OR app.brand_kit.row_version IS DISTINCT FROM EXCLUDED.row_version
            """
        ),
        {"id": BRAND_KIT_ID, "ws": WORKSPACE_ID},
    )
    conn.execute(
        text(
            """
            INSERT INTO app.brand_kit_version (
                brand_kit_id, version, workspace_id, tokens, sha256, created_by
            )
            VALUES (:bk, 1, :ws, CAST(:tokens AS jsonb), :sha, :member)
            ON CONFLICT (brand_kit_id, version) DO NOTHING
            """
        ),
        {
            "bk": BRAND_KIT_ID,
            "ws": WORKSPACE_ID,
            "tokens": json.dumps(tokens),
            "sha": sha,
            "member": PLACEHOLDER_MEMBER_ID,
        },
    )


def _upsert_project(conn) -> None:
    narrator = {"provider": "fake", "voice_id": "synthetic", "settings": {}}
    conn.execute(
        text(
            """
            INSERT INTO app.project (
                id, workspace_id, title, series, state, brand_kit_id, brand_kit_version,
                narrator, row_version
            )
            VALUES (
                :id, :ws, :title, 'solve_this', 'DRAFT', :bk, 1,
                CAST(:narrator AS jsonb), 1
            )
            ON CONFLICT (id) DO UPDATE
            SET title = EXCLUDED.title,
                series = EXCLUDED.series,
                state = EXCLUDED.state,
                brand_kit_id = EXCLUDED.brand_kit_id,
                brand_kit_version = EXCLUDED.brand_kit_version,
                narrator = EXCLUDED.narrator
            WHERE app.project.title IS DISTINCT FROM EXCLUDED.title
               OR app.project.series IS DISTINCT FROM EXCLUDED.series
               OR app.project.state IS DISTINCT FROM EXCLUDED.state
               OR app.project.brand_kit_id IS DISTINCT FROM EXCLUDED.brand_kit_id
               OR app.project.brand_kit_version IS DISTINCT FROM EXCLUDED.brand_kit_version
               OR app.project.narrator IS DISTINCT FROM EXCLUDED.narrator
            """
        ),
        {
            "id": PROJECT_ID,
            "ws": WORKSPACE_ID,
            "title": PROJECT_TITLE,
            "bk": BRAND_KIT_ID,
            "narrator": json.dumps(narrator),
        },
    )


def run() -> None:
    _refuse_production()
    engine = _engine()
    with engine.connect() as conn, conn.begin():
        conn.execute(text("SET LOCAL ROLE oos_migrator"))
        conn.execute(
            text("SELECT set_config('app.workspace_id', :wid, true)"),
            {"wid": str(WORKSPACE_ID)},
        )
        _upsert_workspace(conn)
        _upsert_service_identities(conn)
        # Placeholder member for brand_kit_version FK; owner row is SPEC-06.
        conn.execute(
            text(
                """
                    INSERT INTO app.member (
                        id, workspace_id, idp_issuer, idp_subject, display_name, responsibilities
                    )
                    VALUES (
                        :id, :ws, 'seed', 'placeholder-not-owner',
                        'Seed placeholder (SPEC-06 adds owner)', '{}'::text[]
                    )
                    ON CONFLICT (id) DO NOTHING
                    """
            ),
            {"id": PLACEHOLDER_MEMBER_ID, "ws": WORKSPACE_ID},
        )
        _upsert_brand_kit(conn)
        _upsert_project(conn)


def main() -> None:
    run()
    print("seed: synthetic fixtures loaded")


if __name__ == "__main__":
    main()
