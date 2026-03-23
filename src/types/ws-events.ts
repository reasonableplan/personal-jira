export enum WsEventType {
  ISSUE_CREATED = 'issue_created',
  ISSUE_UPDATED = 'issue_updated',
  ISSUE_DELETED = 'issue_deleted',
  ISSUE_ERROR = 'issue_error',
}

export interface WsIssuePayload {
  id: string;
  title: string;
  [key: string]: unknown;
}

export interface WsErrorPayload {
  message: string;
}

export interface WsEvent {
  type: WsEventType;
  data: WsIssuePayload | WsErrorPayload;
}

export const WS_TOAST_MAP: Record<WsEventType, { type: 'success' | 'error' | 'warning' | 'info'; prefix: string }> = {
  [WsEventType.ISSUE_CREATED]: { type: 'info', prefix: '이슈 생성' },
  [WsEventType.ISSUE_UPDATED]: { type: 'success', prefix: '이슈 수정' },
  [WsEventType.ISSUE_DELETED]: { type: 'warning', prefix: '이슈 삭제' },
  [WsEventType.ISSUE_ERROR]: { type: 'error', prefix: '오류' },
};
