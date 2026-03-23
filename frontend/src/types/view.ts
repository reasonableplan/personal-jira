export const VIEW_TYPES = {
  BOARD: "board",
  TABLE: "table",
} as const;

export type ViewType = (typeof VIEW_TYPES)[keyof typeof VIEW_TYPES];

export const VIEW_STORAGE_KEY = "personal-jira-view-type";
export const DEFAULT_VIEW: ViewType = VIEW_TYPES.BOARD;
