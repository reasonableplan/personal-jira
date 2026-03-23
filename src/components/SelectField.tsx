import React from 'react';

export interface SelectOption {
  value: string;
  label: string;
}

interface SelectFieldProps {
  label: string;
  value: string;
  options: SelectOption[];
  onChange: (value: string) => void;
  error?: string;
  disabled?: boolean;
}

export function SelectField({
  label,
  value,
  options,
  onChange,
  error,
  disabled = false,
}: SelectFieldProps) {
  const id = `select-${label.toLowerCase().replace(/\s+/g, '-')}`;

  return (
    <div className="select-field">
      <label htmlFor={id} className="select-field__label">
        {label}
      </label>
      <select
        id={id}
        className={`select-field__select ${error ? 'select-field__select--error' : ''}`}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {error && <span className="select-field__error">{error}</span>}
    </div>
  );
}
