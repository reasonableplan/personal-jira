import React, { useEffect, useRef } from 'react';
import { IssueForm } from './IssueForm';
import type { Issue, IssueFormData } from '../types/issue';

interface IssueFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: IssueFormData) => void;
  availableLabels: string[];
  initialData?: Issue;
  isSubmitting?: boolean;
  serverError?: string;
}

export function IssueFormModal({
  isOpen,
  onClose,
  onSubmit,
  availableLabels,
  initialData,
  isSubmitting,
  serverError,
}: IssueFormModalProps) {
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const isEdit = !!initialData;

  return (
    <div
      className="modal-backdrop"
      data-testid="modal-backdrop"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        ref={dialogRef}
        onKeyDown={(e) => {
          if (e.key === 'Escape') onClose();
        }}
      >
        <h2 className="modal__title">
          {isEdit ? 'Edit Issue' : 'Create Issue'}
        </h2>
        <IssueForm
          initialData={initialData}
          onSubmit={onSubmit}
          onCancel={onClose}
          availableLabels={availableLabels}
          isSubmitting={isSubmitting}
          serverError={serverError}
        />
      </div>
    </div>
  );
}
