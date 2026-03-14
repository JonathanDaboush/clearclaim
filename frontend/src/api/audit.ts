import { rpcPost, rpcGet } from './client';

export interface AuditEntryData {
  id: string;
  user_id: string;
  device_id: string;
  event_type: string;
  related_object_id: string;
  details: string;
  timestamp: string;
  hash: string;
}

export interface AuditVerifyResult {
  is_valid: boolean;
  invalid_entry_ids: string[];
  total: number;
}

export const auditApi = {
  /** GET /audit/get_entries ?related_object_id=...&limit=... */
  getEntries: (related_object_id?: string, limit = 50) =>
    rpcGet<AuditEntryData[]>('/audit/get_entries', {
      ...(related_object_id ? { related_object_id } : {}),
      limit: String(limit),
    }),

  /** POST /audit/verify_chain args=[] */
  verifyChain: () =>
    rpcPost<boolean>('/audit/verify_chain', []),

  /** POST /audit/verify_entries — per-entry integrity status */
  verifyEntries: () =>
    rpcPost<AuditVerifyResult>('/audit/verify_entries', []),

  /** POST /audit/snapshot args=[] */
  generateSnapshot: () =>
    rpcPost<string>('/audit/snapshot', []),
};
