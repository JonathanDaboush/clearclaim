/**
 * MemberList
 * ─────────────────────────────────────────────────────────────────────────────
 * Displays the member roster for a project. Shows each member's role,
 * verification status, and device count. Allows owners to change roles
 * or remove members.
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { projectsApi } from '@/api/projects';
import type { MemberData } from '@/api/projects';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Button } from '@/components/common/Button';
import { useAuthStore } from '@/stores/authStore';
import { toast } from 'react-toastify';

interface Props {
  projectId: string;
  /** Whether the current user may change roles or remove members. */
  canManage?: boolean;
}

const ROLE_LABELS: Record<string, string> = {
  worker_manager: 'Worker Manager',
  worker:         'Worker',
  legal_rep:      'Legal Representative',
  auditor:        'Auditor',
  owner:          'Owner',
};

export function MemberList({ projectId, canManage = false }: Props) {
  const { session } = useAuthStore();
  const qc = useQueryClient();

  const { data: members = [], isLoading } = useQuery({
    queryKey: ['project-members', projectId],
    queryFn:  () => projectsApi.getMembers(projectId),
    enabled:  !!projectId,
  });

  const removeMutation = useMutation({
    mutationFn: (userId: string) => projectsApi.leave(userId, projectId),
    onSuccess: () => {
      toast.success('Member removed.');
      qc.invalidateQueries({ queryKey: ['project-members', projectId] });
    },
    onError: () => toast.error('Failed to remove member.'),
  });

  if (isLoading) return <p className="text-sm text-meta">Loading members&hellip;</p>;

  if ((members as MemberData[]).length === 0) {
    return <p className="text-sm text-meta">No members yet.</p>;
  }

  return (
    <ul className="divide-y divide-border" role="list">
      {(members as MemberData[]).map((m) => (
        <li key={m.id} className="py-3 flex items-center justify-between gap-4">
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium text-primary truncate">
              {m.user_id}
            </p>
            <div className="flex items-center gap-2 mt-1 flex-wrap">
              <span className="text-xs text-meta">
                {ROLE_LABELS[m.role_id] ?? m.role_id}
              </span>
              {m.verification_status && (
                <StatusBadge status={m.verification_status} />
              )}
              {m.active_device_count !== undefined && (
                <span className="text-xs text-meta">
                  {m.active_device_count} device{m.active_device_count !== 1 ? 's' : ''}
                </span>
              )}
            </div>
          </div>

          {canManage && m.user_id !== session?.user_id && (
            <Button
              variant="secondary"
              onClick={() => removeMutation.mutate(m.user_id)}
              loading={removeMutation.isPending}
            >
              Remove
            </Button>
          )}
        </li>
      ))}
    </ul>
  );
}
