/**
 * ContractEditor
 * ─────────────────────────────────────────────────────────────────────────────
 * Dedicated contract drafting / editing page.
 *
 * Responsibilities:
 *  - Create a new contract (version 1, state = DRAFT) for a given project
 *  - Edit and submit a revision to an existing contract
 *
 * Routes:
 *  /projects/:projectId/contracts/new
 *  /projects/:projectId/contracts/:contractId/edit
 */
import { useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { contractsApi } from '@/api/contracts';
import { useAuthStore } from '@/stores/authStore';
import { Button } from '@/components/common/Button';
import { toast } from 'react-toastify';

export default function ContractEditor() {
  const { projectId, contractId } = useParams<{ projectId: string; contractId?: string }>();
  const { session } = useAuthStore();
  const navigate   = useNavigate();

  const isRevision = !!contractId;

  // Pre-fill content when editing an existing contract
  const { data: versions = [] } = useQuery({
    queryKey: ['contract-versions', contractId],
    queryFn:  () => contractsApi.getVersions(contractId!),
    enabled:  isRevision,
  });

  const latestContent = (versions as { content: string; version_number?: number }[]).reduce(
    (best, v) => ((v.version_number ?? 0) > (best.version_number ?? 0) ? v : best),
    { content: '', version_number: 0 } as { content: string; version_number: number },
  ).content;

  const [name,    setName]    = useState('');
  const [content, setContent] = useState('');
  const initialized = isRevision ? content !== '' || latestContent === '' : true;

  // Populate content from existing version once loaded
  if (isRevision && latestContent && !content) {
    setContent(latestContent);
  }

  const createMutation = useMutation({
    mutationFn: () =>
      contractsApi.create(projectId!, session!.user_id, content, name || 'Untitled Contract'),
    onSuccess: (res) => {
      toast.success('Contract created.');
      navigate(`/projects/${projectId}/contracts/${res.contract_id}`);
    },
    onError: () => toast.error('Failed to create contract.'),
  });

  const reviseMutation = useMutation({
    mutationFn: () =>
      contractsApi.revise(contractId!, content, session!.user_id),
    onSuccess: () => {
      toast.success('Revision submitted. All parties must approve before activation.');
      navigate(`/projects/${projectId}/contracts/${contractId}`);
    },
    onError: () => toast.error('Failed to submit revision.'),
  });

  const handleSave = () => {
    if (!content.trim()) { toast.error('Contract content cannot be empty.'); return; }
    if (isRevision) reviseMutation.mutate(); else createMutation.mutate();
  };

  const isPending = createMutation.isPending || reviseMutation.isPending;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="page-header">
        <nav className="flex items-center gap-1 text-xs text-meta mb-2">
          <Link to="/projects" className="hover:text-accent">Projects</Link>
          <span className="mx-1">›</span>
          <Link to={`/projects/${projectId}`} className="hover:text-accent">Project</Link>
          <span className="mx-1">›</span>
          <span className="text-primary">{isRevision ? 'Edit Contract' : 'New Contract'}</span>
        </nav>
        <h1 className="page-title">{isRevision ? 'Revise Contract' : 'Draft New Contract'}</h1>
      </div>

      <div className="card">
        <div className="card-body space-y-5">
          {!isRevision && (
            <div>
              <label className="form-label" htmlFor="contract-name">Contract Name</label>
              <input
                id="contract-name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="form-input"
                placeholder="e.g. Employment Agreement — Jane Smith"
              />
            </div>
          )}

          <div>
            <label className="form-label" htmlFor="contract-content">
              Contract Content
              {isRevision && (
                <span className="ml-2 text-xs text-meta font-normal">
                  (editing creates a new version — all parties must re-approve)
                </span>
              )}
            </label>
            <textarea
              id="contract-content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="form-input font-mono text-sm resize-none"
              rows={20}
              placeholder="Enter the full contract text here…"
            />
            <p className="text-xs text-meta mt-1">{content.length.toLocaleString()} characters</p>
          </div>

          <div className="flex gap-3 justify-end">
            <Button
              variant="secondary"
              onClick={() =>
                navigate(isRevision ? `/projects/${projectId}/contracts/${contractId}` : `/projects/${projectId}`)
              }
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              loading={isPending}
              disabled={!content.trim() || !initialized}
              onClick={handleSave}
            >
              {isRevision ? 'Submit Revision' : 'Create Contract'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
