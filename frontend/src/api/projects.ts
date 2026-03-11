import { rpcPost, rpcGet } from './client';

export interface ProjectData {
  id: string;
  name: string;
  main_party_id: string;
  created_at: string;
}

export interface MemberData {
  id: string;
  user_id: string;
  project_id: string;
  role_id: string;
}

export const projectsApi = {
  /** POST /project/create args=[name, main_party_id] */
  create: (name: string, user_id: string) =>
    rpcPost<{ status: string; project_id: string }>('/project/create', [name, user_id]),

  /** GET /project/get_user_projects ?user_id=... */
  getUserProjects: (user_id: string) =>
    rpcGet<ProjectData[]>('/project/get_user_projects', { user_id }),

  /** GET /project/get_contracts ?project_id=... */
  getProjectContracts: (project_id: string) =>
    rpcGet<{ id: string; project_id: string; created_by: string; created_at: string; current_version: string | null }[]>(
      '/project/get_contracts', { project_id }
    ),

  /** POST /project/invite_user args=[project_id, user_id, role] */
  inviteUser: (project_id: string, user_id: string, role: string) =>
    rpcPost('/project/invite_user', [project_id, user_id, role]),

  /** POST /project/approve_membership args=[request_id] */
  approveMembership: (request_id: string) =>
    rpcPost('/project/approve_membership', [request_id]),

  /** POST /project/reject_membership args=[request_id] */
  rejectMembership: (request_id: string) =>
    rpcPost('/project/reject_membership', [request_id]),

  /** POST /project/leave args=[user_id, project_id] */
  leave: (user_id: string, project_id: string) =>
    rpcPost('/project/leave', [user_id, project_id]),

  /** POST /project/change_user_role args=[project_id, user_id, new_role] */
  changeUserRole: (project_id: string, user_id: string, new_role: string) =>
    rpcPost('/project/change_user_role', [project_id, user_id, new_role]),

  /** GET /project/get_members ?project_id=... */
  getMembers: (project_id: string) =>
    rpcGet<MemberData[]>('/project/get_members', { project_id }),

  /** GET /project/get_user_role ?user_id=...&project_id=... */
  getUserRole: (user_id: string, project_id: string) =>
    rpcGet<string | null>('/project/get_user_role', { user_id, project_id }),
};
