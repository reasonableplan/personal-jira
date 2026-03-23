import { createColumnHelper } from '@tanstack/react-table';
import { Issue } from '../../types/issue';
import {
  STATUS_LABELS,
  PRIORITY_LABELS,
  TYPE_LABELS,
  STATUS_COLOR,
  PRIORITY_COLOR,
} from '../../constants/issue';

const columnHelper = createColumnHelper<Issue>();

function Badge({ label, className }: { label: string; className: string }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${className}`}>
      {label}
    </span>
  );
}

function formatDate(dateString: string): string {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date(dateString));
}

export const columns = [
  columnHelper.accessor('title', {
    header: 'Title',
    cell: (info) => (
      <span className="font-medium text-gray-900" title={info.getValue()}>
        {info.getValue()}
      </span>
    ),
    enableSorting: true,
  }),
  columnHelper.accessor('issue_type', {
    header: 'Type',
    cell: (info) => TYPE_LABELS[info.getValue()],
    enableSorting: true,
  }),
  columnHelper.accessor('status', {
    header: 'Status',
    cell: (info) => (
      <Badge label={STATUS_LABELS[info.getValue()]} className={STATUS_COLOR[info.getValue()]} />
    ),
    enableSorting: true,
  }),
  columnHelper.accessor('priority', {
    header: 'Priority',
    cell: (info) => (
      <Badge label={PRIORITY_LABELS[info.getValue()]} className={PRIORITY_COLOR[info.getValue()]} />
    ),
    enableSorting: true,
  }),
  columnHelper.accessor('assignee', {
    header: 'Assignee',
    cell: (info) => info.getValue() ?? <span className="text-gray-400">—</span>,
    enableSorting: true,
  }),
  columnHelper.accessor('created_at', {
    header: 'Created',
    cell: (info) => formatDate(info.getValue()),
    enableSorting: true,
  }),
];
