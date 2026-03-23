import { useState, useCallback } from "react";
import type { Issue, ReorderRequest } from "../types/issue";
import { batchReorder } from "../api/issues";

export interface DragState {
  draggedId: string | null;
  overId: string | null;
}

export function reorderItems(items: Issue[], fromId: string, toId: string): Issue[] {
  const fromIdx = items.findIndex((i) => i.id === fromId);
  const toIdx = items.findIndex((i) => i.id === toId);
  if (fromIdx === -1 || toIdx === -1) return items;

  const next = [...items];
  const [moved] = next.splice(fromIdx, 1);
  next.splice(toIdx, 0, moved);
  return next.map((item, idx) => ({ ...item, priority_order: idx }));
}

export function useKanbanDrag(onReorder: (updated: Issue[]) => void) {
  const [dragState, setDragState] = useState<DragState>({
    draggedId: null,
    overId: null,
  });
  const [saving, setSaving] = useState(false);

  const handleDragStart = useCallback((id: string) => {
    setDragState({ draggedId: id, overId: null });
  }, []);

  const handleDragOver = useCallback((id: string) => {
    setDragState((prev) => ({ ...prev, overId: id }));
  }, []);

  const handleDrop = useCallback(
    async (items: Issue[]) => {
      const { draggedId, overId } = dragState;
      if (!draggedId || !overId || draggedId === overId) {
        setDragState({ draggedId: null, overId: null });
        return;
      }

      const reordered = reorderItems(items, draggedId, overId);
      onReorder(reordered);
      setDragState({ draggedId: null, overId: null });

      const requests: ReorderRequest[] = reordered.map((item) => ({
        issue_id: item.id,
        new_order: item.priority_order,
      }));

      setSaving(true);
      try {
        await batchReorder(requests);
      } catch (err) {
        onReorder(items);
        console.error("Reorder failed, reverted:", err);
      } finally {
        setSaving(false);
      }
    },
    [dragState, onReorder],
  );

  const handleDragEnd = useCallback(() => {
    setDragState({ draggedId: null, overId: null });
  }, []);

  return { dragState, saving, handleDragStart, handleDragOver, handleDrop, handleDragEnd };
}
