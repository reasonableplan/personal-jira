export interface KeyboardShortcut {
  key: string;
  description: string;
  handler: () => void;
  modifiers?: {
    ctrl?: boolean;
    shift?: boolean;
    alt?: boolean;
    meta?: boolean;
  };
}

export interface KeyboardShortcutGroup {
  name: string;
  shortcuts: KeyboardShortcut[];
}

export interface UseKeyboardShortcutsOptions {
  onCreateIssue: () => void;
  onNavigateUp: () => void;
  onNavigateDown: () => void;
  onToggleHelp: () => void;
  enabled?: boolean;
}