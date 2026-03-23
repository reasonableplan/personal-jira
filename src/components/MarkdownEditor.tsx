import React, { useState } from 'react';
import { renderMarkdown } from '../utils/markdown';

type Tab = 'write' | 'preview';

interface MarkdownEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  minRows?: number;
}

export function MarkdownEditor({
  value,
  onChange,
  placeholder,
  disabled = false,
  minRows = 6,
}: MarkdownEditorProps) {
  const [activeTab, setActiveTab] = useState<Tab>('write');

  return (
    <div className="markdown-editor">
      <div className="markdown-editor__tabs" role="tablist">
        <button
          role="tab"
          aria-selected={activeTab === 'write'}
          className={`markdown-editor__tab ${activeTab === 'write' ? 'markdown-editor__tab--active' : ''}`}
          onClick={() => setActiveTab('write')}
          type="button"
        >
          Write
        </button>
        <button
          role="tab"
          aria-selected={activeTab === 'preview'}
          className={`markdown-editor__tab ${activeTab === 'preview' ? 'markdown-editor__tab--active' : ''}`}
          onClick={() => setActiveTab('preview')}
          type="button"
        >
          Preview
        </button>
      </div>
      {activeTab === 'write' ? (
        <textarea
          className="markdown-editor__textarea"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          disabled={disabled}
          rows={minRows}
        />
      ) : (
        <div
          className="markdown-editor__preview"
          data-testid="markdown-preview"
          dangerouslySetInnerHTML={{ __html: renderMarkdown(value) }}
        />
      )}
    </div>
  );
}
