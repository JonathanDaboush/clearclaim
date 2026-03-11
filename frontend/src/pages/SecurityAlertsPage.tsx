import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { notificationsApi, type NotificationData } from '@/api/notifications';
import { securityApi } from '@/api/security';
import { useAuthStore } from '@/stores/authStore';
import { format } from 'date-fns';
import { Button } from '@/components/common/Button';
import { StatusBadge } from '@/components/common/StatusBadge';
import { toast } from 'react-toastify';

const SECURITY_TYPES = new Set([
  // Types actually emitted by the backend's SecurityService and related services
  'suspicious_activity', 'actions_restricted', 'device_recovery',
  'restriction_lifted', 'security_alert',
]);

export default function SecurityAlertsPage() {
  const qc = useQueryClient();
  const { session } = useAuthStore();

  const { data: notifications = [] } = useQuery<NotificationData[]>({
    queryKey: ['notifications', session?.user_id],
    queryFn: () => notificationsApi.getAll(session!.user_id),
    enabled: !!session?.user_id,
  });

  const { data: restrictionStatus } = useQuery({
    queryKey: ['is-restricted', session?.user_id],
    queryFn: () => securityApi.isRestricted(session!.user_id),
    enabled: !!session?.user_id,
  });

  const lockMutation = useMutation({
    mutationFn: () => securityApi.restrictActions(session!.user_id, 'manual_lock'),
    onSuccess: () => {
      toast.success('Account locked. Sensitive actions are now blocked.');
      qc.invalidateQueries({ queryKey: ['is-restricted', session?.user_id] });
    },
    onError: () => toast.error('Could not lock account.'),
  });

  const unlockMutation = useMutation({
    mutationFn: () => securityApi.liftRestriction(session!.user_id),
    onSuccess: () => {
      toast.success('Account unlocked. Activity approved.');
      qc.invalidateQueries({ queryKey: ['is-restricted', session?.user_id] });
      qc.invalidateQueries({ queryKey: ['notifications', session?.user_id] });
    },
    onError: () => toast.error('Could not lift restriction.'),
  });

  const isRestricted = restrictionStatus?.restricted ?? false;

  const securityAlerts = [...(notifications as NotificationData[])]
    .filter((n) => SECURITY_TYPES.has(n.type))
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Security Alerts</h1>
        <p className="page-subtitle">
          Suspicious activity on your account. Review each event and take action if needed.
        </p>
      </div>

      <div className="px-6 pb-10 space-y-6 max-w-2xl">

        {/* Account status + lock/unlock */}
        <div className="card">
          <div className="card-header flex items-center justify-between">
            <h2 className="text-sm font-semibold text-primary">Account Status</h2>
            <StatusBadge status={isRestricted ? 'disputed' : 'verified'} />
          </div>
          <div className="card-body space-y-3">
            <p className="text-sm text-secondary">
              {isRestricted
                ? 'Your account is currently locked. Signing and sensitive actions are blocked.'
                : 'Your account is active. You can lock it immediately if you detect suspicious activity.'}
            </p>
            <div className="flex gap-2">
              {!isRestricted ? (
                <Button
                  variant="danger"
                  size="sm"
                  loading={lockMutation.isPending}
                  onClick={() => {
                    if (window.confirm('Lock your account? Signing and sensitive actions will be blocked until you unlock it.')) {
                      lockMutation.mutate();
                    }
                  }}
                >
                  Lock Account
                </Button>
              ) : (
                <Button
                  variant="primary"
                  size="sm"
                  loading={unlockMutation.isPending}
                  onClick={() => {
                    if (window.confirm('Unlock your account and approve recent activity?')) {
                      unlockMutation.mutate();
                    }
                  }}
                >
                  Approve Activity &amp; Unlock
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* Security event list */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-sm font-semibold text-primary">Security Events</h2>
            <p className="text-xs text-secondary mt-0.5">{securityAlerts.length} event{securityAlerts.length !== 1 ? 's' : ''} recorded</p>
          </div>
          <div className="divide-y divide-border">
            {securityAlerts.length === 0 && (
              <p className="px-5 py-8 text-sm text-secondary text-center">No security events.</p>
            )}
            {securityAlerts.map((n) => (
              <div key={n.id} className={`px-5 py-4 flex items-start gap-4 ${!n.is_read ? 'bg-accent-light' : ''}`}>
                <div className="w-2 h-2 rounded-full mt-1.5 shrink-0 bg-disputed" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-primary">
                    {n.type.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                  </p>
                  <p className="text-xs text-secondary mt-0.5">{n.message}</p>
                  <p className="text-xs text-meta mt-1">
                    {format(new Date(n.created_at), 'dd MMM yyyy, HH:mm')}
                  </p>
                </div>
                <StatusBadge status={n.is_read ? 'verified' : 'pending'} />
              </div>
            ))}
          </div>
        </div>

        <p className="text-xs text-meta">
          All security events are permanently recorded in the audit log and cannot be deleted.
          If you believe your account has been compromised, lock it immediately and contact support.
        </p>
      </div>
    </div>
  );
}
