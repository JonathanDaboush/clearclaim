/**
 * EvidenceUploader
 * ─────────────────────────────────────────────────────────────────────────────
 * Standalone file-upload component for adding evidence to a contract.
 * Validates file type and size, computes a local SHA-256 preview hash,
 * then calls evidenceApi.upload() and notifies the parent on success.
 */
import { useRef, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { evidenceApi } from '@/api/evidence';
import { useAuthStore } from '@/stores/authStore';
import { Button } from '@/components/common/Button';

const ALLOWED_TYPES = [
  'application/pdf',
  'image/jpeg',
  'image/png',
  'image/webp',
  'video/mp4',
  'text/plain',
];
const MAX_BYTES = 10 * 1024 * 1024; // 10 MB

async function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve((reader.result as string).split(',')[1] ?? '');
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

async function localSha256(file: File): Promise<string> {
  const buf = await file.arrayBuffer();
  const hash = await crypto.subtle.digest('SHA-256', buf);
  return Array.from(new Uint8Array(hash)).map((b) => b.toString(16).padStart(2, '0')).join('');
}

interface Props {
  contractId: string;
  onUploaded?: (evidenceId: string) => void;
}

export function EvidenceUploader({ contractId, onUploaded }: Props) {
  const { session } = useAuthStore();
  const inputRef = useRef<HTMLInputElement>(null);
  const [file,      setFile]      = useState<File | null>(null);
  const [fileError, setFileError] = useState('');
  const [localHash, setLocalHash] = useState('');

  const uploadMutation = useMutation({
    mutationFn: async () => {
      if (!file) throw new Error('No file selected');
      const data = await fileToBase64(file);
      return evidenceApi.upload(
        contractId,
        file.name,      // file_url — use filename as URL reference
        file.type,      // file_type
        file.size,      // file_size
        session!.user_id,
        data,           // file_bytes (base64)
      );
    },
    onSuccess: (res: { evidence_id?: string }) => {
      setFile(null);
      setLocalHash('');
      if (onUploaded && res.evidence_id) onUploaded(res.evidence_id);
    },
  });

  const pick = async (f: File) => {
    setFileError('');
    if (!ALLOWED_TYPES.includes(f.type)) {
      setFileError(`File type not allowed. Accepted: PDF, JPEG, PNG, WEBP, MP4, TXT.`);
      return;
    }
    if (f.size > MAX_BYTES) {
      setFileError(`File exceeds maximum size of 10 MB.`);
      return;
    }
    setFile(f);
    setLocalHash(await localSha256(f));
  };

  return (
    <div className="space-y-3">
      <div
        className="border-2 border-dashed border-border rounded-lg px-6 py-8 text-center cursor-pointer hover:border-accent transition-colors"
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          const f = e.dataTransfer.files[0];
          if (f) pick(f);
        }}
      >
        <p className="text-sm text-secondary">
          {file ? file.name : 'Click or drag a file here to upload'}
        </p>
        <p className="text-xs text-meta mt-1">PDF, JPEG, PNG, WEBP, MP4, TXT — max 10 MB</p>
        <input
          ref={inputRef}
          type="file"
          accept={ALLOWED_TYPES.join(',')}
          className="hidden"
          onChange={(e) => { const f = e.target.files?.[0]; if (f) pick(f); }}
        />
      </div>

      {fileError && <p className="form-error">{fileError}</p>}

      {localHash && (
        <p className="text-xs text-meta font-mono break-all">
          Local SHA-256: <span className="text-primary">{localHash}</span>
        </p>
      )}

      {uploadMutation.isError && (
        <p className="form-error">Upload failed. Please try again.</p>
      )}

      <Button
        variant="primary"
        disabled={!file || !!fileError}
        loading={uploadMutation.isPending}
        onClick={() => uploadMutation.mutate()}
        className="w-full justify-center"
      >
        Upload Evidence
      </Button>
    </div>
  );
}
