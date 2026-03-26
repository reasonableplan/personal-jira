export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  offset: number;
  limit: number;
}

export interface ApiError {
  detail: string | ValidationError[];
}

export interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
}

export interface PaginationParams {
  offset?: number;
  limit?: number;
  sort_by?: string;
  order?: 'asc' | 'desc';
}

export interface DeleteResponse {
  detail: string;
}
