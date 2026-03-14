import { useState } from 'react';
import { format, formatDistanceToNow } from 'date-fns';
import { useQuery } from '@tanstack/react-query';
import { auditApi } from '@/api/audit';
import type { AuditEntryData } from '@/api/audit';
import { HashDisplay } from '@/components/common/HashDisplay';
import { exportApi } from '@/api/export';
import { clsx } from 'clsx';
interface Props {
  projectId?: string;
  contractId?: string;
}

type EventConfig = {
  label: string;
  dotClass: string;
  iconPath: string;
};

const EVENT_CONFIG: Record<string, EventConfig> = {
  contract_created: {
    label: 'Contract created',
    dotClass: 'bg-accent',
    iconPath:
      'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
  },
  contract_revised: {
    label: 'Revision submitted',
    dotClass: 'bg-pending',
    iconPath:
      'M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z',
  },
  revision_approved: {
    label: 'Revision approved',
    dotClass: 'bg-confirmed',
    iconPath: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
  },
  revision_rejected: {
    label: 'Revision rejected',
    dotClass: 'bg-disputed',
    iconPath: 'M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z',
  },
  contract_signed: {
    label: 'Contract signed',
    dotClass: 'bg-confirmed',
    iconPath:
      'M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z',
  },
  evidence_proposed: {
    label: 'Evidence submitted',
    dotClass: 'bg-[#6F8A87]',
    iconPath:
      'M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z',
  },
  evidence_approved: {
    label: 'Evidence approved',
    dotClass: 'bg-confirmed',
    iconPath: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
  },
  evidence_disputed: {
    label: 'Evidence disputed',
    dotClass: 'bg-disputed',
    iconPath:
      'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
  },
  evidence_deleted: {
    label: 'Evidence removed',
    dotClass: 'bg-disputed',
    iconPath:
      'M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16',
  },
  device_added: {
    label: 'Device authorized',
    dotClass: 'bg-info',
    iconPath:
      'M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z',
  },
  device_revoked: {
    label: 'Device revoked',
    dotClass: 'bg-pending',
    iconPath: 'M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636',
  },
  user_login: {
    label: 'User signed in',
    dotClass: 'bg-secondary',
    iconPath:
      'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
  },
  role_changed: {
    label: 'Role changed',
    dotClass: 'bg-info',
    iconPath:
      'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z',
  },
  member_added: {
    label: 'Member added',
    dotClass: 'bg-info',
    iconPath:
      'M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z',
  },
  suspicious_activity: {
    label: 'Suspicious activity',
    dotClass: 'bg-disputed',
    iconPath:
      'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
  },
};

const INTEGRITY_SIGNALS: Record<string, string> = {
  contract_signed:   'Signature authenticated',
  evidence_approved: 'Evidence timestamp recorded',
  revision_approved: 'Revision integrity confirmed',
  device_added:      'Identity verified',
};

function EventIcon({ path }: { path: string }) {
  return (
    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d={path} />
    </svg>
  );
}

/**
 * Timeline
 * ─────────────────────────────────────────────────────────────────────────────
 * Visual vertical chronological timeline — the "central spine" of a project
 * workspace (spec §6 / §7). Each event is a card with icon, label, actor,
 * timestamp, integrity signal, and expandable hash detail.
 *
 * Distinct from AuditTrail (which is the tabular-grid view on the contract
 * detail page). This component is used for Layer 2 project workspace navigation.
 */
