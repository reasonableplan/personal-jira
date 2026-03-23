import { PAGE_SIZE_OPTIONS } from '../../constants/issue';

interface IssueTablePaginationProps {
  page: number;
  totalPages: number;
  total: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: number) => void;
}

export function IssueTablePagination({
  page,
  totalPages,
  total,
  pageSize,
  onPageChange,
  onPageSizeChange,
}: IssueTablePaginationProps) {
  return (
    <div className="flex items-center justify-between border-t border-gray-200 px-2 py-3 mt-2">
      <div className="flex items-center gap-2 text-sm text-gray-600">
        <span>Page {page} of {totalPages}</span>
        <span className="text-gray-400">·</span>
        <span>{total} total</span>
      </div>

      <div className="flex items-center gap-3">
        <select
          aria-label="Page size"
          value={pageSize}
          onChange={(e) => onPageSizeChange(Number(e.target.value))}
          className="rounded-md border border-gray-300 px-2 py-1 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          {PAGE_SIZE_OPTIONS.map((size) => (
            <option key={size} value={size}>{size} / page</option>
          ))}
        </select>

        <div className="flex gap-1">
          <button
            aria-label="First page"
            onClick={() => onPageChange(1)}
            disabled={page <= 1}
            className="rounded px-2 py-1 text-sm border border-gray-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            ««
          </button>
          <button
            aria-label="Previous page"
            onClick={() => onPageChange(page - 1)}
            disabled={page <= 1}
            className="rounded px-2 py-1 text-sm border border-gray-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            «
          </button>
          <button
            aria-label="Next page"
            onClick={() => onPageChange(page + 1)}
            disabled={page >= totalPages}
            className="rounded px-2 py-1 text-sm border border-gray-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            »
          </button>
          <button
            aria-label="Last page"
            onClick={() => onPageChange(totalPages)}
            disabled={page >= totalPages}
            className="rounded px-2 py-1 text-sm border border-gray-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            »»
          </button>
        </div>
      </div>
    </div>
  );
}
