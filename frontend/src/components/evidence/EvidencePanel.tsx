import { useState } from 'react';
import { format } from 'date-fns';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { evidenceApi } from '@/api/evidence';
import type { EvidenceData } from '@/api/evidence';
import { HashDisplay } from '@/components/common/HashDisplay';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Button } from '@/components/common/Button';
import { Modal } from '@/components/common/Modal';
import { useAuthStore } from '@/stores/authStore';
import { toast } from 'react-toastify';

interface Props {
  contractId: string;
  canAdd?: boolean;
  canRequestDeletion?: boolean;
  canApprove?: boolean;
}

const FILE_TYPES_ALLOWED = [
  'application/pdf',
  'image/jpeg',
  'image/png',
  'image/webp',
  'video/mp4',
  'text/plain',
];
const MAX_FILE_MB = 10;

async function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve((reader.result as string).split(',')[1] ?? '');
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

/**
 * EvidencePanel
 * â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
 * Legal design requirements:
 *  - Evidence is never silently replaced. Only additions via unanimous consent.
 *  - Every item shows: uploader, timestamp, file hash, and status.
 *  - Deletion requests are formally recorded and require approval.
 */
export function EvidencePanel({ contractId, canAdd, canRequestDeletion, canApprove }: Props) {
  const qc = useQueryClient();
  const { session } = useAuthStore();
  const [uploadOpen,   setUploadOpen]   = useState(false);
  const [deleteOpen,   setDeleteOpen]   = useState(false);
  const [activeItem,   setActiveItem]   = useState<EvidenceData | null>(null);
  const [file,         setFile]         = useState<File | null>(null);
  const [fileError,    setFileError]    = useState('');
  const [search,       setSearch]       = useState('');
  const [typeFilter,   setTypeFilter]   = useState<string>('all');
  const [selected,     setSelected]     = useState<Set<string>>(new Set());

  const { data: items = [], isLoading } = useQuery({
    queryKey: ['evidence', contractId],
    queryFn: () => evidenceApi.getContractEvidence(contractId),
  });

  const uploadMutation = useMutation({
    mutationFn: async () => {
      if (!file) throw new Error('No file selected');
      const base64 = await fileToBase64(file);
      const result = await evidenceApi.upload(contractId, '', file.type, file.size, session!.user_id, base64);
      await evidenceApi.proposeAddition(contractId, result.evidence_id, session!.user_id);
    },
    onSuccess: () => {
      toast.success('Evidence submitted. Awaiting party approval.');
      qc.invalidateQueries({ queryKey: ['evidence', contractId] });
      setUploadOpen(false);
      setFile(null);
    },
    onError: () => toast.error('Upload failed. Please try again.'),
  });

  const approveMutation = useMutation({
    mutationFn: (evidence_id: string) => evidenceApi.approve(evidence_id, session!.user_id),
    onSuccess: () => {
      toast.success('Evidence approved.');
      qc.invalidateQueries({ queryKey: ['evidence', contractId] });
    },
  });

  const deleteRequestMutation = useMutation({
    mutationFn: () => evidenceApi.requestDeletion(activeItem!.id, session!.user_id),
    onSuccess: () => {
      toast.success('Deletion request submitted. All parties must approve.');
      qc.invalidateQueries({ queryKey: ['evidence', contractId] });
      setDeleteOpen(false);
    },
  });

  const validateFile = (f: File): string => {
    if (!FILE_TYPES_ALLOWED.includes(f.type)) return 'Unsupported file type.';
    if (f.size > MAX_FILE_MB * 1024 * 1024) return `File exceeds ${MAX_FILE_MB} MB limit.`;
    return '';
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0] ?? null;
    if (!f) return;
    const err = validateFile(f);
    setFileError(err);
    if (!err) setFile(f);
  };

  if (isLoading) return <p className="text-sm text-secondary py-4">Loading evidence…</p>;

  const typeOptions = ['all', 'image', 'video', 'document', 'note'];
  const filteredItems = (items as EvidenceData[]).filter((item) => {
    const matchesSearch = !search || item.file_url.toLowerCase().includes(search.toLowerCase()) || item.added_by.toLowerCase().includes(search.toLowerCase());
    const matchesType = typeFilter === 'all' || (item.file_type ?? '').startsWith(typeFilter === 'image' ? 'image/' : typeFilter === 'video' ? 'video/' : typeFilter === 'document' ? 'application/' : 'text/');
    return matchesSearch && matchesType;
  });

  const toggleSelect = (id: string) => setSelected((s) => {
    const next = new Set(s);
    if (next.has(id)) next.delete(id); else next.add(id);
    return next;
  });

  const exportSelected = () => {
    const toExport = filteredItems.filter((e) => selected.has(e.id));
    const pkg = {
      exported_at: new Date().toISOString(),
      contract_id: contractId,
      item_count: toExport.length,
      items: toExport.map((e) => ({
        id: e.id, file_url: e.file_url, file_type: e.file_type,
        file_hash: e.file_hash, added_by: e.added_by, created_at: e.created_at,
        status: e.status,
      })),
    };
    const blob = new Blob([JSON.stringify(pkg, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `evidence-export-${contractId.slice(0, 8)}.json`;
    a.click();
  };

  return (
    <>
      <div className="card">
        <div className="card-header flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-primary">Evidence</h3>
            <p className="text-xs text-secondary mt-0.5">
              All evidence is timestamped and hashed. Additions require unanimous consent.
              Evidence can never be silently replaced.
            </p>
          </div>
          {canAdd && (
            <Button size="sm" variant="primary" onClick={() => setUploadOpen(true)}>
              + Submit Evidence
            </Button>
          )}
        </div>

        <div className="divide-y divide-border">
          {/* Search + filter bar */}
          <div className="px-5 py-3 flex flex-wrap gap-2 items-center bg-section">
            <input
              type="search"
              placeholder="Search evidence…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="form-input text-xs h-8 flex-1 min-w-32"
            />
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="form-input text-xs h-8 w-32"
            >
              {typeOptions.map((t) => <option key={t} value={t}>{t === 'all' ? 'All types' : t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
            </select>
            {selected.size > 0 && (
              <Button size="sm" variant="secondary" onClick={exportSelected}>
                Export {selected.size} selected
              </Button>
            )}
            {filteredItems.length > 0 && (
              <button
                className="text-xs text-accent hover:text-accent-hover"
                onClick={() => {
                  if (selected.size === filteredItems.length) setSelected(new Set());
                  else setSelected(new Set(filteredItems.map((e) => e.id)));
                }}
              >
                {selected.size === filteredItems.length ? 'Deselect all' : 'Select all'}
              </button>
            )}
          </div>

          {filteredItems.length === 0 && (
            <p className="px-5 py-4 text-sm text-secondary">{items.length === 0 ? 'No evidence on record.' : 'No evidence matches your search.'}</p>
          )}
          {filteredItems.map((item) => (
            <div key={item.id} className="px-5 py-4">
              <div className="flex items-start gap-4">
                <input
                  type="checkbox"
                  checked={selected.has(item.id)}
                  onChange={() => toggleSelect(item.id)}
                  className="mt-1 shrink-0 w-4 h-4 accent-accent"
                  aria-label={`Select evidence ${item.id}`}
                />
                <div className="w-8 h-8 rounded bg-section flex items-center justify-center shrink-0">
                  <svg className="w-4 h-4 text-meta" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2 mb-1">
                    <span className="text-sm font-medium text-primary truncate">{item.file_type}</span>
                    <StatusBadge status={item.status} />
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-0.5 text-xs text-secondary mb-2">
                    <span>Added by <span className="text-primary">{item.added_by}</span></span>
                    <span>{format(new Date(item.created_at), 'dd MMM yyyy, HH:mm')}</span>
                    <span>Size: {(item.file_size / 1024).toFixed(1)} KB</span>
                    <span>Type: {item.file_type}</span>
                  </div>

                  <HashDisplay label="File hash (SHA-256)" hash={item.file_hash} />

                  <div className="flex flex-wrap gap-2 mt-3">
                    {canApprove && item.status === 'pending_approval' && (
                      <Button
                        size="sm"
                        variant="primary"
                        loading={approveMutation.isPending}
                        onClick={() => approveMutation.mutate(item.id)}
                      >
                        Approve Addition
                      </Button>
                    )}
                    {canRequestDeletion && item.status === 'active' && (
                      <Button
                        size="sm"
                        variant="danger"
                        onClick={() => { setActiveItem(item); setDeleteOpen(true); }}
                      >
                        Request Deletion
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Upload Modal */}
      <Modal open={uploadOpen} onClose={() => setUploadOpen(false)} title="Submit Evidence" size="md">
        <div className="space-y-4">
          <div className="legal-notice text-xs">
            Once submitted, evidence cannot be silently replaced. Removal requires unanimous
            approval from all parties. This action is recorded in the immutable audit log.
          </div>

          <div>
            <label className="form-label">File (max {MAX_FILE_MB} MB)</label>
            <input
              type="file"
              accept={FILE_TYPES_ALLOWED.join(',')}
              onChange={handleFileChange}
              className="block w-full text-sm text-secondary file:mr-3 file:py-1.5 file:px-3 file:rounded file:border file:border-border file:text-sm file:bg-card file:text-primary hover:file:bg-section"
            />
            <p className="text-xs text-meta mt-1">PDF, JPEG, PNG, MP4 or TXT</p>
            {fileError && <p className="form-error">{fileError}</p>}
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => setUploadOpen(false)}>Cancel</Button>
            <Button
              variant="primary"
              disabled={!file || !!fileError}
              loading={uploadMutation.isPending}
              onClick={() => uploadMutation.mutate()}
            >
              Submit for Approval
            </Button>
          </div>
        </div>
      </Modal>

      {/* Delete Request Modal */}
      <Modal open={deleteOpen} onClose={() => setDeleteOpen(false)} title="Request Evidence Deletion">
        <div className="space-y-4">
          <div className="legal-notice text-xs">
            Deletion requires unanimous consent from all parties. This request and the final
            decision are permanently recorded in the audit log.
          </div>
          <p className="text-sm text-secondary">
            Submit a deletion request for this evidence item? All parties must approve before
            the item is removed.
          </p>
          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => setDeleteOpen(false)}>Cancel</Button>
            <Button
              variant="danger"
              loading={deleteRequestMutation.isPending}
              onClick={() => deleteRequestMutation.mutate()}
            >
              Submit Deletion Request
            </Button>
          </div>
        </div>
      </Modal>

      {/* Floating "Add Evidence" button — mobile only */}
      {canAdd && (
        <button
          className="fixed bottom-6 right-6 z-40 md:hidden w-14 h-14 rounded-full bg-accent text-white shadow-lg flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2"
          aria-label="Submit Evidence"
          onClick={() => setUploadOpen(true)}
        >
          <svg aria-hidden="true" className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
        </button>
      )}
    </>
  );
}
