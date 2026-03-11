import { rpcPost, rpcGet } from './client';

export interface ContractData {
  id: string;
  project_id: string;
  created_by: string;
  created_at: string;
  current_version: string | null;
  status?: string;
  last_revised_at?: string;
}

export interface ContractVersionData {
  id: string;
  contract_id: string;
  content: string;
  created_by: string;
  created_at: string;
  version_number?: number;
  content_hash?: string;
  signed?: boolean;
  rejected?: boolean;
}

export const contractsApi = {
  /** POST /contract/create args=[project_id, created_by, content] */
  create: (project_id: string, created_by: string, content: string) =>
    rpcPost<{ status: string; contract_id: string; version_id: string }>(
      '/contract/create', [project_id, created_by, content]
    ),

  /** GET /contract/get ?contract_id=... */
  get: (contract_id: string) =>
    rpcGet<ContractData>('/contract/get', { contract_id }),

  /** POST /contract/revise args=[contract_id, new_content, user_id] */
  revise: (contract_id: string, new_content: string, user_id: string) =>
    rpcPost<{ status: string; version_id: string }>(
      '/contract/revise', [contract_id, new_content, user_id]
    ),

  /** GET /contract/get_versions ?contract_id=... */
  getVersions: (contract_id: string) =>
    rpcGet<ContractVersionData[]>('/contract/get_versions', { contract_id }),

  /** POST /contract/generate_diff args=[old_content, new_content] */
  generateDiff: (old_content: string, new_content: string) =>
    rpcPost<string>('/contract/generate_diff', [old_content, new_content]),

  /** POST /contract/approve_revision args=[contract_version_id, user_id] */
  approveRevision: (contract_version_id: string, user_id: string) =>
    rpcPost('/contract/approve_revision', [contract_version_id, user_id]),

  /** POST /contract/reject_revision args=[contract_version_id, user_id] */
  rejectRevision: (contract_version_id: string, user_id: string) =>
    rpcPost('/contract/reject_revision', [contract_version_id, user_id]),

  /** POST /contract/activate_version args=[contract_id, contract_version_id] */
  activateVersion: (contract_id: string, contract_version_id: string) =>
    rpcPost('/contract/activate_version', [contract_id, contract_version_id]),

  /** GET /contract/get_state ?contract_id=... */
  getState: (contract_id: string) =>
    rpcGet<string>('/contract/get_state', { contract_id }),

  /** POST /contract/transition_state args=[contract_id, new_state] */
  transitionState: (contract_id: string, new_state: string) =>
    rpcPost('/contract/transition_state', [contract_id, new_state]),
};
