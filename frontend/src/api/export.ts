import { rpcGet, rpcPost } from './client';

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
};
