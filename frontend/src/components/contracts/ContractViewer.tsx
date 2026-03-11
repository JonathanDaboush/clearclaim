import { useRef, useState, useEffect } from 'react';
import { format } from 'date-fns';
import type { ContractVersionData } from '@/api/contracts';
import { StatusBadge } from '@/components/common/StatusBadge';
import { HashDisplay } from '@/components/common/HashDisplay';

interface Props {
  version: ContractVersionData;
  /** Called when user has scrolled to the bottom and confirmed review */
  onReviewConfirmed: () => void;
  /** True while we are inside the signing flow — forces scroll + checkbox */
  enforceReview?: boolean;
}

/**
 * ContractViewer
 * ─────────────────────────────────────────────────────────────────────────────
 * Legal safeguard: the user must scroll through the entire contract and check
 * a confirmation box before they are permitted to proceed to the signing step.
 *
 * This component intentionally does NOT render any "Sign" button itself —
 * that is the responsibility of the parent (SigningFlow).
 */
export function ContractViewer({ version, onReviewConfirmed, enforceReview = false }: Props) {
  const contentRef   = useRef<HTMLDivElement>(null);
  const [scrolled,   setScrolled]   = useState(false);
  const [confirmed,  setConfirmed]  = useState(false);
  const [showWarning, setShowWarning] = useState(false);

  // Reset when a new version is loaded
  useEffect(() => {
    setScrolled(false);
    setConfirmed(false);
    setShowWarning(false);
  }, [version.id]);

  const handleScroll = () => {
    const el = contentRef.current;
    if (!el) return;
    const atBottom = el.scrollHeight - el.scrollTop <= el.clientHeight + 40;
    if (atBottom) setScrolled(true);
  };

  const handleConfirmChange = (checked: boolean) => {
    if (enforceReview && !scrolled) {
      setShowWarning(true);
      return;
    }
    setConfirmed(checked);
    if (checked) {
      setShowWarning(false);
      onReviewConfirmed();
    }
  };

  return (
    <div className="flex flex-col gap-4">
      {/* Version metadata bar */}
      <div className="card">
        <div className="card-body">
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div>
              <p className="text-xs text-secondary uppercase tracking-wide mb-0.5">Version</p>
              <p className="text-sm font-semibold text-primary">v{version.version_number}</p>
            </div>
            <div>
              <p className="text-xs text-secondary uppercase tracking-wide mb-0.5">Status</p>
              <StatusBadge status={version.signed ? 'confirmed' : 'pending'} />
            </div>
            <div>
              <p className="text-xs text-secondary uppercase tracking-wide mb-0.5">Created</p>
              <p className="text-sm text-primary">
                {format(new Date(version.created_at), 'dd MMM yyyy, HH:mm')}
              </p>
            </div>
            <div>
              <p className="text-xs text-secondary uppercase tracking-wide mb-0.5">Prepared by</p>
              <p className="text-sm text-primary truncate">{version.created_by}</p>
            </div>
          </div>

        </div>
      </div>

      {/* Contract content */}
      <div className="card">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-primary">
              Contract — Version {version.version_number}
            </h3>
            {enforceReview && !scrolled && (
              <span className="text-xs text-pending bg-[#FEF9EC] border border-[#F5DFA0] px-2 py-0.5 rounded">
                Scroll to the bottom to confirm you have read the full document
              </span>
            )}
            {scrolled && (
              <span className="text-xs text-confirmed bg-[#E8F5EE] border border-[#B9E0CC] px-2 py-0.5 rounded">
                Document reviewed
              </span>
            )}
          </div>
        </div>

        <div
          ref={contentRef}
          onScroll={handleScroll}
          className="px-5 py-4 max-h-[520px] overflow-y-auto text-sm text-primary whitespace-pre-wrap font-mono leading-relaxed border-b border-border"
          style={{ scrollBehavior: 'smooth' }}
        >
          {version.content}
        </div>

        {/* Review confirmation — contextual to signing */}
        {enforceReview && (
          <div className="px-5 py-4">
            {showWarning && (
              <div className="legal-notice mb-3 text-xs">
                You must scroll through the entire document before confirming you have reviewed it.
              </div>
            )}
            <label className="flex items-start gap-3 cursor-pointer group">
              <input
                type="checkbox"
                checked={confirmed}
                onChange={(e) => handleConfirmChange(e.target.checked)}
                className="mt-0.5 w-4 h-4 rounded border-border text-accent focus:ring-accent"
              />
              <span className="text-sm text-primary leading-snug group-hover:text-primary">
                I confirm that I have read and understood the full contract text above, including
                all clauses, obligations, and the document hash listed above.
              </span>
            </label>
          </div>
        )}
      </div>
    </div>
  );
}
