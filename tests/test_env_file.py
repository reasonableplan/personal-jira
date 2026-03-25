from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestEnvExample:
    def test_file_exists(self) -> None:
        assert (ROOT / ".env.example").exists()

    def test_required_vars(self) -> None:
        content = (ROOT / ".env.example").read_text()
        required = [
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "POSTGRES_DB",
            "DATABASE_URL",
            "CORS_ORIGINS",
            "LOG_LEVEL",
        ]
        for var in required:
            assert var in content, f"Missing {var}"
