import { useState, useCallback } from 'react';
import type { IssueFormData } from '../types/issue';
import { DEFAULT_FORM_DATA, TITLE_MAX_LENGTH } from '../types/issue';

export type FormErrors = Partial<Record<keyof IssueFormData, string>>;

export function useIssueForm(initial?: IssueFormData) {
  const initialValues = initial ?? DEFAULT_FORM_DATA;
  const [values, setValues] = useState<IssueFormData>({ ...initialValues });
  const [errors, setErrors] = useState<FormErrors>({});

  const setField = useCallback(
    <K extends keyof IssueFormData>(key: K, value: IssueFormData[K]) => {
      setValues((prev) => ({ ...prev, [key]: value }));
      setErrors((prev) => {
        const next = { ...prev };
        delete next[key];
        return next;
      });
    },
    []
  );

  const validate = useCallback((): boolean => {
    const next: FormErrors = {};
    const trimmed = values.title.trim();
    if (!trimmed) {
      next.title = 'Title is required';
    } else if (trimmed.length > TITLE_MAX_LENGTH) {
      next.title = `Title must be under ${TITLE_MAX_LENGTH} characters`;
    }
    setErrors(next);
    return Object.keys(next).length === 0;
  }, [values]);

  const reset = useCallback(() => {
    setValues({ ...initialValues });
    setErrors({});
  }, [initialValues]);

  return { values, errors, setField, validate, reset };
}
