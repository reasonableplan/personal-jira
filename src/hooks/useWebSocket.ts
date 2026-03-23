import { useEffect, useRef, useState, useCallback } from 'react';
import type { WSMessage, WSStatus } from '../types/websocket';
import {
  WS_READY_STATE,
  WS_RECONNECT_INTERVAL_MS,
  WS_MAX_RETRIES,
  WS_NORMAL_CLOSE_CODE,
} from '../constants/websocket';

interface UseWebSocketOptions {
  onMessage?: (message: WSMessage) => void;
}

export function useWebSocket(url: string, options: UseWebSocketOptions = {}) {
  const [status, setStatus] = useState<WSStatus>('connecting');
  const [lastMessage, setLastMessage] = useState<WSMessage | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const retriesRef = useRef(0);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const intentionalCloseRef = useRef(false);
  const onMessageRef = useRef(options.onMessage);
  onMessageRef.current = options.onMessage;

  const connect = useCallback(() => {
    const ws = new WebSocket(url);
    wsRef.current = ws;
    setStatus('connecting');

    ws.onopen = () => {
      setStatus('connected');
      retriesRef.current = 0;
    };

    ws.onmessage = (event: MessageEvent) => {
      try {
        const parsed: WSMessage = JSON.parse(event.data);
        setLastMessage(parsed);
        onMessageRef.current?.(parsed);
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    ws.onerror = () => {
      setStatus('error');
    };

    ws.onclose = (event: CloseEvent) => {
      if (intentionalCloseRef.current) return;

      if (event.code === WS_NORMAL_CLOSE_CODE) {
        setStatus('disconnected');
        return;
      }

      setStatus('disconnected');

      if (retriesRef.current < WS_MAX_RETRIES) {
        retriesRef.current += 1;
        reconnectTimerRef.current = setTimeout(() => {
          connect();
        }, WS_RECONNECT_INTERVAL_MS);
      }
    };
  }, [url]);

  useEffect(() => {
    intentionalCloseRef.current = false;
    connect();

    return () => {
      intentionalCloseRef.current = true;
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  const sendMessage = useCallback((message: WSMessage) => {
    if (wsRef.current?.readyState === WS_READY_STATE.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  const disconnect = useCallback(() => {
    intentionalCloseRef.current = true;
    if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
    wsRef.current?.close(WS_NORMAL_CLOSE_CODE);
    setStatus('disconnected');
  }, []);

  return { status, lastMessage, sendMessage, disconnect };
}
