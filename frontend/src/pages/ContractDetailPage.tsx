import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { contractsApi } from '@/api/contracts';
import type { ContractVersionData } from '@/api/contracts';
import { projectsApi } from '@/api/projects';
import { ContractViewer } from '@/components/contracts/ContractViewer';
import { VersionHistory } from '@/components/contracts/VersionHistory';
import { SigningFlow } from '@/components/contracts/SigningFlow';
import { SignaturePanel } from '@/components/contracts/SignaturePanel';
import { EvidencePanel } from '@/components/evidence/EvidencePanel';
import { AuditTrail } from '@/components/audit/AuditTrail';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Button } from '@/components/common/Button';
import { Modal } from '@/components/common/Modal';
import { useAuthStore } from '@/stores/authStore';
import { exportApi } from '@/api/export';
import { toast } from 'react-toastify';

type Tab = 'contract' | 'versions' | 'signatures' | 'evidence' | 'audit';

export default function ContractDetailPage() {
  const { projectId, contractId } = useParams<{ projectId: string; contractId: string }>();
  const { session } = useAuthStore();
  const qc = useQueryClient();

  const [tab,           setTab]           = useState<Tab>('contract');
  const [signing,       setSigning]       = useState(false);
  const [reviseOpen,    setReviseOpen]    = useState(false);
  const [reviseContent, setReviseContent] = useState('');

  const { data: versions = [], isLoading } = useQuery({
    queryKey: ['contract-versions', contractId],
    queryFn:  () => contractsApi.getVersions(contractId!),
    enabled:  !!contractId,
  });

  const { data: userProjects = [] } = useQuery({
    queryKey: ['user-projects', session?.user_id],
    queryFn:  () => projectsApi.getUserProjects(session!.user_id),
    enabled:  !!session?.user_id,
  });

  const { data: projectContracts = [] } = useQuery({
    queryKey: ['project-contracts', projectId],
    queryFn:  () => projectsApi.getProjectContracts(projectId!),
    enabled:  !!projectId,
  });

  const projectName = (userProjects as { id: string; name: string }[]).find((p) => p.id === projectId)?.name ?? 'Project';
  const contractName = (projectContracts as { id: string; name?: string }[]).find((c) => c.id === contractId)?.name ?? 'Contract';

  const activeVersion: ContractVersionData | undefined =
    versions.find((v) => v.id === versions[0]?.id) ?? versions[0];

  const reviseMutation = useMutation({
    mutationFn: () => contractsApi.revise(contractId!, reviseContent, session!.user_id),
    onSuccess: () => {
      toast.success('Revision submitted. All parties must approve before activation.');
      qc.invalidateQueries({ queryKey: ['contract-versions', contractId] });
      setReviseOpen(false);
      setReviseContent('');
    },
    onError: () => toast.error('Revision failed.'),
  });

  const exportMutation = useMutation({
    mutationFn: () => exportApi.contractHistory(contractId!),
    onSuccess: (res) => {
      const blob = new Blob([JSON.stringify(res, null, 2)], { type: 'application/json' });
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement('a');
      a.href     = url;
      a.download = `clearclaim-contract-${contractId}-export.json`;
      a.click();
      URL.revokeObjectURL(url);
    },
    onError: () => toast.error('Export failed.'),
  });

  const TABS: { id: Tab; label: string }[] = [
    { id: 'contract',   label: 'Contract'    },
    { id: 'versions',   label: 'Versions'    },
    { id: 'signatures', label: 'Signatures'  },
    { id: 'evidence',   label: 'Evidence'    },
    { id: 'audit',      label: 'Audit Trail' },
  ];

  if (isLoading || !contractId) {
    return <div className="p-6 text-sm text-secondary">Loading contractâ€¦</div>;
  }

  return (
    <div>
      {/* Header */}
      <div className="page-header">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <nav className="flex items-center gap-1 text-xs text-meta mb-2">
              <Link to="/projects" className="hover:text-accent">Projects</Link>
              <span className="mx-1">›</span>
              <Link to={`/projects/${projectId}`} className="hover:text-accent">{projectName}</Link>
              <span className="mx-1">›</span>
              <span className="text-primary">{contractName}</span>
            </nav>
            <h1 className="page-title">{contractName}</h1>
            {activeVersion && (
              <div className="flex items-center gap-2 mt-1">
                <p className="page-subtitle">
                  Version {activeVersion.version_number} Â· {activeVersion.id.slice(0, 16)}â€¦
                </p>
              </div>
            )}
          </div>

          <div className="flex flex-wrap gap-2">
            <Button size="sm" variant="secondary" onClick={() => setReviseOpen(true)}>
              Propose Revision
            </Button>
            <Button
              size="sm" variant="secondary"
              loading={exportMutation.isPending}
              onClick={() => exportMutation.mutate()}
            >
              Export Record
            </Button>
            {activeVersion && (
              <Button size="sm" variant="primary" onClick={() => setSigning(true)}>
                Sign Contract
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Signing flow overlay */}
      {signing && activeVersion && (
        <div className="px-4">
          <SigningFlow
            version={activeVersion}
            onComplete={() => {
              setSigning(false);
              setTab('signatures');
            }}
            onCancel={() => setSigning(false)}
          />
        </div>
      )}

      {!signing && (
        <>
          {/* Tabs */}
          <div className="px-6 border-b border-border bg-card flex gap-1 overflow-x-auto">
            {TABS.map((t) => (
              <button
                key={t.id}
                onClick={() => setTab(t.id)}
                className={`
                  px-3 py-3 text-sm border-b-2 transition-colors whitespace-nowrap
                  ${tab === t.id
                    ? 'border-accent text-accent font-semibold'
                    : 'border-transparent text-secondary hover:text-primary'}
                `}
              >
                {t.label}
              </button>
            ))}
          </div>

          <div className="px-6 py-6">
            {tab === 'contract'   && activeVersion && (
              <ContractViewer version={activeVersion} onReviewConfirmed={() => {}} />
            )}
            {tab === 'versions'   && (
              <VersionHistory
                contractId={contractId}
                currentUserId={session?.user_id ?? ''}
                canApprove
                canReject
              />
            )}
            {tab === 'signatures' && activeVersion && (
              <SignaturePanel versionId={activeVersion.id} />
            )}
            {tab === 'evidence'   && (
              <EvidencePanel contractId={contractId} canAdd canRequestDeletion canApprove />
            )}
            {tab === 'audit'      && <AuditTrail contractId={contractId} />}
          </div>
        </>
      )}

      {/* Revise Modal */}
      <Modal
        open={reviseOpen}
        onClose={() => setReviseOpen(false)}
        title="Propose Contract Revision"
        size="xl"
      >
        <div className="space-y-4">
          <div className="legal-notice text-xs">
            Each revision creates a new version. All parties must approve the revision before
            it becomes active. All changes are logged and the previous version is preserved.
          </div>

          {activeVersion && (
            <div>
              <p className="form-label mb-2">Current contract text (v{activeVersion.version_number})</p>
              <pre className="record-box max-h-48 overflow-y-auto">{activeVersion.content}</pre>
            </div>
          )}

          <div>
            <label className="form-label">Revised Contract Text</label>
            <textarea
              value={reviseContent}
              onChange={(e) => setReviseContent(e.target.value)}
              rows={10}
              className="form-textarea font-mono text-xs"
              placeholder="Paste or type the full revised contract text hereâ€¦"
            />
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => setReviseOpen(false)}>Cancel</Button>
            <Button
              variant="primary"
              loading={reviseMutation.isPending}
              disabled={!reviseContent.trim()}
              onClick={() => reviseMutation.mutate()}
            >
              Submit Revision for Approval
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
