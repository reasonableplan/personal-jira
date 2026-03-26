import type { Label } from '@/types/label';
import { cn } from '@/lib/utils';

interface LabelBadgeProps {
  label: Label;
  className?: string;
}

export function LabelBadge({ label, className }: LabelBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold text-white',
        className,
      )}
      style={{ backgroundColor: label.color }}
    >
      {label.name}
    </span>
  );
}
