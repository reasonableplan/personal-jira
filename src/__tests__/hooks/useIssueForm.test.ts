import { renderHook, act } from '@testing-library/react';
import { useIssueForm } from '../../hooks/useIssueForm';
import { IssueType, IssuePriority } from '../../types/issue';
import type { IssueFormData } from '../../types/issue';

describe('useIssueForm', () => {
  test('initializes with defaults', () => {
    const { result } = renderHook(() => useIssueForm());
    expect(result.current.values.title).toBe('');
    expect(result.current.values.description).toBe('');
    expect(result.current.values.issue_type).toBe(IssueType.TASK);
    expect(result.current.values.priority).toBe(IssuePriority.MEDIUM);
    expect(result.current.values.labels).toEqual([]);
  });

  test('initializes with provided data', () => {
    const initial: IssueFormData = {
      title: 'Test',
      description: '# md',
      issue_type: IssueType.BUG,
      priority: IssuePriority.HIGH,
      labels: ['x'],
    };
    const { result } = renderHook(() => useIssueForm(initial));
    expect(result.current.values).toEqual(initial);
  });

  test('setField updates a single field', () => {
    const { result } = renderHook(() => useIssueForm());
    act(() => result.current.setField('title', 'New'));
    expect(result.current.values.title).toBe('New');
  });

  test('validate returns errors for empty title', () => {
    const { result } = renderHook(() => useIssueForm());
    let valid: boolean;
    act(() => {
      valid = result.current.validate();
    });
    expect(valid!).toBe(false);
    expect(result.current.errors.title).toBeDefined();
  });

  test('validate returns errors for title over 200 chars', () => {
    const { result } = renderHook(() => useIssueForm());
    act(() => result.current.setField('title', 'a'.repeat(201)));
    let valid: boolean;
    act(() => {
      valid = result.current.validate();
    });
    expect(valid!).toBe(false);
    expect(result.current.errors.title).toMatch(/200/);
  });

  test('validate passes with valid data', () => {
    const { result } = renderHook(() => useIssueForm());
    act(() => result.current.setField('title', 'Valid'));
    let valid: boolean;
    act(() => {
      valid = result.current.validate();
    });
    expect(valid!).toBe(true);
    expect(result.current.errors).toEqual({});
  });

  test('reset restores initial values', () => {
    const { result } = renderHook(() => useIssueForm());
    act(() => result.current.setField('title', 'Changed'));
    act(() => result.current.reset());
    expect(result.current.values.title).toBe('');
  });
});
