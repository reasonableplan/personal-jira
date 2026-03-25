# 공유 교훈 — 모든 에이전트 필수 읽기

> Director가 reject할 때마다 여기에 추가됩니다. 같은 실수 반복 금지.

## Import 관련
- **models는 `from app.models import ...`** — `app.models.base`에는 Base만 있음. Task, Epic, Label 등은 `app.models`에서 import
- **task_labels는 Table 객체** — ORM 클래스가 아님. `TaskLabel(...)` 생성 불가. `insert(task_labels).values(...)` 사용

## 파일 구조 관련
- **`__init__.py` 반드시 생성** — `app/`, `routers/`, `schemas/`, `services/` 모든 디렉토리에
- **새 라우터 → main.py 등록 필수** — `app.include_router(router)` 빠뜨리면 엔드포인트 404

## 코드 패턴
- **exception_handlers 등록** — `main.py`에서 `register_exception_handlers(app)` 호출
- **DB 세션** — `from app.database import get_db`, `Depends(get_db)`로 주입
- **YAML 파일** — docker-compose.yml 등은 truncation 감지에서 제외됨, 정상 작성 가능

## Lint 관련
- **ruff 설정은 루트 `ruff.toml`만 사용** — `backend/pyproject.toml`의 `[tool.ruff]`는 무시됨
- **E501(줄 길이), B008(Depends), B904(raise from)** — ignore 처리됨, 걱정 불필요
- **`--fix --unsafe-fixes`** — autofix가 자동 적용됨
