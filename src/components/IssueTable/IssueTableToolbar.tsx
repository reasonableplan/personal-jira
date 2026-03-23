import { useCallback, useEffect, useRef, useState } from 'react';
import { IssueFilters, IssuePriority, IssueStatus, IssueType } from '../../types/issue';
import { STATUS_LABELS, PRIORITY_LABELS, TYPE_LABELS } from '../../constants/issue';

const SEARCH_DEBOUNCE_MS = 300;

interface IssueTableToolbarProps {
  filters: IssueFilters;
  onFiltersChange: (filters: IssueFilters) => void;
}

export function IssueTableToolbar({ filters, onFiltersChange }: IssueTableToolbarProps) {
  const [searchValue, setSearchValue] = useState(filters.search ?? '');
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, []);

  const handleSearchChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = e.target.value;
      setSearchValue(value);

      if (debounceRef.current) clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(() => {
        onFiltersChange({ ...filters, search: value || undefined });
      }, SEARCH_DEBOUNCE_MS);
    },
    [filters, onFiltersChange]
  );

  const handleSelectChange = useCallback(
    (key: keyof IssueFilters) => (e: React.ChangeEvent<HTMLSelectElement>) => {
      const value = e.target.value || undefined;
      onFiltersChange({ ...filters, [key]: value });
    },
    [filters, onFiltersChange]
  );

  return (
    <div className="flex flex-wrap items-center gap-3 mb-4">
      <input
        type="text"
        placeholder="Search issues..."
        value={searchValue}
        onChange={handleSearchChange}
        className="rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
      />

      <select
        aria-label="Filter by status"
        value={filters.status ?? ''}
        onChange={handleSelectChange('status')}
        className="rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
      >
        <option value="">All Statuses</option>
        {Object.entries(STATUS_LABELS).map(([value, label]) => (
          <option key={value} value={value}>{label}</option>
        ))}
      </select>

      <select
        aria-label="Filter by priority"
        value={filters.priority ?? ''}
        onChange={handleSelectChange('priority')}
        className="rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
      >
        <option value="">All Priorities</option>
        {Object.entries(PRIORITY_LABELS).map(([value, label]) => (
          <option key={value} value={value}>{label}</option>
        ))}
      </select>

      <select
        aria-label="Filter by type"
        value={filters.issue_type ?? ''}
        onChange={handleSelectChange('issue_type')}
        className="rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
      >
        <option value="">All Types</option>
        {Object.entries(TYPE_LABELS).map(([value, label]) => (
          <option key={value} value={value}>{label}</option>
        ))}
      </select>
    </div>
  );
}
