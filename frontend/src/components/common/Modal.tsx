import { useEffect, useRef, type ReactNode } from 'react';
import { clsx } from 'clsx';
import { Button } from './Button';

interface Props {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  /** Prevent closing by clicking backdrop or pressing Escape */
  blocking?: boolean;
}

const sizeClass = {
  sm:  'max-w-sm',
  md:  'max-w-md',
  lg:  'max-w-lg',
  xl:  'max-w-2xl',
};

export function Modal({ open, onClose, title, children, size = 'md', blocking = false }: Props) {
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open || blocking) return;
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [open, blocking, onClose]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      aria-modal="true"
      role="dialog"
      aria-labelledby="modal-title"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        onClick={blocking ? undefined : onClose}
      />

      {/* Panel */}
      <div
        ref={dialogRef}
        className={clsx(
          'relative z-10 w-full bg-card rounded-lg shadow-xl border border-border',
          sizeClass[size]
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-border">
          <h2 id="modal-title" className="text-base font-semibold text-primary">
            {title}
          </h2>
          {!blocking && (
            <button
              onClick={onClose}
              className="text-meta hover:text-secondary transition-colors"
              aria-label="Close"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>

        {/* Content */}
        <div className="px-5 py-5">
          {children}
        </div>
      </div>
    </div>
  );
}
