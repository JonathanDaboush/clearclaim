import { rpcPost, rpcGet } from './client';

export interface LoginResult {
  status: string;
  user_id?: string;
  email?: string;
  totp_secret?: string;
  verification_status?: string;
  message?: string;
}

export interface SignupResult {
  status: string;
  user_id?: string;
  totp_secret?: string;
  message?: string;
}

export const authApi = {
  /** POST /user/signup args=[email, password] */
  signup: (email: string, password: string) =>
    rpcPost<SignupResult>('/user/signup', [email, password]),

  /** POST /user/login args=[email, password] */
  login: (email: string, password: string) =>
    rpcPost<LoginResult>('/user/login', [email, password]),

  /** POST /user/verify_totp args=[user_id, totp_secret, code] */
  verifyTotp: (user_id: string, totp_secret: string, code: string) =>
    rpcPost<boolean>('/user/verify_totp', [user_id, totp_secret, code]),

  /** POST /user/initiate_password_reset args=[email] */
  initiatePasswordReset: (email: string) =>
    rpcPost('/user/initiate_password_reset', [email]),

  /** POST /user/complete_password_reset args=[token, new_password] */
  completePasswordReset: (token: string, new_password: string) =>
    rpcPost('/user/complete_password_reset', [token, new_password]),

  /** GET /user/get_me ?user_id=... */
  getMe: (user_id: string) =>
    rpcGet<{ id: string; email: string; role_id: string | null; verification_status: string }>(
      '/user/get_me', { user_id }
    ),

  /** GET /user/get_devices ?user_id=... */
  getDevices: (user_id: string) =>
    rpcGet<{ id: string; device_info: string; trusted: boolean }[]>('/user/get_devices', { user_id }),

  /** POST /user/add_device args=[user_id, device_info] */
  addDevice: (user_id: string, device_info: string) =>
    rpcPost<{ status: string; device_id: string }>('/user/add_device', [user_id, device_info]),

  /** POST /user/verify_new_device args=[user_id, device_id] */
  verifyNewDevice: (user_id: string, device_id: string) =>
    rpcPost('/user/verify_new_device', [user_id, device_id]),

  /** POST /user/revoke_device args=[user_id, device_id] */
  revokeDevice: (user_id: string, device_id: string) =>
    rpcPost('/user/revoke_device', [user_id, device_id]),

  /** POST /user/remove_account args=[user_id] */
  removeAccount: (user_id: string) =>
    rpcPost('/user/remove_account', [user_id]),

  /** POST /user/start_identity_verification args=[user_id] */
  startIdentityVerification: (user_id: string) =>
    rpcPost('/user/start_identity_verification', [user_id]),

  /** GET /user/check_identity_verification_status ?user_id=... */
  checkIdentityVerificationStatus: (user_id: string) =>
    rpcGet<{ status: string }>('/user/check_identity_verification_status', { user_id }),
};
