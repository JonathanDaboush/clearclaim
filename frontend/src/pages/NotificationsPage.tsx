import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { notificationsApi } from '@/api/notifications';
import type { NotificationData } from '@/api/notifications';
import { useAuthStore } from '@/stores/authStore';
import { format } from 'date-fns';
import { Button } from '@/components/common/Button';
import { toast } from 'react-toastify';

export default function NotificationsPage() {
  const qc = useQueryClient();
  const { session } = useAuthStore();

  const { data: notifications = [], isLoading } = useQuery({
    queryKey: ['notifications', session?.user_id],
    queryFn: () => notificationsApi.getAll(session!.user_id),
    enabled: !!session?.user_id,
  });

  const markReadMutation = useMutation({
    mutationFn: (id: string) => notificationsApi.markRead(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['notifications', session?.user_id] }),
    onError: () => toast.error('Could not mark notification.'),
  });

  const sorted = [...(notifications as NotificationData[])].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Notifications</h1>
        <p className="page-subtitle">Actions and updates that require your attention.</p>
      </div>

      <div className="px-6 pb-10">
        <div className="card">
          <div className="divide-y divide-border">
            {isLoading && <p className="px-5 py-4 text-sm text-secondary">Loadingâ€¦</p>}

            {!isLoading && sorted.length === 0 && (
              <p className="px-5 py-8 text-sm text-secondary text-center">No notifications.</p>
            )}

            {sorted.map((n) => (
              <div
                key={n.id}
                className={`px-5 py-4 flex items-start gap-4 ${n.is_read ? '' : 'bg-accent-light'}`}
              >
                {!n.is_read && (
                  <span className="w-2 h-2 rounded-full bg-accent mt-1.5 shrink-0" />
                )}
                {n.is_read && <span className="w-2 shrink-0" />}

                <div className="flex-1">
                  <p className={`text-sm font-medium ${n.is_read ? 'text-primary' : 'text-accent'}`}>
                    {n.type.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                  </p>
                  <p className="text-xs text-secondary mt-0.5">{n.message}</p>
                  <p className="text-xs text-meta mt-1">
                    {format(new Date(n.created_at), 'dd MMM yyyy, HH:mm')}
                  </p>
                </div>

                {!n.is_read && (
                  <Button
                    size="sm"
                    variant="ghost"
                    loading={markReadMutation.isPending}
                    onClick={() => markReadMutation.mutate(n.id)}
                  >
                    Mark read
                  </Button>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

