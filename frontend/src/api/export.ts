import { rpcGet, rpcPost, BASE_URL } from './client';

export const exportApi = {
  /** GET /export/contract_history ?contract_id=... */
  contractHistory: (contract_id: string) =>
    rpcGet('/export/contract_history', { contract_id }),

  /** GET /export/contract_versions ?contract_id=... */
  contractVersions: (contract_id: string) =>
    rpcGet('/export/contract_versions', { contract_id }),

  /** GET /export/contract_signatures ?contract_id=... */
  contractSignatures: (contract_id: string) =>
    rpcGet('/export/contract_signatures', { contract_id }),

  /** GET /export/contract_evidence ?contract_id=... */
  contractEvidence: (contract_id: string) =>
    rpcGet('/export/contract_evidence', { contract_id }),

  /** GET /export/audit_logs ?contract_id=... */
  auditLogs: (contract_id: string) =>
    rpcGet('/export/audit_logs', { contract_id }),

  /** POST /export/case_archive args=[contract_id] */
  caseArchive: (contract_id: string) =>
    rpcPost('/export/case_archive', [contract_id]),

  /**
   * GET /export/case_archive_zip — returns a binary ZIP bundle.
   * The caller is responsible for triggering a browser download.
   */
  caseArchiveZipUrl: (contract_id: string): string =>
    `${BASE_URL}/export/case_archive_zip?contract_id=${encodeURIComponent(contract_id)}`,

  caseArchiveZipBlob: async (contract_id: string): Promise<Blob> => {
    const session = JSON.parse(localStorage.getItem('cc_session') ?? 'null');
    const headers: Record<string, string> = {};
    if (session?.access_token) headers['Authorization'] = `Bearer ${session.access_token}`;
    const res = await fetch(
      `${BASE_URL}/export/case_archive_zip?contract_id=${encodeURIComponent(contract_id)}`,
      { headers },
    );
    if (!res.ok) throw new Error(`Export failed: ${res.status}`);
    return res.blob();
  },

  /** GET /export/timeline_pdf?contract_id=... — returns a binary PDF */
  timelinePdfBlob: async (contract_id: string): Promise<Blob> => {
    const session = JSON.parse(localStorage.getItem('cc_session') ?? 'null');
    const headers: Record<string, string> = {};
    if (session?.access_token) headers['Authorization'] = `Bearer ${session.access_token}`;
    const res = await fetch(
      `${BASE_URL}/export/timeline_pdf?contract_id=${encodeURIComponent(contract_id)}`,
      { headers },
    );
    if (!res.ok) throw new Error(`Timeline PDF export failed: ${res.status}`);
    return res.blob();
  },

  /** GET /export/signing_certificate_pdf?signature_id=... — returns a binary PDF */
  signingCertPdfBlob: async (signature_id: string): Promise<Blob> => {
    const session = JSON.parse(localStorage.getItem('cc_session') ?? 'null');
    const headers: Record<string, string> = {};
    if (session?.access_token) headers['Authorization'] = `Bearer ${session.access_token}`;
    const res = await fetch(
      `${BASE_URL}/export/signing_certificate_pdf?signature_id=${encodeURIComponent(signature_id)}`,
      { headers },
    );
    if (!res.ok) throw new Error(`Signing certificate PDF export failed: ${res.status}`);
    return res.blob();
  },
};
