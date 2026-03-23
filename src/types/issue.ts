export interface SearchResult {
  id: string;
  title: string;
  labels: string[];
}

export interface SearchAutocompleteProps {
  onSelect: (result: SearchResult) => void;
  placeholder?: string;
  debounceMs?: number;
  minQueryLength?: number;
  className?: string;
}

export interface UseSearchAutocompleteOptions {
  debounceMs?: number;
  minQueryLength?: number;
}
