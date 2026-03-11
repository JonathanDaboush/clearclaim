import { useMutation } from '@tanstack/react-query';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { authApi } from '@/api/auth';
import { Button } from '@/components/common/Button';
import { StatusBadge } from '@/components/common/StatusBadge';
import { useAuthStore } from '@/stores/authStore';
import { format } from 'date-fns';
import { toast } from 'react-toastify';

interface DeviceRow {
  id: string;
  device_info: string;
  trusted: boolean;
  added_at?: string;
}

export default function DevicesPage() {
  const qc = useQueryClient();
  const { session } = useAuthStore();

  const { data: devices = [], isLoading } = useQuery({
    queryKey: ['devices', session?.user_id],
    queryFn: () => authApi.getDevices(session!.user_id),
    enabled: !!session?.user_id,
  });

  const revokeMutation = useMutation({
    mutationFn: (device_id: string) => authApi.revokeDevice(session!.user_id, device_id),
    onSuccess: () => {
      toast.success('Device revoked. It can no longer sign or access this account.');
      qc.invalidateQueries({ queryKey: ['devices', session?.user_id] });
    },
    onError: () => toast.error('Revocation failed.'),
  });

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Trusted Devices</h1>
        <p className="page-subtitle">
          Devices that have been registered to your account. You may revoke any device at any time.
          Revoked devices cannot sign contracts or access the system.
        </p>
      </div>

      <div className="px-6 pb-10 space-y-4">
        <div className="legal-notice text-xs">
          If you believe a device is lost or stolen, revoke it immediately. All sessions from that
          device will be invalidated. This action is permanently recorded in your audit log.
        </div>

        <div className="card">
          <div className="divide-y divide-border">
            {isLoading && <p className="px-5 py-4 text-sm text-secondary">Loadingâ€¦</p>}
            {!isLoading && (devices as DeviceRow[]).length === 0 && (
              <p className="px-5 py-4 text-sm text-secondary">No registered devices.</p>
            )}
            {(devices as DeviceRow[]).map((device) => (
              <div key={device.id} className="px-5 py-4 flex items-center gap-4">
                <div className="w-9 h-9 rounded-lg bg-section flex items-center justify-center shrink-0">
                  <svg className="w-4 h-4 text-meta" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>

                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-primary">{device.device_info}</p>
                  <p className="text-xs text-meta mt-0.5 font-mono truncate">{device.id}</p>
                  {device.added_at && (
                    <p className="text-xs text-meta mt-0.5">
                      Added {format(new Date(device.added_at), 'dd MMM yyyy, HH:mm')}
                    </p>
                  )}
                </div>

                <StatusBadge status={device.trusted ? 'verified' : 'failed'} />

                <Button
                  size="sm"
                  variant="danger"
                  loading={revokeMutation.isPending}
                  onClick={() => {
                    if (confirm(`Revoke this device? This cannot be undone.`)) {
                      revokeMutation.mutate(device.id);
                    }
                  }}
                >
                  Revoke
                </Button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

