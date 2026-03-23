const BOLD_RE = /\*\*(.+?)\*\*/g;
const ITALIC_RE = /\*(.+?)\*/g;
const H3_RE = /^### (.+)$/gm;
const H2_RE = /^## (.+)$/gm;
const H1_RE = /^# (.+)$/gm;
const CODE_RE = /`([^`]+)`/g;
const LINK_RE = /\[([^\]]+)\]\(([^)]+)\)/g;
const BR_RE = /\n/g;

export function renderMarkdown(md: string): string {
  let html = md
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  html = html
    .replace(H3_RE, '<h3>$1</h3>')
    .replace(H2_RE, '<h2>$1</h2>')
    .replace(H1_RE, '<h1>$1</h1>')
    .replace(BOLD_RE, '<strong>$1</strong>')
    .replace(ITALIC_RE, '<em>$1</em>')
    .replace(CODE_RE, '<code>$1</code>')
    .replace(LINK_RE, '<a href="$2">$1</a>')
    .replace(BR_RE, '<br/>');

  return html;
}
