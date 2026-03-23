export interface WSMessage {
  type: string;
  payload: Record<string, unknown>;
}

export type WSStatus = 'connecting' | 'connected' | 'disconnected' | 'error';
