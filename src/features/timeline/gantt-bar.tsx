import { useState } from 'react';
import type { TimelineIssue } from './types';
import { calcBarPosition, getStatusColor } from './gantt-utils';

interface GanttBarProps {
  issue: TimelineIssue;
  timelineStart: string;
}

export function GanttBar({ issue, timelineStart }: GanttBarProps): React.JSX.Element {
  const [hovered, setHovered] = useState(false);
  const { left, width } = calcBarPosition(issue.startDate, issue.dueDate, timelineStart);
  const color = getStatusColor(issue.status);

  return (
    <div className="relative h-8 my-0.5">
      <div
        data-testid={`gantt-bar-${issue.id}`}
        className={`absolute top-0 h-full rounded ${color} text-white text-xs flex items-center px-2 cursor-pointer transition-opacity hover:opacity-90 overflow-hidden whitespace-nowrap`}
        style={{ left: `${left}px`, width: `${width}px` }}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
      >
        <span className="truncate">{issue.title}</span>
      </div>

      {hovered && (
        <div
          className="absolute z-50 bg-gray-900 text-white text-xs rounded-lg px-3 py-2 shadow-lg pointer-events-none"
          style={{ left: `${left}px`, top: '-60px' }}
        >
          <p className="font-semibold">{issue.title}</p>
          <p>{issue.startDate} ~ {issue.dueDate}</p>
          <p>{issue.status} · <span className="font-medium">{issue.priority}</span></p>
        </div>
      )}
    </div>
  );
}
