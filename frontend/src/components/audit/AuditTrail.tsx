import { useState } from 'react';
import { format } from 'date-fns';
import { useQuery, useMutation } from '@tanstack/react-query';
import { auditApi } from '@/api/audit';
import type { AuditEntryData } from '@/api/audit';
import { HashDisplay } from '@/components/common/HashDisplay';
import { Button } from '@/components/common/Button';
import { toast } from 'react-toastify';
import { clsx } from 'clsx';

interface Props {
  contractId?: string;
  projectId?:  string;
}

const EVENT_COLORS: Record<string, string> = {
  contract_created:     'bg-info',
  contract_revised:     'bg-accent',
  revision_approved:    'bg-confirmed',
  contract_signed:      'bg-confirmed',
  evidence_proposed:    'bg-teal',
  evidence_approved:    'bg-confirmed',
  evidence_disputed:    'bg-disputed',
  evidence_deleted:     'bg-disputed',
  user_login:           'bg-meta',
  device_added:         'bg-meta',
  device_revoked:       'bg-pending',
  suspicious_activity:  'bg-disputed',
};

const dotColor = (event: string) =>
  EVENT_COLORS[event] ?? 'bg-meta';

const INTEGRITY_SIGNALS: Record<string, { label: string; color: string }> = {
  contract_signed:   { label: 'Signature authenticated',      color: 'bg-confirmed/15 text-confirmed border border-confirmed/30' },
  evidence_approved: { label: 'Evidence timestamp recorded',  color: 'bg-confirmed/15 text-confirmed border border-confirmed/30' },
  device_added:      { label: 'Identity verified',            color: 'bg-info/15 text-info border border-info/30' },
  user_login:        { label: 'Identity verified',            color: 'bg-info/15 text-info border border-info/30' },
  revision_approved: { label: 'Revision integrity confirmed', color: 'bg-accent/15 text-accent border border-accent/30' },
};

/**
 * AuditTrail
 * â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
 * Exposes the append-only, cryptographically chained audit log for a contract
 * or project. Each entry shows:
 *   - Event type, user, timestamp, device, IP
 *   - Entry hash and previous hash (chain linkage)
 *   - Chain integrity verification status
 *
 * The "Verify Chain" action calls the backend validator which walks the full
 * hash chain and reports any broken link.
 */
export function AuditTrail({ contractId, projectId }: Props) {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const { data: entries = [], isLoading } = useQuery({
    queryKey: ['audit', contractId ?? projectId],
    queryFn: () => auditApi.getEntries(contractId ?? projectId),
  });

  const verifyMutation = useMutation({
    mutationFn: () => auditApi.verifyChain(),
    onSuccess: (valid) => {
      if (valid) {
        toast.success('Audit chain verified â€” no tampering detected.');
      } else {
        toast.error('Chain integrity failure detected.');
      }
    },
    onError: () => toast.error('Chain verification request failed.'),
  });

  const toggleExpanded = (id: string) =>
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));

  if (isLoading) return <p className="text-sm text-secondary py-4">Loading audit trailâ€¦</p>;

  const sorted = [...(entries as AuditEntryData[])].sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  return (
    <div className="card">
      <div className="card-header flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-primary">Audit Trail</h3>
          <p className="text-xs text-secondary mt-0.5">
            Append-only, cryptographically chained log. {sorted.length} events recorded.
          </p>
        </div>
        <Button
          size="sm"
          variant="secondary"
          loading={verifyMutation.isPending}
          onClick={() => verifyMutation.mutate()}
        >
          Verify Chain Integrity
        </Button>
      </div>

      {/* Header row */}
      <div className="hidden sm:grid grid-cols-12 gap-2 px-5 py-2 bg-section border-b border-border text-xs font-medium text-secondary uppercase tracking-wide">
        <div className="col-span-3">Timestamp</div>
        <div className="col-span-3">Event</div>
        <div className="col-span-4">User</div>
        <div className="col-span-2">Details</div>
      </div>

      <div className="divide-y divide-border">
        {sorted.length === 0 && (
          <p className="px-5 py-4 text-sm text-secondary">No audit entries found.</p>
        )}

        {sorted.map((entry) => {
          const isOpen = expanded[entry.id] ?? false;

          return (
            <div key={entry.id}>
              {/* Main row */}
              <div
                className="grid grid-cols-12 gap-2 px-5 py-3 cursor-pointer hover:bg-section transition-colors"
                onClick={() => setExpanded((prev) => ({ ...prev, [entry.id]: !prev[entry.id] }))}
              >
                {/* Timestamp */}
                <div className="col-span-12 sm:col-span-3 flex items-center gap-2">
                  <span className={clsx('w-2 h-2 rounded-full shrink-0', dotColor(entry.event_type))} />
                  <span className="text-xs text-secondary font-mono">
                    {format(new Date(entry.timestamp), 'dd MMM yy, HH:mm:ss')}
                  </span>
                </div>

                {/* Event */}
                <div className="col-span-12 sm:col-span-3 space-y-1">
                  <span className="text-xs font-medium text-primary">
                    {entry.event_type.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                  </span>
                  {INTEGRITY_SIGNALS[entry.event_type] && (
                    <span className={clsx('inline-flex items-center gap-1 text-[10px] font-medium px-1.5 py-0.5 rounded-full', INTEGRITY_SIGNALS[entry.event_type].color)}>
                      <svg className="w-2.5 h-2.5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 1a9 9 0 100 18A9 9 0 0010 1zm3.707 7.707a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      {INTEGRITY_SIGNALS[entry.event_type].label}
                    </span>
                  )}
                </div>

                {/* User */}
                <div className="col-span-11 sm:col-span-4">
                  <span className="text-xs text-secondary truncate">{entry.user_id ?? 'System'}</span>
                </div>

                {/* Expand */}
                <div className="col-span-1 flex items-center justify-end">
                  <svg
                    className={clsx('w-3.5 h-3.5 text-meta transition-transform', isOpen && 'rotate-180')}
                    fill="none" stroke="currentColor" viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>

              {/* Expanded detail */}
              {isOpen && (
                <div className="px-5 pb-4 bg-section space-y-3">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                    <div>
                      <p className="text-meta uppercase tracking-wide mb-0.5">Event ID</p>
                      <p className="font-mono text-primary break-all">{entry.id}</p>
                    </div>
                    <div>
                      <p className="text-meta uppercase tracking-wide mb-0.5">Related Object</p>
                      <p className="font-mono text-primary break-all">{entry.related_object_id || 'â€”'}</p>
                    </div>
                  </div>

                  <HashDisplay label="Entry Hash" hash={entry.hash} />

                  {entry.details && (
                    <div>
                      <p className="text-xs text-meta uppercase tracking-wide mb-1">Details</p>
                      <pre className="record-box whitespace-pre-wrap">{entry.details}</pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
