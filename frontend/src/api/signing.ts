import { rpcPost, rpcGet } from './client';

export interface SignatureData {
  id: string;
  contract_version_id: string;
  user_id: string;
  device_id: string;
  signed_at: string;
  signature_hash: string;
}

export const signingApi = {
  /**
   * Step 1: POST /signing/request args=[contract_version_id, user_id]
   * Indicates intent to sign. Returns a request record.
   */
  request: (contract_version_id: string, user_id: string) =>
    rpcPost<{ status: string }>('/signing/request', [contract_version_id, user_id]),

  /**
   * Step 2: POST /signing/verify_totp args=[totp_secret, code]
   * Verify the TOTP code before signing. Returns bool.
   */
  verifyTotp: (totp_secret: string, code: string) =>
    rpcPost<boolean>('/signing/verify_totp', [totp_secret, code]),

  /**
   * Step 3: POST /signing/sign args=[contract_version_id, user_id, device_id, ip, totp_secret, totp_code, idempotency_key]
   * Cryptographically sign the contract version. Backend enforces TOTP and idempotency.
   * ip is injected by the server; pass '' from the client.
   */
  sign: (
    contract_version_id: string,
    user_id: string,
    device_id: string,
    totp_secret: string = '',
    totp_code: string = '',
    idempotency_key: string = '',
  ) =>
    rpcPost<{ status: string; signature_id: string; ip?: string; signed_at?: string; contract_snapshot_hash?: string; totp_verified?: boolean }>(
      '/signing/sign',
      [contract_version_id, user_id, device_id, '', totp_secret, totp_code, idempotency_key],
    ),

  /** GET /signing/get_signatures ?contract_version_id=... */
  getSignatures: (contract_version_id: string) =>
    rpcGet<SignatureData[]>('/signing/get_signatures', { contract_version_id }),

  /** GET /signing/check_fully_signed ?contract_version_id=... */
  checkFullySigned: (contract_version_id: string) =>
    rpcGet<boolean>('/signing/check_fully_signed', { contract_version_id }),
};
