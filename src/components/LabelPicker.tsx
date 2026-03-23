import React, { useState } from 'react';

interface LabelPickerProps {
  availableLabels: string[];
  selected: string[];
  onChange: (labels: string[]) => void;
  allowCustom?: boolean;
}

export function LabelPicker({
  availableLabels,
  selected,
  onChange,
  allowCustom = false,
}: LabelPickerProps) {
  const [customValue, setCustomValue] = useState('');

  const toggle = (label: string) => {
    if (selected.includes(label)) {
      onChange(selected.filter((l) => l !== label));
    } else {
      onChange([...selected, label]);
    }
  };

  const handleCustomKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key !== 'Enter') return;
    const trimmed = customValue.trim();
    if (!trimmed || selected.includes(trimmed)) return;
    onChange([...selected, trimmed]);
    setCustomValue('');
  };

  return (
    <div className="label-picker">
      <div className="label-picker__list">
        {availableLabels.map((label) => (
          <button
            key={label}
            type="button"
            className={`label-picker__chip ${selected.includes(label) ? 'label-picker__chip--selected' : ''}`}
            aria-pressed={selected.includes(label)}
            onClick={() => toggle(label)}
          >
            {label}
          </button>
        ))}
      </div>
      {allowCustom && (
        <input
          className="label-picker__input"
          placeholder="Add label..."
          value={customValue}
          onChange={(e) => setCustomValue(e.target.value)}
          onKeyDown={handleCustomKeyDown}
        />
      )}
    </div>
  );
}
