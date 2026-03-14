/**
 * SecuritySettingsPage
 * ─────────────────────────────────────────────────────────────────────────────
 * Authentication system security settings: identity verification status,
 * trusted device list, and account security actions.
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { authApi } from '@/api/auth';
import { useAuthStore } from '@/stores/authStore';
import { Button } from '@/components/common/Button';
import { StatusBadge } from '@/components/common/StatusBadge';
import { toast } from 'react-toastify';
import { format } from 'date-fns';

export default function SecuritySettingsPage() {
  const { session } = useAuthStore();
  const qc = useQueryClient();
  const userId = session?.user_id ?? '';

  const { data: idStatus, isLoading: idLoading } = useQuery({
    queryKey: ['id-verification', userId],
    queryFn:  () => authApi.checkIdentityVerificationStatus(userId),
    enabled:  !!userId,
  });

  const { data: devices = [], isLoading: devLoading } = useQuery({
    queryKey: ['devices', userId],
    queryFn:  () => authApi.getDevices(userId),
    enabled:  !!userId,
  });

  const startVerifyMutation = useMutation({
    mutationFn: () => authApi.startIdentityVerification(userId),
    onSuccess: () => {
      toast.success('Identity verification started. Complete the steps provided.');
      qc.invalidateQueries({ queryKey: ['id-verification', userId] });
    },
    onError: () => toast.error('Could not start identity verification.'),
  });

  const revokeMutation = useMutation({
    mutationFn: (deviceId: string) => authApi.revokeDevice(userId, deviceId),
    onSuccess: () => {
      toast.success('Device revoked.');
      qc.invalidateQueries({ queryKey: ['devices', userId] });
    },
    onError: () => toast.error('Could not revoke device.'),
  });

  return (
    <div className="space-y-8 max-w-2xl mx-auto">
      <div>
        <h1 className="text-xl font-semibold text-primary">Security Settings</h1>
        <p className="text-sm text-secondary mt-1">Manage identity verification and trusted devices.</p>
      </div>

      {/* Identity verification */}
      <section className="card">
        <div className="card-body space-y-4">
          <h2 className="text-base font-semibold text-primary">Identity Verification</h2>
          <p className="text-sm text-secondary">
            Identity verification is required before you can sign contracts. Your verification
            status is displayed on all signed documents.
          </p>

          {idLoading ? (
            <p className="text-sm text-meta">Loading&hellip;</p>
          ) : (
            <div className="flex items-center gap-3">
              <StatusBadge status={idStatus?.status ?? 'unverified'} />
              {idStatus?.status !== 'verified' && (
                <Button
                  variant="primary"
                  loading={startVerifyMutation.isPending}
                  onClick={() => startVerifyMutation.mutate()}
                >
                  Start Verification
                </Button>
              )}
            </div>
          )}
        </div>
      </section>

      {/* Trusted devices */}
      <section className="card">
        <div className="card-body space-y-4">
          <h2 className="text-base font-semibold text-primary">Trusted Devices</h2>
          <p className="text-sm text-secondary">
            Each device used to sign is recorded. Revoke devices you no longer recognise.
          </p>

          {devLoading ? (
            <p className="text-sm text-meta">Loading&hellip;</p>
          ) : devices.length === 0 ? (
            <p className="text-sm text-meta">No trusted devices registered yet.</p>
          ) : (
            <ul className="divide-y divide-border">
              {(devices as { id: string; device_info: string; location?: string; trusted: boolean; added_at?: string }[]).map((d) => (
                <li key={d.id} className="py-3 flex items-center justify-between gap-4">
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-primary truncate">{d.device_info || 'Unknown device'}</p>
                    <p className="text-xs text-meta">
                      {d.location ? `${d.location} · ` : ''}
                      {d.added_at ? format(new Date(d.added_at), 'PPp') : ''}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <StatusBadge status={d.trusted ? 'trusted' : 'pending'} />
                    <Button
                      variant="secondary"
                      onClick={() => revokeMutation.mutate(d.id)}
                      loading={revokeMutation.isPending}
                    >
                      Revoke
                    </Button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>

      {/* Two-factor authentication */}
      <section className="card">
        <div className="card-body space-y-3">
          <h2 className="text-base font-semibold text-primary">Two-Factor Authentication</h2>
          <p className="text-sm text-secondary">
            TOTP-based two-factor authentication is <strong>mandatory</strong> on this platform.
            It is required for every login and every contract signing action and cannot be disabled.
          </p>
          <div className="rounded-lg bg-green-50 border border-green-200 px-4 py-3 text-sm text-green-800">
            2FA is active on your account.
          </div>
        </div>
      </section>
    </div>
  );
}
