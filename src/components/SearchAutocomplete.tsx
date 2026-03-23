import React, { useRef, useState, useCallback } from 'react';
import { useSearchAutocomplete } from '../hooks/useSearchAutocomplete';
import { SearchResult, SearchAutocompleteProps } from '../types/issue';
import { SEARCH_DEBOUNCE_MS, SEARCH_MIN_QUERY_LENGTH } from '../constants/api';
import styles from './SearchAutocomplete.module.css';

export const SearchAutocomplete: React.FC<SearchAutocompleteProps> = ({
  onSelect,
  placeholder = '이슈 검색...',
  debounceMs = SEARCH_DEBOUNCE_MS,
  minQueryLength = SEARCH_MIN_QUERY_LENGTH,
  className,
}) => {
  const { query, setQuery, results, isLoading, isOpen, error, close } =
    useSearchAutocomplete({ debounceMs, minQueryLength });

  const [activeIndex, setActiveIndex] = useState(-1);
  const listRef = useRef<HTMLUListElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSelect = useCallback(
    (result: SearchResult) => {
      onSelect(result);
      close();
      setActiveIndex(-1);
    },
    [onSelect, close]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (!isOpen || results.length === 0) return;

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setActiveIndex((prev) =>
            prev < results.length - 1 ? prev + 1 : prev
          );
          break;
        case 'ArrowUp':
          e.preventDefault();
          setActiveIndex((prev) => (prev > 0 ? prev - 1 : prev));
          break;
        case 'Enter':
          e.preventDefault();
          if (activeIndex >= 0 && activeIndex < results.length) {
            handleSelect(results[activeIndex]);
          }
          break;
        case 'Escape':
          e.preventDefault();
          close();
          setActiveIndex(-1);
          break;
      }
    },
    [isOpen, results, activeIndex, handleSelect, close]
  );

  const listboxId = 'search-autocomplete-listbox';

  return (
    <div className={`${styles.container} ${className ?? ''}`}>
      <input
        ref={inputRef}
        role="combobox"
        aria-autocomplete="list"
        aria-expanded={isOpen}
        aria-controls={isOpen ? listboxId : undefined}
        aria-activedescendant={
          activeIndex >= 0 ? `search-option-${activeIndex}` : undefined
        }
        type="text"
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          setActiveIndex(-1);
        }}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        className={styles.input}
      />

      {isLoading && (
        <div role="status" className={styles.loading}>
          <span className={styles.spinner} aria-label="검색 중" />
        </div>
      )}

      {error && (
        <div role="alert" className={styles.error}>
          {error}
        </div>
      )}

      {isOpen && results.length > 0 && (
        <ul
          ref={listRef}
          id={listboxId}
          role="listbox"
          className={styles.dropdown}
        >
          {results.map((result, index) => (
            <li
              key={result.id}
              id={`search-option-${index}`}
              role="option"
              aria-selected={index === activeIndex}
              className={`${styles.option} ${
                index === activeIndex ? styles.optionActive : ''
              }`}
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => handleSelect(result)}
              onMouseEnter={() => setActiveIndex(index)}
            >
              <span className={styles.title}>{result.title}</span>
              {result.labels.length > 0 && (
                <span className={styles.labels}>
                  {result.labels.map((label) => (
                    <span key={label} className={styles.badge}>
                      {label}
                    </span>
                  ))}
                </span>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
