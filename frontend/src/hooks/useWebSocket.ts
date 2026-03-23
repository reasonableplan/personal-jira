import { useEffect, useRef, useState, useCallback } from 'react';
import type { WsEvent } from '../types/issue';

const WS_RECONNECT_INTERVAL_MS = 3000;
const WS_MAX_RECONNECT_ATTEMPTS = 5;

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

interface UseWebSocketOptions {
  url: string;
  onMessage?: (event: WsEvent) => void;
  enabled?: boolean;
}

interface UseWebSocketReturn {
  status: ConnectionStatus;
  lastEvent: WsEvent | null;
  reconnectAttempt: number;
  disconnect: () => void;
}

export function useWebSocket({ url, onMessage, enabled = true }: UseWebSocketOptions): UseWebSocketReturn {
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');
  const [lastEvent, setLastEvent] = useState<WsEvent | null>(null);
  const [reconnectAttempt, setReconnectAttempt] = useState(0);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const enabledRef = useRef(enabled);
  enabledRef.current = enabled;

  const cleanup = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const connect = useCallback(() => {
    if (!enabledRef.current) return;
    cleanup();
    setStatus('connecting');

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setStatus('connected');
      setReconnectAttempt(0);
    };

    ws.onmessage = (event: MessageEvent) => {
      try {
        const parsed: WsEvent = JSON.parse(event.data);
        setLastEvent(parsed);
        onMessage?.(parsed);
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    ws.onerror = () => {
      setStatus('error');
    };

    ws.onclose = () => {
      setStatus('disconnected');
      wsRef.current = null;
      if (enabledRef.current) {
        setReconnectAttempt((prev) => {
          const next = prev + 1;
          if (next <= WS_MAX_RECONNECT_ATTEMPTS) {
            reconnectTimerRef.current = setTimeout(connect, WS_RECONNECT_INTERVAL_MS);
          }
          return next;
        });
      }
    };
  }, [url, onMessage, cleanup]);

  useEffect(() => {
    if (enabled) {
      connect();
    } else {
      cleanup();
      setStatus('disconnected');
    }
    return cleanup;
  }, [enabled, connect, cleanup]);

  const disconnect = useCallback(() => {
    enabledRef.current = false;
    cleanup();
    setStatus('disconnected');
  }, [cleanup]);

  return { status, lastEvent, reconnectAttempt, disconnect };
}