export function Timeline({ projectId, contractId }: Props) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [exporting, setExporting] = useState(false);

  async function handleExportPdf() {
    if (!contractId) return;
    setExporting(true);
    try {
      const blob = await exportApi.timelinePdfBlob(contractId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `timeline-${contractId}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      // silently swallow export errors — user can retry
    } finally {
      setExporting(false);
    }
  }

  const { data: entries = [], isLoading } = useQuery({
    queryKey: ['audit', contractId ?? projectId],
    queryFn: () => auditApi.getEntries(contractId ?? projectId),
    refetchInterval: 30_000,
  });

  const { data: integrityResult } = useQuery({
    queryKey: ['audit-integrity', contractId ?? projectId],
    queryFn: () => auditApi.verifyEntries(),
    refetchInterval: 60_000,
    staleTime: 30_000,
  });

  const invalidIds = new Set<string>(integrityResult?.invalid_entry_ids ?? []);

  const sorted = [...(entries as AuditEntryData[])].sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime(),
  );

  const toggle = (id: string) =>
    setExpanded((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });

  if (isLoading) {
    return (
      <div className="space-y-4 py-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="flex gap-4 animate-pulse">
            <div className="w-10 h-10 rounded-full bg-border shrink-0" />
            <div className="flex-1 space-y-2 pt-1">
              <div className="h-3 bg-border rounded w-1/3" />
              <div className="h-2 bg-border rounded w-1/4" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (sorted.length === 0) {
    return (
      <div className="text-center py-14">
        <div className="w-12 h-12 rounded-full bg-section flex items-center justify-center mx-auto mb-3">
          <svg className="w-5 h-5 text-meta" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <p className="text-sm text-secondary font-medium">No events recorded yet</p>
        <p className="text-xs text-meta mt-1">
          Events will appear here as contracts are created, revised, and signed.
        </p>
      </div>
    );
  }

  return (
    <div className="relative pl-1">
      {/* Header row with optional PDF export */}
      {contractId && (
        <div className="flex justify-end mb-3">
          <button
            onClick={handleExportPdf}
            disabled={exporting}
            className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-md border border-border bg-card hover:bg-section text-secondary disabled:opacity-50 transition-colors"
          >
            <svg className="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            {exporting ? 'Exporting…' : 'Export PDF'}
          </button>
        </div>
      )}

      {/* Vertical rail */}
      <div
        className="absolute left-[19px] top-6 bottom-8 w-0.5 bg-border"
        aria-hidden="true"
      />

      <ol className="space-y-0">
        {sorted.map((entry) => {
          const cfg   = EVENT_CONFIG[entry.event_type];
          const isOpen = expanded.has(entry.id);
          const signal = INTEGRITY_SIGNALS[entry.event_type];
          const label  = cfg?.label
            ?? entry.event_type.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
          const isVerified = integrityResult !== undefined && !invalidIds.has(entry.id);
          const isTampered = integrityResult !== undefined && invalidIds.has(entry.id);

          return (
            <li key={entry.id} className="relative flex gap-4 pb-5">
              {/* Icon dot */}
              <div
                className={clsx(
                  'relative z-10 mt-1 flex h-10 w-10 shrink-0 items-center justify-center rounded-full ring-4 ring-background',
                  cfg?.dotClass ?? 'bg-meta',
                )}
                aria-hidden="true"
              >
                {cfg ? (
                  <EventIcon path={cfg.iconPath} />
                ) : (
                  <span className="w-2 h-2 rounded-full bg-white/80" />
                )}
              </div>

              {/* Card */}
              <div className="flex-1 min-w-0 pt-1">
                <button
                  className="w-full text-left rounded-lg border border-border bg-card hover:bg-section transition-colors p-4 group"
                  onClick={() => toggle(entry.id)}
                  aria-expanded={isOpen}
                >
                  <div className="flex items-start justify-between gap-2 sm:gap-3">
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-semibold text-primary truncate">{label}</p>

                      <div className="flex flex-wrap items-center gap-x-2 gap-y-1 mt-1">
                        <span className="text-xs text-secondary truncate max-w-[120px] sm:max-w-[200px]">
                          {entry.user_id ?? 'System'}
                        </span>
                        <span className="text-meta text-xs" aria-hidden="true">·</span>
                        <time
                          className="text-xs text-meta"
                          dateTime={entry.timestamp}
                          title={format(new Date(entry.timestamp), 'PPPpp')}
                        >
                          <span className="hidden sm:inline">{format(new Date(entry.timestamp), 'dd MMM yyyy, HH:mm')}</span>
                          <span className="sm:hidden">{format(new Date(entry.timestamp), 'dd MMM, HH:mm')}</span>
                        </time>
                        <span className="hidden sm:inline text-[10px] text-meta/60">
                          ({formatDistanceToNow(new Date(entry.timestamp), { addSuffix: true })})
                        </span>
                      </div>

                      {signal && (
                        <span className="inline-flex items-center gap-1 text-[10px] font-medium px-1.5 py-0.5 rounded-full mt-2 bg-confirmed/10 text-confirmed border border-confirmed/20">
                          <svg className="w-2.5 h-2.5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd"
                              d="M10 1a9 9 0 100 18A9 9 0 0010 1zm3.707 7.707a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                              clipRule="evenodd" />
                          </svg>
                          {signal}
                        </span>
                      )}

                      {/* Integrity indicator */}
                      {isTampered ? (
                        <span className="inline-flex items-center gap-1 text-[10px] font-medium px-1.5 py-0.5 rounded-full mt-2 bg-disputed/10 text-disputed border border-disputed/30">
                          <svg className="w-2.5 h-2.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                          </svg>
                          Integrity mismatch
                        </span>
                      ) : isVerified ? (
                        <span className="inline-flex items-center gap-1 text-[10px] font-medium px-1.5 py-0.5 rounded-full mt-2 bg-section text-meta border border-border">
                          <svg className="w-2.5 h-2.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                              d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                          </svg>
                          Hash verified
                        </span>
                      ) : null}
                    </div>

                    <svg
                      className={clsx(
                        'w-3.5 h-3.5 text-meta shrink-0 mt-0.5 transition-transform',
                        isOpen && 'rotate-180',
                      )}
                      fill="none" stroke="currentColor" viewBox="0 0 24 24"
                      aria-hidden="true"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </button>

                {/* Expanded detail */}
                {isOpen && (
                  <div className="mt-1.5 rounded-lg border border-border bg-section p-4 space-y-3 text-xs">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div>
                        <p className="text-meta uppercase tracking-wide mb-0.5">Event ID</p>
                        <p className="font-mono text-primary break-all">{entry.id}</p>
                      </div>
                      {entry.related_object_id && (
                        <div>
                          <p className="text-meta uppercase tracking-wide mb-0.5">Related Record</p>
                          <p className="font-mono text-primary break-all">{entry.related_object_id}</p>
                        </div>
                      )}
                      {entry.device_id && (
                        <div>
                          <p className="text-meta uppercase tracking-wide mb-0.5">Device</p>
                          <p className="font-mono text-primary break-all">{entry.device_id}</p>
                        </div>
                      )}
                    </div>

                    <HashDisplay label="Entry Hash" hash={entry.hash} />

                    {entry.details && (
                      <div>
                        <p className="text-meta uppercase tracking-wide mb-1">Details</p>
                        <pre className="record-box whitespace-pre-wrap">{entry.details}</pre>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
