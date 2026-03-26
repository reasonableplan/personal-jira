import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import { ErrorBoundary } from './ErrorBoundary';

function ThrowingComponent({ error }: { error?: Error }) {
  if (error) {
    throw error;
  }
  return <div>정상 렌더링</div>;
}

describe('ErrorBoundary', () => {
  it('정상일 때 children을 렌더링한다', () => {
    render(
      <ErrorBoundary>
        <ThrowingComponent />
      </ErrorBoundary>,
    );

    expect(screen.getByText('정상 렌더링')).toBeInTheDocument();
  });

  it('에러 발생 시 기본 fallback UI를 렌더링한다', () => {
    // suppress console.error from React + ErrorBoundary
    vi.spyOn(console, 'error').mockImplementation(() => {});

    render(
      <ErrorBoundary>
        <ThrowingComponent error={new Error('테스트 에러')} />
      </ErrorBoundary>,
    );

    expect(screen.getByRole('alert')).toBeInTheDocument();
    expect(screen.getByText('문제가 발생했습니다')).toBeInTheDocument();
    expect(screen.getByText('테스트 에러')).toBeInTheDocument();
    expect(screen.getByText('다시 시도')).toBeInTheDocument();

    vi.restoreAllMocks();
  });

  it('다시 시도 버튼 클릭 시 에러 상태를 초기화한다', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
    const user = userEvent.setup();

    let shouldThrow = true;

    function ConditionalThrow() {
      if (shouldThrow) {
        throw new Error('테스트 에러');
      }
      return <div>정상 렌더링</div>;
    }

    render(
      <ErrorBoundary>
        <ConditionalThrow />
      </ErrorBoundary>,
    );

    expect(screen.getByRole('alert')).toBeInTheDocument();

    // Fix the error condition before retrying
    shouldThrow = false;
    await user.click(screen.getByText('다시 시도'));

    expect(screen.getByText('정상 렌더링')).toBeInTheDocument();

    vi.restoreAllMocks();
  });

  it('커스텀 fallback을 렌더링한다', () => {
    vi.spyOn(console, 'error').mockImplementation(() => {});

    render(
      <ErrorBoundary
        fallback={(error, reset) => (
          <div>
            <span>커스텀: {error.message}</span>
            <button onClick={reset}>리셋</button>
          </div>
        )}
      >
        <ThrowingComponent error={new Error('커스텀 에러')} />
      </ErrorBoundary>,
    );

    expect(screen.getByText('커스텀: 커스텀 에러')).toBeInTheDocument();
    expect(screen.getByText('리셋')).toBeInTheDocument();

    vi.restoreAllMocks();
  });
});
