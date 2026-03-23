import { useMemo } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
  SortingState,
} from '@tanstack/react-table';
import { useIssues } from '../../hooks/useIssues';
import { columns } from './columns';
import { IssueTableToolbar } from './IssueTableToolbar';
import { IssueTablePagination } from './IssueTablePagination';

export function IssueTable() {
  const {
    data,
    isLoading,
    error,
    page,
    pageSize,
    filters,
    sortField,
    sortOrder,
    setPage,
    setPageSize,
    setFilters,
    setSorting,
  } = useIssues();

  const sorting: SortingState = useMemo(
    () => (sortField ? [{ id: sortField, desc: sortOrder === 'desc' }] : []),
    [sortField, sortOrder]
  );

  const table = useReactTable({
    data: data?.items ?? [],
    columns,
    state: { sorting },
    onSortingChange: (updater) => {
      const next = typeof updater === 'function' ? updater(sorting) : updater;
      if (next.length === 0) {
        setSorting(undefined, undefined);
      } else {
        setSorting(next[0].id, next[0].desc ? 'desc' : 'asc');
      }
    },
    getCoreRowModel: getCoreRowModel(),
    manualSorting: true,
    manualPagination: true,
    pageCount: data?.total_pages ?? -1,
  });

  if (isLoading && !data) {
    return (
      <div role="status" className="flex items-center justify-center py-12 text-gray-500">
        <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        Loading issues...
      </div>
    );
  }

  if (error) {
    return (
      <div role="alert" className="rounded-md bg-red-50 p-4 text-sm text-red-700">
        {error}
      </div>
    );
  }

  return (
    <div className="w-full">
      <IssueTableToolbar filters={filters} onFiltersChange={setFilters} />

      <div className="overflow-x-auto rounded-lg border border-gray-200">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 select-none cursor-pointer hover:bg-gray-100"
                    onClick={header.column.getToggleSortingHandler()}
                  >
                    <div className="flex items-center gap-1">
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      {{
                        asc: ' ↑',
                        desc: ' ↓',
                      }[header.column.getIsSorted() as string] ?? null}
                    </div>
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {table.getRowModel().rows.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="px-4 py-8 text-center text-sm text-gray-500">
                  No issues found
                </td>
              </tr>
            ) : (
              table.getRowModel().rows.map((row) => (
                <tr key={row.id} className="hover:bg-gray-50 transition-colors">
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id} className="px-4 py-3 text-sm whitespace-nowrap">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {data && (
        <IssueTablePagination
          page={data.page}
          totalPages={data.total_pages}
          total={data.total}
          pageSize={pageSize}
          onPageChange={setPage}
          onPageSizeChange={setPageSize}
        />
      )}
    </div>
  );
}
