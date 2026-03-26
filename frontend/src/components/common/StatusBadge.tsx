import type { TaskStatus } from '@/types/task';
import { TASK_STATUS, TASK_STATUS_LABELS } from '@/types/task';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface StatusBadgeProps {
  status: TaskStatus;
  className?: string;
}

const STATUS_STYLES: Record<TaskStatus, string> = {
  [TASK_STATUS.TODO]: 'bg-gray-100 text-gray-800 border-gray-200',
  [TASK_STATUS.IN_PROGRESS]: 'bg-blue-100 text-blue-800 border-blue-200',
  [TASK_STATUS.IN_REVIEW]: 'bg-purple-100 text-purple-800 border-purple-200',
  [TASK_STATUS.DONE]: 'bg-green-100 text-green-800 border-green-200',
};

export function StatusBadge({ status, className }: StatusBadgeProps) {
  return (
    <Badge
      variant="outline"
      className={cn(STATUS_STYLES[status], className)}
    >
      {TASK_STATUS_LABELS[status]}
    </Badge>
  );
}
