import { http, HttpResponse } from 'msw';
import type { Issue, Comment } from '@/types/issue';
import { IssueStatus, IssuePriority } from '@/types/issue';

const API_BASE = '/api/v1';

let issueIdCounter = 1;
let commentIdCounter = 1;
const issues: Issue[] = [];
const comments: Map<string, Comment[]> = new Map();

export function resetMockData(): void {
  issueIdCounter = 1;
  commentIdCounter = 1;
  issues.length = 0;
  comments.clear();
}

export const handlers = [
  http.get(`${API_BASE}/issues`, () => {
    return HttpResponse.json(issues);
  }),

  http.post(`${API_BASE}/issues`, async ({ request }) => {
    const body = (await request.json()) as Partial<Issue>;
    const issue: Issue = {
      id: String(issueIdCounter++),
      title: body.title ?? '',
      description: body.description ?? '',
      status: IssueStatus.BACKLOG,
      priority: body.priority ?? IssuePriority.MEDIUM,
      assignee: body.assignee ?? null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    issues.push(issue);
    return HttpResponse.json(issue, { status: 201 });
  }),

  http.get(`${API_BASE}/issues/:id`, ({ params }) => {
    const issue = issues.find((i) => i.id === params.id);
    if (!issue) return HttpResponse.json({ detail: 'Not found' }, { status: 404 });
    return HttpResponse.json(issue);
  }),

  http.post(`${API_BASE}/issues/:id/transition`, async ({ params, request }) => {
    const issue = issues.find((i) => i.id === params.id);
    if (!issue) return HttpResponse.json({ detail: 'Not found' }, { status: 404 });
    const body = (await request.json()) as { status: IssueStatus };
    issue.status = body.status;
    issue.updated_at = new Date().toISOString();
    return HttpResponse.json(issue);
  }),

  http.get(`${API_BASE}/issues/:id/comments`, ({ params }) => {
    const issueComments = comments.get(params.id as string) ?? [];
    return HttpResponse.json(issueComments);
  }),

  http.post(`${API_BASE}/issues/:id/comments`, async ({ params, request }) => {
    const body = (await request.json()) as { content: string };
    const comment: Comment = {
      id: String(commentIdCounter++),
      issue_id: params.id as string,
      content: body.content,
      author: 'test-user',
      created_at: new Date().toISOString(),
    };
    const existing = comments.get(params.id as string) ?? [];
    existing.push(comment);
    comments.set(params.id as string, existing);
    return HttpResponse.json(comment, { status: 201 });
  }),
];
