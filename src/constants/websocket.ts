export const WS_READY_STATE = {
  CONNECTING: 0,
  OPEN: 1,
  CLOSING: 2,
  CLOSED: 3,
} as const;

export const WS_RECONNECT_INTERVAL_MS = 3000;
export const WS_MAX_RETRIES = 5;
export const WS_NORMAL_CLOSE_CODE = 1000;
