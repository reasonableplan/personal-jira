import { useTimeline } from './use-timeline';
import { GanttBar } from './gantt-bar';
import { buildTimelineDays, GANTT_CONFIG } from './gantt-utils';

export function GanttChart(): React.JSX.Element {
  const { epicGroups, timelineStart, totalDays, isLoading, error } = useTimeline();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        Loading timeline...
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64 text-red-600">
        {error}
      </div>
    );
  }

  if (epicGroups.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">
        No timeline data available
      </div>
    );
  }

  const days = buildTimelineDays(timelineStart, totalDays);
  const chartWidth = totalDays * GANTT_CONFIG.DAY_WIDTH;

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden bg-white">
      <h2 className="text-lg font-semibold px-4 py-3 border-b border-gray-200 bg-gray-50">
        Timeline
      </h2>

      <div className="overflow-x-auto">
        <div className="flex" style={{ minWidth: `${GANTT_CONFIG.LABEL_WIDTH + chartWidth}px` }}>
          {/* Left labels */}
          <div className="flex-shrink-0" style={{ width: `${GANTT_CONFIG.LABEL_WIDTH}px` }}>
            <div
              className="border-b border-r border-gray-200 bg-gray-50 px-3 font-medium text-sm text-gray-600 flex items-center"
              style={{ height: `${GANTT_CONFIG.HEADER_HEIGHT}px` }}
            >
              Epic / Issue
            </div>
            {epicGroups.map((group) => (
              <div key={group.epicId}>
                <div
                  className="border-b border-r border-gray-200 bg-indigo-50 px-3 font-semibold text-sm text-indigo-800 flex items-center"
                  style={{ height: `${GANTT_CONFIG.ROW_HEIGHT}px` }}
                >
                  {group.epicTitle}
                </div>
                {group.issues.map((issue) => (
                  <div
                    key={issue.id}
                    className="border-b border-r border-gray-100 px-3 pl-6 text-sm text-gray-700 flex items-center truncate"
                    style={{ height: `${GANTT_CONFIG.ROW_HEIGHT}px` }}
                  >
                    {issue.title}
                  </div>
                ))}
              </div>
            ))}
          </div>

          {/* Right chart area */}
          <div className="flex-1 relative">
            {/* Date header */}
            <div
              className="flex border-b border-gray-200 bg-gray-50"
              style={{ height: `${GANTT_CONFIG.HEADER_HEIGHT}px` }}
            >
              {days.map((day) => (
                <div
                  key={day.date}
                  className={`flex-shrink-0 flex items-center justify-center text-xs border-r border-gray-100 ${
                    day.isWeekend ? 'text-red-400 bg-red-50/50' : 'text-gray-500'
                  }`}
                  style={{ width: `${GANTT_CONFIG.DAY_WIDTH}px` }}
                >
                  {day.label}
                </div>
              ))}
            </div>

            {/* Bars */}
            {epicGroups.map((group) => (
              <div key={group.epicId}>
                {/* Epic summary row */}
                <div
                  className="relative border-b border-gray-200 bg-indigo-50/30"
                  style={{ height: `${GANTT_CONFIG.ROW_HEIGHT}px` }}
                />
                {/* Issue bars */}
                {group.issues.map((issue) => (
                  <div
                    key={issue.id}
                    className="relative border-b border-gray-100"
                    style={{ height: `${GANTT_CONFIG.ROW_HEIGHT}px` }}
                  >
                    <GanttBar issue={issue} timelineStart={timelineStart} />
                  </div>
                ))}
              </div>
            ))}

            {/* Today line */}
            <TodayMarker timelineStart={timelineStart} chartHeight="100%" />
          </div>
        </div>
      </div>
    </div>
  );
}

function TodayMarker({ timelineStart, chartHeight }: { timelineStart: string; chartHeight: string }): React.JSX.Element | null {
  const today = new Date().toISOString().slice(0, 10);
  const offsetDays = Math.round(
    (new Date(today).getTime() - new Date(timelineStart).getTime()) / (1000 * 60 * 60 * 24),
  );

  if (offsetDays < 0) return null;

  const left = offsetDays * GANTT_CONFIG.DAY_WIDTH + GANTT_CONFIG.DAY_WIDTH / 2;

  return (
    <div
      className="absolute top-0 w-0.5 bg-red-500 pointer-events-none z-10"
      style={{ left: `${left}px`, height: chartHeight }}
      aria-label="Today"
    />
  );
}
