import { useEffect, useRef, useState, useCallback } from 'react';

export const WS_READY_STATE = {
  CONNECTING: 0,
  OPEN: 1,
  CLOSING: 2,
  CLOSED: 3,
} as const;

const RECONNECT_DELAY = 3000;
const NORMAL_CLOSE_CODE = 1000;

interface UseWebSocketOptions {
  onMessage?: (data: unknown) => void;
  enabled?: boolean;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  lastMessage: unknown;
  sendMessage: (data: unknown) => void;
}

export function useWebSocket(
  url: string,
  options?: UseWebSocketOptions
): UseWebSocketReturn {
  const { onMessage, enabled = true } = options ?? {};
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<unknown>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  const connect = useCallback(() => {
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => setIsConnected(true);

    ws.onmessage = (event: MessageEvent) => {
      try {
        const parsed = JSON.parse(event.data as string);
        setLastMessage(parsed);
        onMessageRef.current?.(parsed);
      } catch (err) {
        console.error('[WebSocket] Failed to parse message:', err);
      }
    };

    ws.onclose = (event: CloseEvent) => {
      setIsConnected(false);
      if (event.code !== NORMAL_CLOSE_CODE) {
        reconnectTimerRef.current = setTimeout(connect, RECONNECT_DELAY);
      }
    };

    ws.onerror = () => {
      console.error('[WebSocket] Connection error');
    };
  }, [url]);

  useEffect(() => {
    if (!enabled) return;
    connect();
    return () => {
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
      }
      wsRef.current?.close();
    };
  }, [connect, enabled]);

  const sendMessage = useCallback((data: unknown) => {
    if (wsRef.current?.readyState === WS_READY_STATE.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  return { isConnected, lastMessage, sendMessage };
}
