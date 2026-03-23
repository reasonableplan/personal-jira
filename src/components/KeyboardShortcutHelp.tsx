import type { FC, KeyboardEvent, MouseEvent } from 'react';
import type { KeyboardShortcutGroup } from '../types/keyboard';

interface KeyboardShortcutHelpProps {
  isOpen: boolean;
  onClose: () => void;
  groups: KeyboardShortcutGroup[];
}

export const KeyboardShortcutHelp: FC<KeyboardShortcutHelpProps> = ({
  isOpen,
  onClose,
  groups,
}) => {
  if (!isOpen) return null;

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Escape') onClose();
  };

  const handleContentClick = (e: MouseEvent) => {
    e.stopPropagation();
  };

  return (
    <div
      role="dialog"
      aria-label="키보드 단축키"
      onKeyDown={handleKeyDown}
      tabIndex={-1}
      style={{
        position: 'fixed',
        inset: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
      }}
    >
      <div
        data-testid="shortcut-help-backdrop"
        onClick={onClose}
        style={{
          position: 'absolute',
          inset: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
        }}
      />
      <div
        data-testid="shortcut-help-content"
        onClick={handleContentClick}
        style={{
          position: 'relative',
          backgroundColor: 'var(--bg-primary, #fff)',
          borderRadius: '8px',
          padding: '24px',
          minWidth: '320px',
          maxWidth: '480px',
          boxShadow: '0 4px 24px rgba(0, 0, 0, 0.15)',
        }}
      >
        <h2 style={{ margin: '0 0 16px', fontSize: '18px', fontWeight: 600 }}>
          키보드 단축키
        </h2>
        {groups.map((group) => (
          <div key={group.name} style={{ marginBottom: '16px' }}>
            <h3 style={{ margin: '0 0 8px', fontSize: '14px', fontWeight: 600, color: 'var(--text-secondary, #666)' }}>
              {group.name}
            </h3>
            <dl style={{ margin: 0 }}>
              {group.shortcuts.map((shortcut) => (
                <div
                  key={shortcut.key}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '4px 0',
                  }}
                >
                  <dd style={{ margin: 0, fontSize: '14px' }}>{shortcut.description}</dd>
                  <dt>
                    <kbd
                      style={{
                        display: 'inline-block',
                        padding: '2px 8px',
                        fontSize: '12px',
                        fontFamily: 'monospace',
                        backgroundColor: 'var(--bg-secondary, #f5f5f5)',
                        border: '1px solid var(--border-color, #ddd)',
                        borderRadius: '4px',
                        minWidth: '24px',
                        textAlign: 'center',
                      }}
                    >
                      {shortcut.key}
                    </kbd>
                  </dt>
                </div>
              ))}
            </dl>
          </div>
        ))}
      </div>
    </div>
  );
};