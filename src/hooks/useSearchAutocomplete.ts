import { useState, useEffect, useRef, useCallback } from 'react';
import { useDebounce } from './useDebounce';
import { searchIssues } from '../services/issueApi';
import { SearchResult, UseSearchAutocompleteOptions } from '../types/issue';
import { SEARCH_DEBOUNCE_MS, SEARCH_MIN_QUERY_LENGTH } from '../constants/api';

export function useSearchAutocomplete(options?: UseSearchAutocompleteOptions) {
  const debounceMs = options?.debounceMs ?? SEARCH_DEBOUNCE_MS;
  const minQueryLength = options?.minQueryLength ?? SEARCH_MIN_QUERY_LENGTH;

  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const debouncedQuery = useDebounce(query, debounceMs);
  const abortControllerRef = useRef<AbortController | null>(null);
  const requestIdRef = useRef(0);

  useEffect(() => {
    if (debouncedQuery.length < minQueryLength) {
      setResults([]);
      setIsOpen(false);
      setError(null);
      return;
    }

    const currentRequestId = ++requestIdRef.current;

    abortControllerRef.current?.abort();
    const controller = new AbortController();
    abortControllerRef.current = controller;

    setIsLoading(true);
    setError(null);

    searchIssues(debouncedQuery, controller.signal)
      .then((data) => {
        if (currentRequestId !== requestIdRef.current) return;
        setResults(data);
        setIsOpen(true);
      })
      .catch((err: Error) => {
        if (err.name === 'AbortError') return;
        if (currentRequestId !== requestIdRef.current) return;
        setError('검색 중 오류가 발생했습니다');
        setResults([]);
      })
      .finally(() => {
        if (currentRequestId === requestIdRef.current) {
          setIsLoading(false);
        }
      });

    return () => {
      controller.abort();
    };
  }, [debouncedQuery, minQueryLength]);

  const close = useCallback(() => {
    setIsOpen(false);
  }, []);

  return { query, setQuery, results, isLoading, isOpen, error, close };
}
