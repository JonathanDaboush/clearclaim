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

  /** POST /audit/snapshot args=[] */
  generateSnapshot: () =>
    rpcPost<string>('/audit/snapshot', []),
};
