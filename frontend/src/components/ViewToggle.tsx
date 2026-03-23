import type { ViewType } from "../types/view";
import { VIEW_TYPES } from "../types/view";
import styles from "./ViewToggle.module.css";

interface ViewToggleProps {
  view: ViewType;
  onToggle: (view: ViewType) => void;
}

const VIEW_OPTIONS: { type: ViewType; label: string; icon: string }[] = [
  { type: VIEW_TYPES.BOARD, label: "Board", icon: "⊞" },
  { type: VIEW_TYPES.TABLE, label: "Table", icon: "☰" },
];

export function ViewToggle({ view, onToggle }: ViewToggleProps) {
  return (
    <div className={styles.container} role="group" aria-label="View toggle">
      {VIEW_OPTIONS.map(({ type, label, icon }) => {
        const isActive = view === type;
        return (
          <button
            key={type}
            type="button"
            className={`${styles.button} ${isActive ? styles.active : ""}`}
            aria-pressed={isActive}
            onClick={() => {
              if (!isActive) onToggle(type);
            }}
          >
            <span className={styles.icon} aria-hidden="true">
              {icon}
            </span>
            {label}
          </button>
        );
      })}
    </div>
  );
}
