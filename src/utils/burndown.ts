export function generateIdealLine(totalPoints: number, days: number): number[] {
  if (days <= 1) return [days === 1 ? 0 : totalPoints];
  const decrement = totalPoints / (days - 1);
  return Array.from({ length: days }, (_, i) => totalPoints - decrement * i);
}

export function calcCompletionRate(totalPoints: number, remaining: number): number {
  if (totalPoints === 0) return 0;
  return Math.round(((totalPoints - remaining) / totalPoints) * 100);
}

export function calcVelocity(completedPoints: number, days: number): number {
  if (days === 0) return 0;
  return Math.round((completedPoints / days) * 100) / 100;
}

export function isSprintActive(
  startDate: string,
  endDate: string,
  today: Date = new Date(),
): boolean {
  const start = new Date(startDate);
  const end = new Date(endDate);
  start.setHours(0, 0, 0, 0);
  end.setHours(23, 59, 59, 999);
  return today >= start && today <= end;
}
