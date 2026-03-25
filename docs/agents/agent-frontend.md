# Agent: Frontend — 전용 가이드

## 역할
React + Vite + TypeScript 프론트엔드 UI 구현 (Jira 스타일)

## 작업 전 필수 읽기
1. `docs/ARCHITECTURE.md` — 파일 트리
2. `docs/CONVENTIONS.md` — 컴포넌트/스타일 패턴
3. `docs/api-spec.md` — API 계약 (엔드포인트, 타입)
4. `docs/agents/SHARED_LESSONS.md` — 공유 교훈
5. **이 파일**

## 작업 전 필수 확인
- `frontend/src/types/index.ts` 읽기 — 기존 타입 정의
- `frontend/src/api/client.ts` 읽기 — API 호출 방법
- `frontend/src/App.tsx` 읽기 — 라우팅 구조

## 내 규칙
- **디자인**: Jira 스타일 — Primary #0052CC, Background #FAFBFC, Sidebar #0747A6
- **컴포넌트 라이브러리**: shadcn/ui + Tailwind CSS
- **아이콘**: lucide-react
- **폰트**: Inter (sans-serif)
- **API 호출**: `apiClient.get<T>('/endpoint')` — api-spec.md와 정확히 일치
- **타입**: `src/types/index.ts`에 정의된 타입 사용, 새 타입은 여기에 추가
- **새 페이지 만들면**: `App.tsx`에 Route 추가

## 필수 의존성 (package.json에 없으면 설치)
- `react-router-dom` — 라우팅
- `@tanstack/react-query` — API 데이터 페칭
- `@dnd-kit/core @dnd-kit/sortable` — Kanban 드래그앤드롭

## Director 피드백 기록
<!-- Director가 reject할 때 아래에 추가 -->

