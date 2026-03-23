import React from 'react';
import { useIssueForm } from '../hooks/useIssueForm';
import { MarkdownEditor } from './MarkdownEditor';
import { SelectField } from './SelectField';
import { LabelPicker } from './LabelPicker';
import {
  IssueType,
  IssuePriority,
  ISSUE_TYPE_LABELS,
  ISSUE_PRIORITY_LABELS,
} from '../types/issue';
import type { Issue, IssueFormData } from '../types/issue';

interface IssueFormProps {
  initialData?: Issue;
  onSubmit: (data: IssueFormData) => void;
  onCancel: () => void;
  availableLabels: string[];
  isSubmitting?: boolean;
  serverError?: string;
}

const TYPE_OPTIONS = Object.values(IssueType).map((v) => ({
  value: v,
  label: ISSUE_TYPE_LABELS[v],
}));

const PRIORITY_OPTIONS = Object.values(IssuePriority).map((v) => ({
  value: v,
  label: ISSUE_PRIORITY_LABELS[v],
}));

export function IssueForm({
  initialData,
  onSubmit,
  onCancel,
  availableLabels,
  isSubmitting = false,
  serverError,
}: IssueFormProps) {
  const isEdit = !!initialData;
  const { values, errors, setField, validate } = useIssueForm(
    initialData
      ? {
          title: initialData.title,
          description: initialData.description,
          issue_type: initialData.issue_type,
          priority: initialData.priority,
          labels: initialData.labels,
        }
      : undefined
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    onSubmit(values);
  };

  return (
    <form className="issue-form" onSubmit={handleSubmit}>
      {serverError && (
        <div className="issue-form__error" role="alert">
          {serverError}
        </div>
      )}

      <div className="issue-form__field">
        <label htmlFor="issue-title" className="issue-form__label">
          Title
        </label>
        <input
          id="issue-title"
          className={`issue-form__input ${errors.title ? 'issue-form__input--error' : ''}`}
          value={values.title}
          onChange={(e) => setField('title', e.target.value)}
          disabled={isSubmitting}
        />
        {errors.title && (
          <span className="issue-form__field-error">{errors.title}</span>
        )}
      </div>

      <div className="issue-form__row">
        <SelectField
          label="Type"
          value={values.issue_type}
          options={TYPE_OPTIONS}
          onChange={(v) => setField('issue_type', v as IssueType)}
          disabled={isSubmitting}
        />
        <SelectField
          label="Priority"
          value={values.priority}
          options={PRIORITY_OPTIONS}
          onChange={(v) => setField('priority', v as IssuePriority)}
          disabled={isSubmitting}
        />
      </div>

      <div className="issue-form__field">
        <label className="issue-form__label">Description</label>
        <MarkdownEditor
          value={values.description}
          onChange={(v) => setField('description', v)}
          placeholder="Describe the issue (markdown supported)..."
          disabled={isSubmitting}
        />
      </div>

      <div className="issue-form__field">
        <label className="issue-form__label">Labels</label>
        <LabelPicker
          availableLabels={availableLabels}
          selected={values.labels}
          onChange={(labels) => setField('labels', labels)}
          allowCustom
        />
      </div>

      <div className="issue-form__actions">
        <button
          type="button"
          className="issue-form__btn issue-form__btn--cancel"
          onClick={onCancel}
          disabled={isSubmitting}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="issue-form__btn issue-form__btn--submit"
          disabled={isSubmitting}
        >
          {isEdit ? 'Save' : 'Create'}
        </button>
      </div>
    </form>
  );
}
