import { useState, useEffect } from 'react';
import type { UseTimelineResult, TimelineIssue } from './types';
import { groupIssuesByEpic, calcDaysBetween, GANTT_CONFIG } from './gantt-utils';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';
const TIMELINE_ENDPOINT = `${API_BASE}/issues/timeline`;

export function useTimeline(): UseTimelineResult {
  const [issues, setIssues] = useState<TimelineIssue[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchTimeline(): Promise<void> {
      try {
        const res = await fetch(TIMELINE_ENDPOINT);
        if (!res.ok) {
          throw new Error(`Failed to fetch timeline: ${res.status} ${res.statusText}`);
        }
        const data: TimelineIssue[] = await res.json();
        if (!cancelled) {
          setIssues(data);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Unknown error');
          setIssues([]);
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    fetchTimeline();
    return () => { cancelled = true; };
  }, []);

  const epicGroups = groupIssuesByEpic(issues);

  let timelineStart = '';
  let totalDays = 0;

  if (issues.length > 0) {
    const allDates = issues.flatMap((i) => [i.startDate, i.dueDate]).sort();
    timelineStart = allDates[0];
    const timelineEnd = allDates[allDates.length - 1];
    totalDays = calcDaysBetween(timelineStart, timelineEnd) + GANTT_CONFIG.PADDING_DAYS;
  }

  return { epicGroups, timelineStart, totalDays, isLoading, error };
}
