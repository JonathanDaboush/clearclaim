/**
 * ExportButton
 * ─────────────────────────────────────────────────────────────────────────────
 * Standalone button that builds and downloads a case archive ZIP for the
 * given contract. The archive contains: contract JSON, signatures, audit chain,
 * evidence files, timeline, and a SHA-256 hash manifest.
 */
import { useMutation } from '@tanstack/react-query';
import { exportApi } from '@/api/export';
import { Button } from '@/components/common/Button';

interface Props {
  contractId: string;
  label?: string;
  className?: string;
}

export function ExportButton({ contractId, label = 'Export Record', className }: Props) {
  const exportMutation = useMutation({
    mutationFn: () => exportApi.caseArchiveZipBlob(contractId),
    onSuccess: (blob) => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `clearclaim-export-${contractId}.zip`;
      a.click();
      URL.revokeObjectURL(url);
    },
  });

  return (
    <Button
      variant="secondary"
      loading={exportMutation.isPending}
      onClick={() => exportMutation.mutate()}
      className={className}
      title="Download a ZIP archive containing the full signed contract record, audit chain, evidence, and hash manifest."
    >
      {exportMutation.isError ? 'Export failed — retry' : label}
    </Button>
  );
}
