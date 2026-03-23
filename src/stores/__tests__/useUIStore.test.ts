import { act } from '@testing-library/react';
import { useUIStore, VIEW_MODE } from '../useUIStore';

beforeEach(() => {
  act(() => useUIStore.getState().reset());
});

describe('useUIStore', () => {
  describe('initial state', () => {
    it('starts with side panel closed and board view', () => {
      const state = useUIStore.getState();
      expect(state.sidePanel.isOpen).toBe(false);
      expect(state.sidePanel.contentType).toBeNull();
      expect(state.viewMode).toBe(VIEW_MODE.BOARD);
    });
  });

  describe('openSidePanel', () => {
    it('opens panel with content type', () => {
      act(() => useUIStore.getState().openSidePanel('issue-detail'));
      const state = useUIStore.getState();
      expect(state.sidePanel.isOpen).toBe(true);
      expect(state.sidePanel.contentType).toBe('issue-detail');
    });
  });

  describe('closeSidePanel', () => {
    it('closes panel and clears content type', () => {
      act(() => useUIStore.getState().openSidePanel('issue-detail'));
      act(() => useUIStore.getState().closeSidePanel());
      const state = useUIStore.getState();
      expect(state.sidePanel.isOpen).toBe(false);
      expect(state.sidePanel.contentType).toBeNull();
    });
  });

  describe('toggleSidePanel', () => {
    it('toggles panel open/closed', () => {
      act(() => useUIStore.getState().toggleSidePanel('issue-detail'));
      expect(useUIStore.getState().sidePanel.isOpen).toBe(true);
      act(() => useUIStore.getState().toggleSidePanel('issue-detail'));
      expect(useUIStore.getState().sidePanel.isOpen).toBe(false);
    });

    it('switches content type if panel is open with different type', () => {
      act(() => useUIStore.getState().openSidePanel('issue-detail'));
      act(() => useUIStore.getState().toggleSidePanel('create-issue'));
      const state = useUIStore.getState();
      expect(state.sidePanel.isOpen).toBe(true);
      expect(state.sidePanel.contentType).toBe('create-issue');
    });
  });

  describe('setViewMode', () => {
    it('changes view mode to list', () => {
      act(() => useUIStore.getState().setViewMode(VIEW_MODE.LIST));
      expect(useUIStore.getState().viewMode).toBe(VIEW_MODE.LIST);
    });

    it('changes view mode to board', () => {
      act(() => useUIStore.getState().setViewMode(VIEW_MODE.LIST));
      act(() => useUIStore.getState().setViewMode(VIEW_MODE.BOARD));
      expect(useUIStore.getState().viewMode).toBe(VIEW_MODE.BOARD);
    });

    it('changes view mode to timeline', () => {
      act(() => useUIStore.getState().setViewMode(VIEW_MODE.TIMELINE));
      expect(useUIStore.getState().viewMode).toBe(VIEW_MODE.TIMELINE);
    });
  });
});
