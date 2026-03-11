import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { projectsApi, type ProjectData } from '@/api/projects';
import { useAuthStore } from '@/stores/authStore';
import { Button } from '@/components/common/Button';
import { Modal } from '@/components/common/Modal';
import { format } from 'date-fns';
import { toast } from 'react-toastify';

export default function ProjectsPage() {
  const qc = useQueryClient();
  const { session } = useAuthStore();
  const [createOpen, setCreateOpen] = useState(false);
  const [name, setName] = useState('');

  const { data: projects = [], isLoading } = useQuery<ProjectData[]>({
    queryKey: ['projects', session?.user_id],
    queryFn: () => projectsApi.getUserProjects(session!.user_id),
    enabled: !!session?.user_id,
  });

  const createMutation = useMutation({
    mutationFn: () => projectsApi.create(name, session!.user_id),
    onSuccess: () => {
      toast.success('Project created.');
      qc.invalidateQueries({ queryKey: ['projects'] });
      setCreateOpen(false);
      setName('');
    },
    onError: () => toast.error('Failed to create project.'),
  });

  return (
    <div>
      <div className="page-header flex items-center justify-between">
        <div>
          <h1 className="page-title">Projects</h1>
          <p className="page-subtitle">Each project holds contracts, evidence, and an immutable audit trail.</p>
        </div>
        <Button variant="primary" onClick={() => setCreateOpen(true)}>+ New Project</Button>
      </div>

      <div className="px-6 pb-10">
        {isLoading && <p className="text-sm text-meta py-4">Loadingâ€¦</p>}

        {!isLoading && projects.length === 0 && (
          <div className="card text-center py-12">
            <p className="text-sm text-secondary">No projects yet.</p>
            <Button variant="primary" className="mt-4" onClick={() => setCreateOpen(true)}>
              Create your first project
            </Button>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((p) => (
            <Link
              key={p.id}
              to={`/projects/${p.id}`}
              className="card hover:shadow-card-md transition-shadow group block"
            >
              <div className="card-body">
                <p className="text-base font-semibold text-primary group-hover:text-accent">
                  {p.name}
                </p>
                <p className="text-xs text-meta mt-3">
                  Created {format(new Date(p.created_at), 'dd MMM yyyy')}
                </p>
              </div>
            </Link>
          ))}
        </div>
      </div>

      <Modal open={createOpen} onClose={() => setCreateOpen(false)} title="Create New Project">
        <div className="space-y-4">
          <div>
            <label className="form-label">Project Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="form-input"
              placeholder="e.g. Construction Agreement â€” 2026"
              onKeyDown={(e) => e.key === 'Enter' && name.trim() && createMutation.mutate()}
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => setCreateOpen(false)}>Cancel</Button>
            <Button
              variant="primary"
              loading={createMutation.isPending}
              disabled={!name.trim()}
              onClick={() => createMutation.mutate()}
            >
              Create Project
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
