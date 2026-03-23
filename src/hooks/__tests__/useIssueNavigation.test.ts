import { renderHook, act } from '@testing-library/react';
import { useIssueNavigation } from '../useIssueNavigation';

const MOCK_ISSUE_IDS = ['issue-1', 'issue-2', 'issue-3', 'issue-4'];

describe('useIssueNavigation', () => {
  it('starts with selectedIndex at 0', () => {
    const { result } = renderHook(() => useIssueNavigation(MOCK_ISSUE_IDS));
    expect(result.current.selectedIndex).toBe(0);
    expect(result.current.selectedId).toBe('issue-1');
  });

  it('navigates down with moveDown', () => {
    const { result } = renderHook(() => useIssueNavigation(MOCK_ISSUE_IDS));

    act(() => { result.current.moveDown(); });
    expect(result.current.selectedIndex).toBe(1);
    expect(result.current.selectedId).toBe('issue-2');
  });

  it('navigates up with moveUp', () => {
    const { result } = renderHook(() => useIssueNavigation(MOCK_ISSUE_IDS));

    act(() => { result.current.moveDown(); });
    act(() => { result.current.moveDown(); });
    act(() => { result.current.moveUp(); });
    expect(result.current.selectedIndex).toBe(1);
  });

  it('does not go below 0', () => {
    const { result } = renderHook(() => useIssueNavigation(MOCK_ISSUE_IDS));

    act(() => { result.current.moveUp(); });
    expect(result.current.selectedIndex).toBe(0);
  });

  it('does not exceed list length', () => {
    const { result } = renderHook(() => useIssueNavigation(MOCK_ISSUE_IDS));

    for (let i = 0; i < 10; i++) {
      act(() => { result.current.moveDown(); });
    }
    expect(result.current.selectedIndex).toBe(MOCK_ISSUE_IDS.length - 1);
  });

  it('returns null selectedId for empty list', () => {
    const { result } = renderHook(() => useIssueNavigation([]));
    expect(result.current.selectedId).toBeNull();
    expect(result.current.selectedIndex).toBe(0);
  });

  it('resets index when issueIds change', () => {
    const { result, rerender } = renderHook(
      ({ ids }) => useIssueNavigation(ids),
      { initialProps: { ids: MOCK_ISSUE_IDS } }
    );

    act(() => { result.current.moveDown(); });
    act(() => { result.current.moveDown(); });
    expect(result.current.selectedIndex).toBe(2);

    rerender({ ids: ['new-1', 'new-2'] });
    expect(result.current.selectedIndex).toBe(0);
    expect(result.current.selectedId).toBe('new-1');
  });

  it('allows setting index directly via setSelectedIndex', () => {
    const { result } = renderHook(() => useIssueNavigation(MOCK_ISSUE_IDS));

    act(() => { result.current.setSelectedIndex(2); });
    expect(result.current.selectedIndex).toBe(2);
    expect(result.current.selectedId).toBe('issue-3');
  });

  it('clamps setSelectedIndex to valid range', () => {
    const { result } = renderHook(() => useIssueNavigation(MOCK_ISSUE_IDS));

    act(() => { result.current.setSelectedIndex(100); });
    expect(result.current.selectedIndex).toBe(3);

    act(() => { result.current.setSelectedIndex(-5); });
    expect(result.current.selectedIndex).toBe(0);
  });
});