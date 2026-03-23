import { useCallback, useEffect, useMemo, useState } from 'react';

export interface UseIssueNavigationReturn {
  selectedIndex: number;
  selectedId: string | null;
  moveUp: () => void;
  moveDown: () => void;
  setSelectedIndex: (index: number) => void;
}

export const useIssueNavigation = (issueIds: string[]): UseIssueNavigationReturn => {
  const [selectedIndex, setSelectedIndexRaw] = useState(0);

  useEffect(() => {
    setSelectedIndexRaw(0);
  }, [issueIds]);

  const clamp = useCallback(
    (val: number) => Math.max(0, Math.min(val, Math.max(0, issueIds.length - 1))),
    [issueIds.length]
  );

  const moveUp = useCallback(() => {
    setSelectedIndexRaw((prev) => clamp(prev - 1));
  }, [clamp]);

  const moveDown = useCallback(() => {
    setSelectedIndexRaw((prev) => clamp(prev + 1));
  }, [clamp]);

  const setSelectedIndex = useCallback(
    (index: number) => setSelectedIndexRaw(clamp(index)),
    [clamp]
  );

  const selectedId = useMemo(
    () => issueIds[selectedIndex] ?? null,
    [issueIds, selectedIndex]
  );

  return { selectedIndex, selectedId, moveUp, moveDown, setSelectedIndex };
};