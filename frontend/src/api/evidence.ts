import { rpcPost, rpcGet } from './client';

export interface EvidenceData {
  id: string;
  contract_id: string;
  file_url: string;
  file_type: string;
  file_size: number;
  file_hash: string;
  added_by: string;
  status: string;
  created_at: string;
}

export const evidenceApi = {
  /**
   * POST /evidence/upload args=[contract_id, file_bytes, file_url, file_type, file_size, added_by]
   * file_bytes: pass empty string "" if URL-referenced; base64 string for inline upload.
   */
  upload: (contract_id: string, file_url: string, file_type: string, file_size: number, added_by: string, file_bytes: string = "") =>
    rpcPost<{ status: string; evidence_id: string }>('/evidence/upload', [contract_id, file_bytes, file_url, file_type, file_size, added_by]),

  /** POST /evidence/propose_addition args=[contract_id, evidence_id, user_id] */
  proposeAddition: (contract_id: string, evidence_id: string, user_id: string) =>
    rpcPost('/evidence/propose_addition', [contract_id, evidence_id, user_id]),

  /** POST /evidence/approve args=[evidence_id, user_id] */
  approve: (evidence_id: string, user_id: string) =>
    rpcPost('/evidence/approve', [evidence_id, user_id]),

  /** POST /evidence/request_deletion args=[evidence_id, user_id] */
  requestDeletion: (evidence_id: string, user_id: string) =>
    rpcPost('/evidence/request_deletion', [evidence_id, user_id]),

  /** POST /evidence/approve_deletion args=[evidence_id, user_id] */
  approveDeletion: (evidence_id: string, user_id: string) =>
    rpcPost('/evidence/approve_deletion', [evidence_id, user_id]),

  /** GET /evidence/get_contract_evidence ?contract_id=... */
  getContractEvidence: (contract_id: string) =>
    rpcGet<EvidenceData[]>('/evidence/get_contract_evidence', { contract_id }),

  /** GET /evidence/get_user_evidence ?user_id=... */
  getAll: (user_id: string) =>
    rpcGet<EvidenceData[]>('/evidence/get_user_evidence', { user_id }),
};
