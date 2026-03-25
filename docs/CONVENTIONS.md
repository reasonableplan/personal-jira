# Personal Jira — Coding Conventions

> 모든 에이전트가 코드 작성 전 반드시 읽으세요.

## Python (Backend)

### Import 규칙
```python
# ✅ 올바른 import
from app.models import Epic, Story, Task, Label
from app.database import get_db
from app.config import settings

# ❌ 잘못된 import — 절대 이렇게 하지 마세요
from app.models.base import Task      # base.py에는 Base만 있음
from app.models.issue import Epic     # __init__.py를 통해 import
from app.database import Base         # database.py의 Base 사용 금지, models에서
```

### FastAPI 라우터 패턴
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Epic
from app.schemas.epic import EpicCreate, EpicResponse

router = APIRouter(prefix="/api/epics", tags=["epics"])

@router.get("/", response_model=list[EpicResponse])
async def list_epics(db: AsyncSession = Depends(get_db)):
    ...

@router.post("/", response_model=EpicResponse, status_code=201)
async def create_epic(body: EpicCreate, db: AsyncSession = Depends(get_db)):
    ...
```

### 라우터를 만들면 반드시
1. `main.py`에 `app.include_router(router)` 추가
2. 테스트 파일 작성 (`tests/test_routers_{name}.py`)

### 서비스 패턴
```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Epic

class EpicService:
    async def get_by_id(self, session: AsyncSession, id: str) -> Epic | None:
        result = await session.execute(select(Epic).where(Epic.id == id))
        return result.scalar_one_or_none()
```

### 테스트 패턴
```python
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

async def test_list_epics(client: AsyncClient):
    response = await client.get("/api/epics/")
    assert response.status_code == 200
```

### 필수 규칙
- **`__init__.py`**: 새 디렉토리 만들면 반드시 생성 (빈 파일이라도)
- **타입 힌트**: 모든 함수에 매개변수 + 반환 타입
- **빈 catch 금지**: `except Exception: pass` 금지, 최소한 log
- **commit 전**: `ruff check --fix` 실행

## TypeScript (Frontend)

### API 호출 패턴
```typescript
import { apiClient } from '@/api/client';
import type { Epic } from '@/types';

// api-spec.md의 엔드포인트와 정확히 일치해야 함
const epics = await apiClient.get<Epic[]>('/epics');
```

### 컴포넌트 패턴
- Jira 스타일: Primary #0052CC, Background #FAFBFC
- shadcn/ui + Tailwind CSS
- lucide-react 아이콘
- Inter 폰트

## 완료 조건 (Worker 자체 검증)

코드 작성 후 반드시 확인:
1. `python -c "from app.main import app"` — ImportError 없음
2. `ruff check --fix` — lint 통과
3. `pytest tests/ -x -q` — 테스트 통과
4. 새 파일에 `__init__.py` 있음
5. 새 라우터가 main.py에 등록됨
