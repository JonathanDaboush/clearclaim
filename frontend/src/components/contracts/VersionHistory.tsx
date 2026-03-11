import { useState } from 'react';
import { format } from 'date-fns';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import ReactDiffViewer, { DiffMethod } from 'react-diff-viewer-continued';
import { contractsApi } from '@/api/contracts';
import type { ContractVersionData } from '@/api/contracts';
import { StatusBadge } from '@/components/common/StatusBadge';
import { HashDisplay } from '@/components/common/HashDisplay';
import { Button } from '@/components/common/Button';
import { toast } from 'react-toastify';

interface Props {
  contractId: string;
  /** Current logged-in user id */
  currentUserId: string;
  canApprove: boolean;
}

/**
 * VersionHistory
 * ─────────────────────────────────────────────────────────────────────────────
 * Shows the full chain of contract versions with:
 *  - Diff view (GitHub-style line-by-line) between any two versions
 *  - Content hash per version (integrity guarantee)
 *  - Revision approval status
 *  - Ability for authorised users to approve a pending revision
 *
 * This component directly supports legal defensibility by making all changes
 * visible and attributable (date, who created each version, hash).
 */
export function VersionHistory({ contractId, currentUserId, canApprove }: Props) {
  const qc = useQueryClient();
  const [selectedA, setSelectedA] = useState<ContractVersionData | null>(null);
  const [selectedB, setSelectedB] = useState<ContractVersionData | null>(null);
  const [showDiff, setShowDiff] = useState(false);

  const { data: versions = [], isLoading } = useQuery({
    queryKey: ['contract-versions', contractId],
    queryFn: () => contractsApi.getVersions(contractId),
  });

  const approveMutation = useMutation({
    mutationFn: (version_id: string) => contractsApi.approveRevision(version_id, currentUserId),
    onSuccess: () => {
      toast.success('Revision approved.');
      qc.invalidateQueries({ queryKey: ['contract-versions', contractId] });
    },
    onError: () => toast.error('Approval failed. Please try again.'),
  });

  const handleShowDiff = () => {
    if (!selectedA || !selectedB) return;
    setShowDiff(true);
  };

  if (isLoading) return <p className="text-sm text-slate-500 py-4">Loading version history…</p>;

  const sorted = [...versions].sort((a, b) => (b.version_number ?? 0) - (a.version_number ?? 0));

  return (
    <div className="space-y-4">
      <div className="card">
        <div className="card-header">
          <h3 className="text-sm font-semibold text-primary">Version History</h3>
          <p className="text-xs text-secondary mt-0.5">
            All revisions are immutably recorded. Each version has a unique content hash.
          </p>
        </div>

        <div className="divide-y divide-border">
          {sorted.map((v) => {
            const isCheckedA = selectedA?.id === v.id;
            const isCheckedB = selectedB?.id === v.id;

            return (
              <div key={v.id} className="px-5 py-3.5 flex items-start gap-4">
                {/* Compare checkboxes */}
                <div className="flex flex-col gap-1 pt-0.5 text-xs text-slate-400 items-center">
                  <label title="Compare from">
                    <input
                      type="radio"
                      name="compare-a"
                      checked={isCheckedA}
                      onChange={() => setSelectedA(v)}
                      className="sr-only"
                    />
                    <span
                      className={`block w-4 h-4 rounded-full border-2 cursor-pointer ${
                        isCheckedA ? 'bg-accent border-accent' : 'border-border'
                      }`}
                    />
                  </label>
                  <label title="Compare to">
                    <input
                      type="radio"
                      name="compare-b"
                      checked={isCheckedB}
                      onChange={() => setSelectedB(v)}
                      className="sr-only"
                    />
                    <span
                      className={`block w-4 h-4 rounded border-2 cursor-pointer ${
                        isCheckedB ? 'bg-confirmed border-confirmed' : 'border-border'
                      }`}
                    />
                  </label>
                </div>

                {/* Version info */}
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2 mb-1">
                    <span className="text-sm font-semibold text-primary">
                      Version {v.version_number ?? '—'}
                    </span>
                    {v.signed && (
                      <span className="badge-confirmed text-xs">Signed</span>
                    )}
                    <StatusBadge status={v.signed ? 'signed' : 'pending'} />
                  </div>

                  <p className="text-xs text-secondary">
                    Created {format(new Date(v.created_at), 'dd MMM yyyy, HH:mm')} by{' '}
                    <span className="text-primary">{v.created_by}</span>
                  </p>

                  <div className="mt-2">
                    <HashDisplay label="Content hash" hash={v.content_hash ?? ''} />
                  </div>
                </div>

                {/* Approval action */}
                {canApprove && !v.signed && (
                  <Button
                    size="sm"
                    variant="primary"
                    loading={approveMutation.isPending}
                    onClick={() => approveMutation.mutate(v.id)}
                  >
                    Approve Revision
                  </Button>
                )}
              </div>
            );
          })}
        </div>

        {/* Compare button */}
        {sorted.length >= 2 && (
          <div className="card-body border-t border-border flex items-center gap-3">
            <p className="text-xs text-secondary flex-1">
              Select two versions (circles) to compare them side-by-side.
            </p>
            <Button
              size="sm"
              disabled={!selectedA || !selectedB || selectedA.id === selectedB.id}
              onClick={handleShowDiff}
            >
              Compare Selected
            </Button>
          </div>
        )}
      </div>

      {/* Diff viewer */}
      {showDiff && selectedA && selectedB && (
        <div className="card overflow-hidden">
          <div className="card-header flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-primary">
                Version Comparison: v{Math.min(selectedA.version_number ?? 0, selectedB.version_number ?? 0)}{' '}
                → v{Math.max(selectedA.version_number ?? 0, selectedB.version_number ?? 0)}
              </h3>
              <p className="text-xs text-secondary mt-0.5">
                Highlighted additions and deletions. Green = added. Red = removed.
              </p>
            </div>
            <Button size="sm" variant="ghost" onClick={() => setShowDiff(false)}>
              Close
            </Button>
          </div>

          <div className="overflow-x-auto text-xs">
            <ReactDiffViewer
              oldValue={
                (selectedA.version_number ?? 0) < (selectedB.version_number ?? 0)
                  ? selectedA.content
                  : selectedB.content
              }
              newValue={
                (selectedA.version_number ?? 0) < (selectedB.version_number ?? 0)
                  ? selectedB.content
                  : selectedA.content
              }
              splitView={false}
              compareMethod={DiffMethod.WORDS}
              leftTitle={`Version ${Math.min(selectedA.version_number ?? 0, selectedB.version_number ?? 0)}`}
              rightTitle={`Version ${Math.max(selectedA.version_number ?? 0, selectedB.version_number ?? 0)}`}
              useDarkTheme={false}
              styles={{
                variables: {
                  light: {
                    fontSize: '12px',
                  } as Record<string, string>,
                },
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
