/**
 * EvidenceViewer
 * ─────────────────────────────────────────────────────────────────────────────
 * Renders a single piece of evidence with its metadata, integrity hash,
 * uploader identity, and status. Provides inline preview for images and PDFs.
 */
import { format } from 'date-fns';
import type { EvidenceData } from '@/api/evidence';
import { HashDisplay } from '@/components/common/HashDisplay';
import { StatusBadge } from '@/components/common/StatusBadge';

const IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

interface Props {
  item: EvidenceData & {
    timestamp_proof?: string;
    uploader_hash?: string;
    metadata?: string;
  };
}

export function EvidenceViewer({ item }: Props) {
  const isImage = IMAGE_TYPES.includes(item.file_type);
  const isPdf   = item.file_type === 'application/pdf';

  return (
    <div className="card">
      <div className="card-body space-y-4">
        {/* File preview */}
        {isImage && item.file_url && (
          <div className="rounded-lg overflow-hidden border border-border max-h-80">
            <img
              src={item.file_url}
              alt="Evidence preview"
              className="w-full h-full object-contain"
            />
          </div>
        )}

        {isPdf && item.file_url && (
          <div className="rounded-lg border border-border overflow-hidden" style={{ height: '20rem' }}>
            <iframe
              src={item.file_url}
              title="Evidence PDF"
              className="w-full h-full"
            />
          </div>
        )}

        {/* Metadata table */}
        <dl className="grid grid-cols-[auto_1fr] gap-x-6 gap-y-2 text-sm">
          <dt className="text-meta">File</dt>
          <dd className="text-primary font-medium truncate">{item.file_url.split('/').pop() ?? item.file_url}</dd>

          <dt className="text-meta">Type</dt>
          <dd className="text-primary">{item.file_type}</dd>

          <dt className="text-meta">Size</dt>
          <dd className="text-primary">{(item.file_size / 1024).toFixed(1)} KB</dd>

          <dt className="text-meta">Uploaded by</dt>
          <dd className="text-primary">{item.added_by}</dd>

          <dt className="text-meta">Uploaded at</dt>
          <dd className="text-primary">
            {item.timestamp_proof
              ? format(new Date(item.timestamp_proof), 'PPpp')
              : format(new Date(item.created_at), 'PPpp')}
          </dd>

          <dt className="text-meta">Status</dt>
          <dd><StatusBadge status={item.status} /></dd>
        </dl>

        {/* Integrity hashes */}
        <div className="space-y-2 pt-2 border-t border-border">
          <p className="text-xs font-semibold text-meta uppercase tracking-wide">Integrity</p>
          <div>
            <p className="text-xs text-meta mb-0.5">File SHA-256</p>
            <HashDisplay hash={item.file_hash} />
          </div>
          {item.uploader_hash && (
            <div>
              <p className="text-xs text-meta mb-0.5">
                Uploader anchor{' '}
                <span className="font-normal">(SHA-256 of uploader + file hash + timestamp)</span>
              </p>
              <HashDisplay hash={item.uploader_hash} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
