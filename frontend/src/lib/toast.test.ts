import { describe, expect, it, vi } from 'vitest';

vi.mock('sonner', () => ({
  toast: {
    error: vi.fn(),
  },
}));

import { toast } from 'sonner';

import type { AppError } from '@/api/client';

import { showApiError } from './toast';

describe('showApiError', () => {
  it('문자열 detail이 있으면 description에 표시한다', () => {
    const error: AppError = {
      message: 'Request failed',
      status: 404,
      detail: '리소스를 찾을 수 없습니다',
    };

    showApiError(error);

    expect(toast.error).toHaveBeenCalledWith('요청 실패', {
      description: '리소스를 찾을 수 없습니다',
    });
  });

  it('detail이 문자열이 아니면 message를 사용한다', () => {
    const error: AppError = {
      message: 'Network Error',
      status: 0,
      detail: [{ loc: ['body'], msg: 'invalid', type: 'value_error' }],
    };

    showApiError(error);

    expect(toast.error).toHaveBeenCalledWith('요청 실패', {
      description: 'Network Error',
    });
  });
});
