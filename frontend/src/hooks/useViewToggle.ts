import { useState, useCallback, useMemo } from "react";
import {
  VIEW_TYPES,
  VIEW_STORAGE_KEY,
  DEFAULT_VIEW,
  type ViewType,
} from "../types/view";

const VALID_VIEWS = new Set<string>(Object.values(VIEW_TYPES));

function readStoredView(): ViewType {
  try {
    const stored = localStorage.getItem(VIEW_STORAGE_KEY);
    if (stored && VALID_VIEWS.has(stored)) return stored as ViewType;
  } catch {
    /* localStorage unavailable */
  }
  return DEFAULT_VIEW;
}

function persistView(view: ViewType): void {
  try {
    localStorage.setItem(VIEW_STORAGE_KEY, view);
  } catch {
    /* localStorage unavailable */
  }
}

export function useViewToggle() {
  const [view, setViewState] = useState<ViewType>(readStoredView);

  const setView = useCallback((next: ViewType) => {
    setViewState(next);
    persistView(next);
  }, []);

  const toggle = useCallback(() => {
    setViewState((prev) => {
      const next =
        prev === VIEW_TYPES.BOARD ? VIEW_TYPES.TABLE : VIEW_TYPES.BOARD;
      persistView(next);
      return next;
    });
  }, []);

  const derived = useMemo(
    () => ({
      isBoard: view === VIEW_TYPES.BOARD,
      isTable: view === VIEW_TYPES.TABLE,
    }),
    [view]
  );

  return { view, setView, toggle, ...derived };
}
