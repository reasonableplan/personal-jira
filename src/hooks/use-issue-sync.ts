import { useCallback } from 'react';
import { useWebSocket } from './use-websocket';
import { useToast } from './use-toast';
import { WsEventType, WS_TOAST_MAP, type WsEvent, type WsIssuePayload, type WsErrorPayload } from '../types/ws-events';

const WS_ISSUES_PATH = '/ws/issues';

function buildWsUrl(): string {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = import.meta.env.VITE_WS_HOST ?? window.location.host;
  return `${protocol}//${host}${WS_ISSUES_PATH}`;
}

interface UseIssueSyncOptions {
  onMessage?: (event: WsEvent) => void;
}

export function useIssueSync(options?: UseIssueSyncOptions) {
  const { addToast } = useToast();

  const handleMessage = useCallback(
    (raw: unknown) => {
      const event = raw as WsEvent;
      const mapping = WS_TOAST_MAP[event.type];
      if (mapping) {
        const displayText =
          event.type === WsEventType.ISSUE_ERROR
            ? (event.data as WsErrorPayload).message
            : `${mapping.prefix}: ${(event.data as WsIssuePayload).title}`;
        addToast({ type: mapping.type, message: displayText });
      }
      options?.onMessage?.(event);
    },
    [addToast, options]
  );

  const { isConnected, sendMessage } = useWebSocket(buildWsUrl(), {
    onMessage: handleMessage,
  });

  return { isConnected, sendMessage };
}
