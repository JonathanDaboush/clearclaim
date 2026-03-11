import { format } from 'date-fns';
import { useQuery } from '@tanstack/react-query';
import { signingApi } from '@/api/signing';
import type { SignatureData } from '@/api/signing';
import { HashDisplay } from '@/components/common/HashDisplay';
import { RecordPanel } from '@/components/common/RecordPanel';

interface Props {
  versionId: string;
}

/** Displays each signer's recorded signature with all legally relevant metadata. */
export function SignaturePanel({ versionId }: Props) {
  const { data: signatures = [], isLoading } = useQuery({
    queryKey: ['signatures', versionId],
    queryFn: () => signingApi.getSignatures(versionId),
    enabled: !!versionId,
  });

  const { data: fullySigned } = useQuery({
    queryKey: ['fully-signed', versionId],
    queryFn: () => signingApi.checkFullySigned(versionId),
    enabled: !!versionId,
  });

  if (isLoading) return <p className="text-sm text-secondary py-4">Loading signaturesâ€¦</p>;

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-primary">Signatures</h3>
          {fullySigned !== undefined && (
            <span className={fullySigned ? 'badge-confirmed' : 'badge-pending'}>
              {fullySigned ? 'Fully Signed' : 'Awaiting Signatures'}
            </span>
          )}
        </div>
      </div>

      <div className="divide-y divide-border">
        {signatures.length === 0 && (
          <p className="px-5 py-4 text-sm text-secondary">No signatures recorded yet.</p>
        )}
        {(signatures as SignatureData[]).map((sig) => (
          <div key={sig.id} className="px-5 py-4">
            <RecordPanel
              title={`Signer: ${sig.user_id}`}
              variant="success"
              icon={
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              }
              fields={[
                { label: 'User ID',         value: sig.user_id,               mono: true },
                { label: 'Timestamp',       value: format(new Date(sig.signed_at), 'dd MMM yyyy, HH:mm:ss z') },
                { label: 'Device ID',       value: sig.device_id,             mono: true },
                { label: 'Signature Hash',  value: sig.signature_hash,        mono: true },
              ]}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
