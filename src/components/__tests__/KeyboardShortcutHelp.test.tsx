import { render, screen, fireEvent } from '@testing-library/react';
import { KeyboardShortcutHelp } from '../KeyboardShortcutHelp';
import type { KeyboardShortcutGroup } from '../../types/keyboard';

const MOCK_GROUPS: KeyboardShortcutGroup[] = [
  {
    name: '이슈',
    shortcuts: [
      { key: 'C', description: '새 이슈 생성', handler: jest.fn() },
      { key: 'J', description: '다음 이슈로 이동', handler: jest.fn() },
      { key: 'K', description: '이전 이슈로 이동', handler: jest.fn() },
    ],
  },
  {
    name: '일반',
    shortcuts: [
      { key: '?', description: '단축키 도움말', handler: jest.fn() },
    ],
  },
];

describe('KeyboardShortcutHelp', () => {
  it('renders nothing when isOpen is false', () => {
    const { container } = render(
      <KeyboardShortcutHelp isOpen={false} onClose={jest.fn()} groups={MOCK_GROUPS} />
    );
    expect(container.firstChild).toBeNull();
  });

  it('renders modal when isOpen is true', () => {
    render(
      <KeyboardShortcutHelp isOpen={true} onClose={jest.fn()} groups={MOCK_GROUPS} />
    );
    expect(screen.getByText('키보드 단축키')).toBeInTheDocument();
  });

  it('renders all shortcut groups', () => {
    render(
      <KeyboardShortcutHelp isOpen={true} onClose={jest.fn()} groups={MOCK_GROUPS} />
    );
    expect(screen.getByText('이슈')).toBeInTheDocument();
    expect(screen.getByText('일반')).toBeInTheDocument();
  });

  it('renders all shortcut keys and descriptions', () => {
    render(
      <KeyboardShortcutHelp isOpen={true} onClose={jest.fn()} groups={MOCK_GROUPS} />
    );
    expect(screen.getByText('C')).toBeInTheDocument();
    expect(screen.getByText('새 이슈 생성')).toBeInTheDocument();
    expect(screen.getByText('J')).toBeInTheDocument();
    expect(screen.getByText('다음 이슈로 이동')).toBeInTheDocument();
    expect(screen.getByText('K')).toBeInTheDocument();
    expect(screen.getByText('이전 이슈로 이동')).toBeInTheDocument();
    expect(screen.getByText('?')).toBeInTheDocument();
    expect(screen.getByText('단축키 도움말')).toBeInTheDocument();
  });

  it('calls onClose when backdrop is clicked', () => {
    const onClose = jest.fn();
    render(
      <KeyboardShortcutHelp isOpen={true} onClose={onClose} groups={MOCK_GROUPS} />
    );
    fireEvent.click(screen.getByTestId('shortcut-help-backdrop'));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when Escape key is pressed', () => {
    const onClose = jest.fn();
    render(
      <KeyboardShortcutHelp isOpen={true} onClose={onClose} groups={MOCK_GROUPS} />
    );
    fireEvent.keyDown(screen.getByRole('dialog'), { key: 'Escape' });
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('does not call onClose when modal content is clicked', () => {
    const onClose = jest.fn();
    render(
      <KeyboardShortcutHelp isOpen={true} onClose={onClose} groups={MOCK_GROUPS} />
    );
    fireEvent.click(screen.getByTestId('shortcut-help-content'));
    expect(onClose).not.toHaveBeenCalled();
  });

  it('renders with correct aria attributes', () => {
    render(
      <KeyboardShortcutHelp isOpen={true} onClose={jest.fn()} groups={MOCK_GROUPS} />
    );
    const dialog = screen.getByRole('dialog');
    expect(dialog).toHaveAttribute('aria-label', '키보드 단축키');
  });
});