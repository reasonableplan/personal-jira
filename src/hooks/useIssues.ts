import { useCallback, useEffect, useRef, useState } from 'react';
import { fetchIssues } from '../api/issues';
import { DEFAULT_PAGE_SIZE } from '../constants/issue';
import { Issue, IssueFilters, PaginatedResponse } from '../types/issue';

interface UseIssuesOptions {
  initialPage?: number;
  initialPageSize?: number;
  initialFilters?: IssueFilters;
  initialSortField?: string;
  initialSortOrder?: 'asc' | 'desc';
}

interface UseIssuesReturn {
  data: PaginatedResponse<Issue> | null;
  isLoading: boolean;
  error: string | null;
  page: number;
  pageSize: number;
  filters: IssueFilters;
  sortField: string | undefined;
  sortOrder: 'asc' | 'desc' | undefined;
  setPage: (page: number) => void;
  setPageSize: (size: number) => void;
  setFilters: (filters: IssueFilters) => void;
  setSorting: (field?: string, order?: 'asc' | 'desc') => void;
  refetch: () => void;
}

export function useIssues(options: UseIssuesOptions = {}): UseIssuesReturn {
  const {
    initialPage = 1,
    initialPageSize = DEFAULT_PAGE_SIZE,
    initialFilters = {},
    initialSortField,
    initialSortOrder,
  } = options;

  const [data, setData] = useState<PaginatedResponse<Issue> | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [filters, setFilters] = useState<IssueFilters>(initialFilters);
  const [sortField, setSortField] = useState<string | undefined>(initialSortField);
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc' | undefined>(initialSortOrder);
  const abortRef = useRef<AbortController | null>(null);

  const load = useCallback(async () => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setIsLoading(true);
    setError(null);

    try {
      const result = await fetchIssues(page, pageSize, filters, sortField, sortOrder);
      if (!controller.signal.aborted) {
        setData(result);
      }
    } catch (err) {
      if (!controller.signal.aborted) {
        setError(err instanceof Error ? err.message : 'Failed to fetch issues');
      }
    } finally {
      if (!controller.signal.aborted) {
        setIsLoading(false);
      }
    }
  }, [page, pageSize, filters, sortField, sortOrder]);

  useEffect(() => {
    load();
    return () => {
      abortRef.current?.abort();
    };
  }, [load]);

  const setSorting = useCallback((field?: string, order?: 'asc' | 'desc') => {
    setSortField(field);
    setSortOrder(order);
    setPage(1);
  }, []);

  const handleSetFilters = useCallback((newFilters: IssueFilters) => {
    setFilters(newFilters);
    setPage(1);
  }, []);

  const handleSetPageSize = useCallback((size: number) => {
    setPageSize(size);
    setPage(1);
  }, []);

  return {
    data,
    isLoading,
    error,
    page,
    pageSize,
    filters,
    sortField,
    sortOrder,
    setPage,
    setPageSize: handleSetPageSize,
    setFilters: handleSetFilters,
    setSorting,
    refetch: load,
  };
}
