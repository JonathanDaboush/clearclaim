// ─── Core domain types mirroring the backend models ─────────────────────────

export type Role = 'worker_manager' | 'worker' | 'legal_rep' | 'client' | 'guest';

export type ContractState =
  | 'draft'
  | 'under_review'
  | 'approved'
  | 'active'
  | 'disputed'
  | 'terminated';

export type VerificationStatus = 'unverified' | 'pending' | 'verified' | 'failed';

// ─── User & Auth ─────────────────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  totp_enabled: boolean;
  verification_status: VerificationStatus;
  verification_provider?: string;
  verification_timestamp?: string;
  created_at: string;
}

export interface Device {
  id: string;
  user_id: string;
  device_name: string;
  device_fingerprint: string;
  trusted: boolean;
  registered_at: string;
  last_seen?: string;
}

export interface AuthSession {
  access_token: string;
  token_type: string;
  user: User;
}

// ─── Project & Membership ────────────────────────────────────────────────────

export interface Project {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  main_party_user_id: string;
}

export interface Subgroup {
  id: string;
  project_id: string;
  name: string;
  created_at: string;
}

export interface Membership {
  user_id: string;
  project_id: string;
  subgroup_id?: string;
  role: Role;
  joined_at: string;
  is_active: boolean;
}

// ─── Contract & Versioning ───────────────────────────────────────────────────

export interface Contract {
  id: string;
  project_id: string;
  title: string;
  state: ContractState;
  created_by: string;
  created_at: string;
  current_version_id?: string;
}

export interface ContractVersion {
  id: string;
  contract_id: string;
  version_number: number;
  content: string;
  content_hash: string;
  created_by: string;
  created_at: string;
  is_active: boolean;
  approval_status: 'pending' | 'approved' | 'rejected';
}

export interface RevisionChange {
  id: string;
  contract_version_id: string;
  line_number: number;
  change_type: 'added' | 'removed' | 'modified';
  old_content?: string;
  new_content: string;
}

export interface ContractRevisionApproval {
  id: string;
  contract_version_id: string;
  user_id: string;
  approved: boolean;
  approved_at: string;
}

export interface DiffResult {
  old_version: number;
  new_version: number;
  changes: RevisionChange[];
  old_content: string;
  new_content: string;
}

// ─── Signatures ──────────────────────────────────────────────────────────────

export interface Signature {
  id: string;
  contract_id: string;
  contract_version_id: string;
  contract_version_number: number;
  user_id: string;
  user_email: string;
  timestamp: string;
  device_id: string;
  device_name: string;
  ip_address: string;
  content_hash: string;
  signature_hash: string;
}

export interface SigningReceipt {
  signature: Signature;
  document_hash: string;
  signing_timestamp: string;
  confirmation_id: string;
}

// ─── Evidence ────────────────────────────────────────────────────────────────

export type EvidenceStatus = 'pending_approval' | 'active' | 'deletion_requested' | 'deleted';

export interface Evidence {
  id: string;
  contract_id: string;
  project_id: string;
  filename: string;
  file_type: string;
  file_size: number;
  file_hash: string;
  uploaded_by: string;
  uploaded_by_email: string;
  uploaded_at: string;
  status: EvidenceStatus;
  description?: string;
  is_disputed: boolean;
  dispute_note?: string;
}

export interface EvidenceApproval {
  id: string;
  evidence_id: string;
  user_id: string;
  action: 'addition' | 'deletion';
  approved: boolean;
  approved_at: string;
}

// ─── Audit ───────────────────────────────────────────────────────────────────

export interface AuditEntry {
  id: string;
  event_type: string;
  user_id?: string;
  user_email?: string;
  contract_id?: string;
  project_id?: string;
  evidence_id?: string;
  timestamp: string;
  ip_address?: string;
  device_id?: string;
  device_name?: string;
  details: Record<string, unknown>;
  entry_hash: string;
  previous_hash?: string;
}

// ─── Notifications ───────────────────────────────────────────────────────────

export interface Notification {
  id: string;
  user_id: string;
  title: string;
  message: string;
  event_type: string;
  related_contract_id?: string;
  related_project_id?: string;
  is_read: boolean;
  created_at: string;
}

// ─── Billing ─────────────────────────────────────────────────────────────────

export interface Subscription {
  id: string;
  user_id: string;
  plan_name: string;
  status: 'active' | 'cancelled' | 'past_due';
  current_period_start: string;
  current_period_end: string;
}

export interface Payment {
  id: string;
  user_id: string;
  amount_cents: number;
  currency: string;
  status: 'paid' | 'pending' | 'failed';
  created_at: string;
  description: string;
}

// ─── Export ───────────────────────────────────────────────────────────────────

export interface ContractExport {
  contract: Contract;
  versions: ContractVersion[];
  signatures: Signature[];
  evidence: Evidence[];
  audit_entries: AuditEntry[];
  exported_at: string;
}

// ─── API responses ───────────────────────────────────────────────────────────

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

// ─── UI state helpers ────────────────────────────────────────────────────────

export type SigningStep = 'review' | 'confirm_intent' | 'totp' | 'receipt';
