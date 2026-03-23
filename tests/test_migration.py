import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.pool import StaticPool
from alembic.config import Config
from alembic import command
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ALEMBIC_INI = PROJECT_ROOT / "alembic.ini"

EXPECTED_TABLES = {"issues", "work_logs", "code_artifacts"}

ISSUE_COLUMNS = {
    "id", "title", "description", "priority", "status",
    "parent_id", "created_at", "updated_at",
}

WORK_LOG_COLUMNS = {
    "id", "issue_id", "agent_id", "summary",
    "llm_calls", "tokens_used", "created_at", "updated_at",
}

CODE_ARTIFACT_COLUMNS = {
    "id", "work_log_id", "file_path", "content",
    "artifact_type", "created_at", "updated_at",
}


@pytest.fixture()
def alembic_cfg() -> Config:
    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option(
        "sqlalchemy.url",
        "sqlite://",
    )
    return cfg


@pytest.fixture()
def engine():
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    yield eng
    eng.dispose()


@pytest.fixture()
def upgraded_engine(engine, alembic_cfg: Config):
    alembic_cfg.set_main_option("sqlalchemy.url", "sqlite://")
    alembic_cfg.attributes["connection"] = engine.connect()
    with engine.connect() as conn:
        alembic_cfg.attributes["connection"] = conn
        command.upgrade(alembic_cfg, "head")
        conn.commit()
    return engine


class TestMigrationUpgrade:
    def test_upgrade_creates_all_tables(
        self, upgraded_engine
    ) -> None:
        insp = inspect(upgraded_engine)
        tables = set(insp.get_table_names())
        for t in EXPECTED_TABLES:
            assert t in tables, f"Table '{t}' not created by migration"

    def test_issues_table_columns(
        self, upgraded_engine
    ) -> None:
        insp = inspect(upgraded_engine)
        cols = {c["name"] for c in insp.get_columns("issues")}
        assert cols == ISSUE_COLUMNS

    def test_work_logs_table_columns(
        self, upgraded_engine
    ) -> None:
        insp = inspect(upgraded_engine)
        cols = {c["name"] for c in insp.get_columns("work_logs")}
        assert cols == WORK_LOG_COLUMNS

    def test_code_artifacts_table_columns(
        self, upgraded_engine
    ) -> None:
        insp = inspect(upgraded_engine)
        cols = {c["name"] for c in insp.get_columns("code_artifacts")}
        assert cols == CODE_ARTIFACT_COLUMNS

    def test_issues_primary_key(
        self, upgraded_engine
    ) -> None:
        insp = inspect(upgraded_engine)
        pk = insp.get_pk_constraint("issues")
        assert pk["constrained_columns"] == ["id"]

    def test_work_logs_foreign_key_to_issues(
        self, upgraded_engine
    ) -> None:
        insp = inspect(upgraded_engine)
        fks = insp.get_foreign_keys("work_logs")
        issue_fk = [
            fk for fk in fks if fk["referred_table"] == "issues"
        ]
        assert len(issue_fk) == 1
        assert issue_fk[0]["constrained_columns"] == ["issue_id"]

    def test_code_artifacts_foreign_key_to_work_logs(
        self, upgraded_engine
    ) -> None:
        insp = inspect(upgraded_engine)
        fks = insp.get_foreign_keys("code_artifacts")
        wl_fk = [
            fk for fk in fks if fk["referred_table"] == "work_logs"
        ]
        assert len(wl_fk) == 1
        assert wl_fk[0]["constrained_columns"] == ["work_log_id"]

    def test_issues_self_referencing_foreign_key(
        self, upgraded_engine
    ) -> None:
        insp = inspect(upgraded_engine)
        fks = insp.get_foreign_keys("issues")
        self_fk = [
            fk for fk in fks if fk["referred_table"] == "issues"
        ]
        assert len(self_fk) == 1
        assert self_fk[0]["constrained_columns"] == ["parent_id"]

    def test_work_logs_indexes(
        self, upgraded_engine
    ) -> None:
        insp = inspect(upgraded_engine)
        indexes = insp.get_indexes("work_logs")
        idx_cols = {idx["name"]: idx["column_names"] for idx in indexes}
        assert any(
            "issue_id" in cols for cols in idx_cols.values()
        ), "Missing index on work_logs.issue_id"
        assert any(
            "agent_id" in cols for cols in idx_cols.values()
        ), "Missing index on work_logs.agent_id"


class TestMigrationDowngrade:
    def test_downgrade_removes_all_tables(
        self, upgraded_engine, alembic_cfg: Config
    ) -> None:
        with upgraded_engine.connect() as conn:
            alembic_cfg.attributes["connection"] = conn
            command.downgrade(alembic_cfg, "base")
            conn.commit()
        insp = inspect(upgraded_engine)
        tables = set(insp.get_table_names())
        for t in EXPECTED_TABLES:
            assert t not in tables, f"Table '{t}' not removed after downgrade"

    def test_roundtrip_upgrade_downgrade_upgrade(
        self, upgraded_engine, alembic_cfg: Config
    ) -> None:
        with upgraded_engine.connect() as conn:
            alembic_cfg.attributes["connection"] = conn
            command.downgrade(alembic_cfg, "base")
            conn.commit()
            command.upgrade(alembic_cfg, "head")
            conn.commit()
        insp = inspect(upgraded_engine)
        tables = set(insp.get_table_names())
        for t in EXPECTED_TABLES:
            assert t in tables, f"Table '{t}' missing after roundtrip"


class TestMigrationData:
    def test_insert_issue_after_upgrade(
        self, upgraded_engine
    ) -> None:
        with upgraded_engine.connect() as conn:
            conn.execute(
                text(
                    "INSERT INTO issues (id, title, priority, status, created_at, updated_at) "
                    "VALUES ('a1b2c3d4-0000-0000-0000-000000000001', 'Test', 'medium', 'open', "
                    "'2026-01-01 00:00:00', '2026-01-01 00:00:00')"
                )
            )
            conn.commit()
            row = conn.execute(text("SELECT title FROM issues")).fetchone()
            assert row is not None
            assert row[0] == "Test"

    def test_cascade_delete_work_logs(
        self, upgraded_engine
    ) -> None:
        with upgraded_engine.connect() as conn:
            conn.execute(
                text(
                    "INSERT INTO issues (id, title, priority, status, created_at, updated_at) "
                    "VALUES ('a1b2c3d4-0000-0000-0000-000000000002', 'Parent', 'medium', 'open', "
                    "'2026-01-01 00:00:00', '2026-01-01 00:00:00')"
                )
            )
            conn.execute(
                text(
                    "INSERT INTO work_logs (id, issue_id, agent_id, llm_calls, tokens_used, created_at, updated_at) "
                    "VALUES ('b1b2c3d4-0000-0000-0000-000000000001', "
                    "'a1b2c3d4-0000-0000-0000-000000000002', 'agent-1', 0, 0, "
                    "'2026-01-01 00:00:00', '2026-01-01 00:00:00')"
                )
            )
            conn.commit()
            conn.execute(text("PRAGMA foreign_keys = ON"))
            conn.execute(
                text("DELETE FROM issues WHERE id = 'a1b2c3d4-0000-0000-0000-000000000002'")
            )
            conn.commit()
            rows = conn.execute(text("SELECT * FROM work_logs")).fetchall()
            assert len(rows) == 0
