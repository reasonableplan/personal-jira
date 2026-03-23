export interface SearchSuggestion {
  id: string;
  text: string;
  type: 'issue' | 'project' | 'user';
  status?: string;
}
