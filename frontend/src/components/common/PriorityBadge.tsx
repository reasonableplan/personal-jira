import {
  AlertTriangle,
  ArrowDown,
  ArrowUp,
  ChevronsDown,
  ChevronsUp,
} from 'lucide-react';
import type { Priority } from '@/types/priority';
import { PRIORITY, PRIORITY_CONFIG } from '@/types/priority';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface PriorityBadgeProps {
  priority: Priority;
  className?: string;
}

const PRIORITY_ICONS: Record<Priority, React.ReactNode> = {
  [PRIORITY.CRITICAL]: <ChevronsUp className="h-3 w-3" />,
  [PRIORITY.HIGH]: <ArrowUp className="h-3 w-3" />,
  [PRIORITY.MEDIUM]: <AlertTriangle className="h-3 w-3" />,
  [PRIORITY.LOW]: <ArrowDown className="h-3 w-3" />,
  [PRIORITY.LOWEST]: <ChevronsDown className="h-3 w-3" />,
};

export function PriorityBadge({ priority, className }: PriorityBadgeProps) {
  const config = PRIORITY_CONFIG[priority];

  return (
    <Badge
      variant="outline"
      className={cn('gap-1', config.className, className)}
    >
      {PRIORITY_ICONS[priority]}
      {config.label}
    </Badge>
  );
}
