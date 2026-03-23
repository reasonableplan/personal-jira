export interface ShortcutEntry {
  handler: () => void;
  description: string;
}

export type ShortcutMap = Record<string, ShortcutEntry>;

export interface ShortcutInfo {
  keys: string;
  description: string;
}
