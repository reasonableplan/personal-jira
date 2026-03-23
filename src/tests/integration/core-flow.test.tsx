import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, within, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { App } from '@/App';
import { resetMockData } from '../mocks/handlers';

describe('Core Flow Integration', () => {
  beforeEach(() => {
    resetMockData();
  });

  describe('Issue Creation', () => {
    it('creates an issue via the form and displays it on the board', async () => {
      const user = userEvent.setup();
      render(<App />);

      await user.click(screen.getByRole('button', { name: /새 이슈/i }));

      const dialog = screen.getByRole('dialog');
      await user.type(within(dialog).getByLabelText(/제목/i), '첫 번째 이슈');
      await user.type(within(dialog).getByLabelText(/설명/i), '테스트 설명입니다');
      await user.click(within(dialog).getByRole('button', { name: /생성/i }));

      await waitFor(() => {
        expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      });

      const backlogColumn = screen.getByTestId('column-backlog');
      expect(within(backlogColumn).getByText('첫 번째 이슈')).toBeInTheDocument();
    });

    it('shows validation error when title is empty', async () => {
      const user = userEvent.setup();
      render(<App />);

      await user.click(screen.getByRole('button', { name: /새 이슈/i }));
      const dialog = screen.getByRole('dialog');
      await user.click(within(dialog).getByRole('button', { name: /생성/i }));

      expect(within(dialog).getByText(/제목.*필수/i)).toBeInTheDocument();
    });
  });

  describe('Kanban Board Status Transition', () => {
    it('moves an issue to a different column via status transition', async () => {
      const user = userEvent.setup();
      render(<App />);

      await user.click(screen.getByRole('button', { name: /새 이슈/i }));
      const dialog = screen.getByRole('dialog');
      await user.type(within(dialog).getByLabelText(/제목/i), '드래그 이슈');
      await user.click(within(dialog).getByRole('button', { name: /생성/i }));

      await waitFor(() => {
        expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      });

      const issueCard = screen.getByText('드래그 이슈');
      await user.click(issueCard);

      await waitFor(() => {
        expect(screen.getByTestId('issue-detail-panel')).toBeInTheDocument();
      });

      const panel = screen.getByTestId('issue-detail-panel');
      const statusSelect = within(panel).getByLabelText(/상태/i);
      await user.selectOptions(statusSelect, IssueStatusLabel.READY);

      await waitFor(() => {
        const readyColumn = screen.getByTestId('column-ready');
        expect(within(readyColumn).getByText('드래그 이슈')).toBeInTheDocument();
      });

      const backlogColumn = screen.getByTestId('column-backlog');
      expect(within(backlogColumn).queryByText('드래그 이슈')).not.toBeInTheDocument();
    });
  });

  describe('Issue Detail Panel', () => {
    it('opens detail panel on issue card click and shows issue info', async () => {
      const user = userEvent.setup();
      render(<App />);

      await user.click(screen.getByRole('button', { name: /새 이슈/i }));
      const dialog = screen.getByRole('dialog');
      await user.type(within(dialog).getByLabelText(/제목/i), '상세 이슈');
      await user.type(within(dialog).getByLabelText(/설명/i), '상세 설명 텍스트');
      await user.click(within(dialog).getByRole('button', { name: /생성/i }));

      await waitFor(() => {
        expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      });

      await user.click(screen.getByText('상세 이슈'));

      await waitFor(() => {
        const panel = screen.getByTestId('issue-detail-panel');
        expect(within(panel).getByText('상세 이슈')).toBeInTheDocument();
        expect(within(panel).getByText('상세 설명 텍스트')).toBeInTheDocument();
      });
    });

    it('closes detail panel on close button click', async () => {
      const user = userEvent.setup();
      render(<App />);

      await user.click(screen.getByRole('button', { name: /새 이슈/i }));
      const dialog = screen.getByRole('dialog');
      await user.type(within(dialog).getByLabelText(/제목/i), '닫기 테스트'));
      await user.click(within(dialog).getByRole('button', { name: /생성/i }));

      await waitFor(() => {
        expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      });

      await user.click(screen.getByText('닫기 테스트'));
      await waitFor(() => {
        expect(screen.getByTestId('issue-detail-panel')).toBeInTheDocument();
      });

      await user.click(screen.getByRole('button', { name: /닫기/i }));
      await waitFor(() => {
        expect(screen.queryByTestId('issue-detail-panel')).not.toBeInTheDocument();
      });
    });
  });

  describe('Comment Writing', () => {
    it('adds a comment to an issue via detail panel', async () => {
      const user = userEvent.setup();
      render(<App />);

      await user.click(screen.getByRole('button', { name: /새 이슈/i }));
      const dialog = screen.getByRole('dialog');
      await user.type(within(dialog).getByLabelText(/제목/i), '코멘트 이슈');
      await user.click(within(dialog).getByRole('button', { name: /생성/i }));

      await waitFor(() => {
        expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      });

      await user.click(screen.getByText('코멘트 이슈'));
      await waitFor(() => {
        expect(screen.getByTestId('issue-detail-panel')).toBeInTheDocument();
      });

      const panel = screen.getByTestId('issue-detail-panel');
      const commentInput = within(panel).getByPlaceholderText(/코멘트/i);
      await user.type(commentInput, '첫 번째 코멘트입니다');
      await user.click(within(panel).getByRole('button', { name: /등록/i }));

      await waitFor(() => {
        expect(within(panel).getByText('첫 번째 코멘트입니다')).toBeInTheDocument();
      });

      expect((commentInput as HTMLTextAreaElement).value).toBe('');
    });

    it('displays multiple comments in chronological order', async () => {
      const user = userEvent.setup();
      render(<App />);

      await user.click(screen.getByRole('button', { name: /새 이슈/i }));
      const dialog = screen.getByRole('dialog');
      await user.type(within(dialog).getByLabelText(/제목/i), '다중 코멘트');
      await user.click(within(dialog).getByRole('button', { name: /생성/i }));

      await waitFor(() => {
        expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      });

      await user.click(screen.getByText('다중 코멘트'));
      await waitFor(() => {
        expect(screen.getByTestId('issue-detail-panel')).toBeInTheDocument();
      });

      const panel = screen.getByTestId('issue-detail-panel');
      const commentInput = within(panel).getByPlaceholderText(/코멘트/i);

      await user.type(commentInput, '첫 번째');
      await user.click(within(panel).getByRole('button', { name: /등록/i }));
      await waitFor(() => {
        expect(within(panel).getByText('첫 번째')).toBeInTheDocument();
      });

      await user.type(commentInput, '두 번째');
      await user.click(within(panel).getByRole('button', { name: /등록/i }));
      await waitFor(() => {
        expect(within(panel).getByText('두 번째')).toBeInTheDocument();
      });

      const commentItems = within(panel).getAllByTestId('comment-item');
      expect(commentItems).toHaveLength(2);
    });
  });

  describe('Full E2E-like Flow', () => {
    it('creates issue → views on board → opens detail → writes comment', async () => {
      const user = userEvent.setup();
      render(<App />);

      // Step 1: Create issue
      await user.click(screen.getByRole('button', { name: /새 이슈/i }));
      const dialog = screen.getByRole('dialog');
      await user.type(within(dialog).getByLabelText(/제목/i), 'E2E 플로우 이슈');
      await user.type(within(dialog).getByLabelText(/설명/i), 'E2E 설명');
      await user.click(within(dialog).getByRole('button', { name: /생성/i }));

      await waitFor(() => {
        expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      });

      // Step 2: Verify on board
      const backlogColumn = screen.getByTestId('column-backlog');
      expect(within(backlogColumn).getByText('E2E 플로우 이슈')).toBeInTheDocument();

      // Step 3: Open detail panel
      await user.click(screen.getByText('E2E 플로우 이슈'));
      await waitFor(() => {
        expect(screen.getByTestId('issue-detail-panel')).toBeInTheDocument();
      });

      const panel = screen.getByTestId('issue-detail-panel');
      expect(within(panel).getByText('E2E 플로우 이슈')).toBeInTheDocument();
      expect(within(panel).getByText('E2E 설명')).toBeInTheDocument();

      // Step 4: Write comment
      const commentInput = within(panel).getByPlaceholderText(/코멘트/i);
      await user.type(commentInput, 'E2E 코멘트 작성 완료');
      await user.click(within(panel).getByRole('button', { name: /등록/i }));

      await waitFor(() => {
        expect(within(panel).getByText('E2E 코멘트 작성 완료')).toBeInTheDocument();
      });
    });
  });
});

const IssueStatusLabel = {
  BACKLOG: 'backlog',
  READY: 'ready',
  IN_PROGRESS: 'in_progress',
  IN_REVIEW: 'in_review',
  DONE: 'done',
  CANCELLED: 'cancelled',
  BLOCKED: 'blocked',
} as const;
