from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent


def test_db_module_has_engine() -> None:
    content = (BACKEND / "app" / "db.py").read_text(
        encoding="utf-8"
    )
    assert "engine" in content
    assert "Session" in content or "session" in content


def test_db_module_has_session_factory() -> None:
    content = (BACKEND / "app" / "db.py").read_text(
        encoding="utf-8"
    )
    assert "SessionLocal" in content or "get_db" in content
