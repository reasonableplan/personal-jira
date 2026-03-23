import { useState, useRef, useCallback, useEffect } from 'react';
import type { SearchSuggestion } from '../types/search';

const DEFAULT_DEBOUNCE_MS = 300;
const DEFAULT_MIN_QUERY_LENGTH = 1;

interface SearchAutocompleteProps {
  onSearch: (query: string) => void;
  onSelect: (suggestion: SearchSuggestion) => void;
  fetchSuggestions: (query: string) => Promise<SearchSuggestion[]>;
  placeholder?: string;
  minQueryLength?: number;
  debounceMs?: number;
}

export function SearchAutocomplete({
  onSearch,
  onSelect,
  fetchSuggestions,
  placeholder = 'Search...',
  minQueryLength = DEFAULT_MIN_QUERY_LENGTH,
  debounceMs = DEFAULT_DEBOUNCE_MS,
}: SearchAutocompleteProps) {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [highlightIndex, setHighlightIndex] = useState(-1);
  const [isLoading, setIsLoading] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleChange = useCallback(
    (value: string) => {
      setQuery(value);
      setHighlightIndex(-1);

      if (debounceRef.current) clearTimeout(debounceRef.current);

      if (value.length < minQueryLength) {
        setSuggestions([]);
        setIsOpen(false);
        return;
      }

      setIsLoading(true);
      debounceRef.current = setTimeout(async () => {
        try {
          const results = await fetchSuggestions(value);
          setSuggestions(results);
          setIsOpen(true);
        } catch (err) {
          console.error('Failed to fetch suggestions:', err);
          setSuggestions([]);
        } finally {
          setIsLoading(false);
        }
      }, debounceMs);
    },
    [fetchSuggestions, minQueryLength, debounceMs]
  );

  const selectSuggestion = useCallback(
    (suggestion: SearchSuggestion) => {
      onSelect(suggestion);
      setQuery(suggestion.text);
      setIsOpen(false);
      setSuggestions([]);
    },
    [onSelect]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (!isOpen) return;

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setHighlightIndex((prev) =>
            prev < suggestions.length - 1 ? prev + 1 : prev
          );
          break;
        case 'ArrowUp':
          e.preventDefault();
          setHighlightIndex((prev) => (prev > 0 ? prev - 1 : prev));
          break;
        case 'Enter':
          e.preventDefault();
          if (highlightIndex >= 0 && highlightIndex < suggestions.length) {
            selectSuggestion(suggestions[highlightIndex]);
          }
          break;
        case 'Escape':
          setIsOpen(false);
          setSuggestions([]);
          break;
      }
    },
    [isOpen, suggestions, highlightIndex, selectSuggestion]
  );

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      onSearch(query);
    },
    [onSearch, query]
  );

  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, []);

  return (
    <form onSubmit={handleSubmit} className="search-autocomplete">
      <div className="search-input-wrapper">
        <input
          role="combobox"
          type="text"
          value={query}
          onChange={(e) => handleChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          aria-autocomplete="list"
          aria-expanded={isOpen}
          aria-controls="search-suggestions"
        />
        {isLoading && <span data-testid="search-spinner" className="spinner" />}
      </div>

      {isOpen && suggestions.length > 0 && (
        <ul id="search-suggestions" role="listbox" className="suggestions-list">
          {suggestions.map((suggestion, index) => (
            <li
              key={suggestion.id}
              role="option"
              aria-selected={index === highlightIndex}
              className={index === highlightIndex ? 'highlighted' : ''}
              onClick={() => selectSuggestion(suggestion)}
            >
              <span className="suggestion-text">{suggestion.text}</span>
              {suggestion.status && (
                <span className="suggestion-status">{suggestion.status}</span>
              )}
            </li>
          ))}
        </ul>
      )}
    </form>
  );
}
