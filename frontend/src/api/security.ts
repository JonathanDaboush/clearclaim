import { rpcPost, rpcGet } from './client';

export const securityApi = {
  /** GET /security/is_restricted ?user_id=... */
  isRestricted: (user_id: string) =>
    rpcGet<{ restricted: boolean }>('/security/is_restricted', { user_id }),

  /** POST /security/restrict_actions args=[user_id, event_type] */
  restrictActions: (user_id: string, event_type: string) =>
    rpcPost<{ status: string }>('/security/restrict_actions', [user_id, event_type]),

  /** POST /security/lift_restriction args=[user_id] */
  liftRestriction: (user_id: string) =>
    rpcPost<{ status: string }>('/security/lift_restriction', [user_id]),
};
