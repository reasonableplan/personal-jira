
- [2026-03-27 00:31] Backend FastAPI 프로젝트 스캐폴딩: 총 3개 이슈 발견:

**이슈 1 — Task Match 미충족: 헬스체크 엔드포인트 스펙 불일치**
1. **File**: backend/app/main.py
2. **Line/Section**: `@app.get("/health")` 및 `health_check` 함수
3. **Problem**: 태스크 요구사항은 `GET /api/health → {"status": "ok", "version": "0.1.0"}`이나, 현재 main.py는 (1) 경로가 `/health`이지 `/api/health`가 아님, (2) 응답에 `version` 필드가 누락됨 (`{"status": "ok"}`만 반환). 요약에서는 `app/routers/health.py`가 올바른 엔드포인트를 가진다고 하지만, main.py에 라우터 등록 코드(`include_router`)가 전혀 없어 해당 라우터가 실제로 동작하지 않음.
4. **Fix**: main.py에서 직접 정의된 `@app.get("
