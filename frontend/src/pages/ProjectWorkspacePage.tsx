import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { projectsApi } from '@/api/projects';
import type { ProjectData, MemberData } from '@/api/projects';
import { contractsApi } from '@/api/contracts';
import type { ContractData } from '@/api/contracts';
import { AuditTrail } from '@/components/audit/AuditTrail';
import { EvidencePanel } from '@/components/evidence/EvidencePanel';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Button } from '@/components/common/Button';
import { Modal } from '@/components/common/Modal';
import { useAuthStore } from '@/stores/authStore';
import { format } from 'date-fns';
import { toast } from 'react-toastify';

type Tab = 'timeline' | 'contracts' | 'evidence' | 'members' | 'settings';

export default function ProjectWorkspacePage() {
  const { projectId } = useParams<{ projectId: string }>();
  const { session } = useAuthStore();
  const navigate = useNavigate();
  const qc = useQueryClient();

  const [tab,             setTab]            = useState<Tab>('timeline');
  const [createOpen,      setCreateOpen]     = useState(false);
  const [contractContent, setContractContent] = useState('');
  const [inviteOpen,      setInviteOpen]     = useState(false);
  const [inviteEmail,     setInviteEmail]    = useState('');
  const [inviteRole,      setInviteRole]     = useState('worker');
  const [changeRoleOpen,  setChangeRoleOpen] = useState(false);
  const [changeRoleTarget, setChangeRoleTarget] = useState<MemberData | null>(null);
  const [newRole,         setNewRole]        = useState('worker');

  const { data: members = [], refetch: refetchMembers } = useQuery({
    queryKey: ['project-members', projectId],
    queryFn: () => projectsApi.getMembers(projectId!),
    enabled: !!projectId,
  });

  const changeRoleMutation = useMutation({
    mutationFn: ({ userId, role }: { userId: string; role: string }) =>
      projectsApi.changeUserRole(projectId!, userId, role),
    onSuccess: () => {
      toast.success('Role updated.');
      refetchMembers();
      setChangeRoleOpen(false);
      setChangeRoleTarget(null);
    },
    onError: () => toast.error('Failed to update role.'),
  });

  const removeMemberMutation = useMutation({
    mutationFn: (userId: string) => projectsApi.leave(userId, projectId!),
    onSuccess: () => { toast.success('Member removed.'); refetchMembers(); },
    onError: () => toast.error('Failed to remove member.'),
  });

  const { data: projects = [], isLoading: loadingProjects } = useQuery({
    queryKey: ['user-projects', session?.user_id],
    queryFn: () => projectsApi.getUserProjects(session!.user_id),
    enabled: !!session?.user_id,
  });

  const project: ProjectData | undefined = (projects as ProjectData[]).find((p) => p.id === projectId);

  const { data: contracts = [], isLoading: loadingContracts } = useQuery({
    queryKey: ['project-contracts', projectId],
    queryFn: () => projectsApi.getProjectContracts(projectId!),
    enabled: !!projectId,
  });

  const createContractMutation = useMutation({
    mutationFn: () => contractsApi.create(projectId!, session!.user_id, contractContent),
    onSuccess: (res) => {
      toast.success('Contract created.');
      qc.invalidateQueries({ queryKey: ['project-contracts', projectId] });
      setCreateOpen(false);
      setContractContent('');
      navigate(`/projects/${projectId}/contracts/${res.contract_id}`);
    },
    onError: () => toast.error('Failed to create contract.'),
  });

  const TABS: { id: Tab; label: string }[] = [
    { id: 'timeline',  label: 'Timeline'  },
    { id: 'contracts', label: 'Contracts' },
    { id: 'evidence',  label: 'Evidence'  },
    { id: 'members',   label: 'Members'   },
    { id: 'settings',  label: 'Settings'  },
  ];

  if (loadingProjects) {
    return <div className="p-6 text-sm text-secondary">Loading project…</div>;
  }

  if (!project && !loadingProjects) {
    return (
      <div className="p-6">
        <p className="text-sm text-secondary">Project not found.</p>
        <button className="text-sm text-accent mt-2 hover:underline" onClick={() => navigate('/projects')}>
          ← Back to projects
        </button>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="page-header">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <button
              className="text-xs text-meta hover:text-accent mb-1 flex items-center gap-1"
              onClick={() => navigate('/projects')}
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              All Projects
            </button>
            <h1 className="page-title">{project?.name ?? '…'}</h1>
            <p className="page-subtitle">
              {project && `Created ${format(new Date(project.created_at), 'dd MMM yyyy')}`}
            </p>
          </div>
          {tab === 'contracts' && (
            <Button size="sm" variant="primary" onClick={() => setCreateOpen(true)}>
              + New Contract
            </Button>
          )}
        </div>
      </div>

      {/* Sub-tab navigation */}
      <div className="px-6 border-b border-border bg-card flex gap-1 overflow-x-auto">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`
              px-3 py-3 text-sm border-b-2 transition-colors whitespace-nowrap
              ${tab === t.id
                ? 'border-accent text-accent font-semibold'
                : 'border-transparent text-secondary hover:text-primary'}
            `}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="px-6 py-6">
        {/* Timeline tab */}
        {tab === 'timeline' && projectId && (
          <AuditTrail projectId={projectId} />
        )}

        {/* Contracts tab */}
        {tab === 'contracts' && (
          <div className="space-y-3">
            {loadingContracts && <p className="text-sm text-secondary">Loading contracts…</p>}
            {!loadingContracts && (contracts as ContractData[]).length === 0 && (
              <div className="card p-8 text-center">
                <p className="text-sm text-secondary mb-3">No contracts in this project yet.</p>
                <Button variant="primary" size="sm" onClick={() => setCreateOpen(true)}>
                  Create First Contract
                </Button>
              </div>
            )}
            {(contracts as ContractData[]).map((contract) => (
              <div
                key={contract.id}
                className="card p-4 flex items-center justify-between gap-4 hover:bg-section transition-colors cursor-pointer"
                onClick={() => navigate(`/projects/${projectId}/contracts/${contract.id}`)}
              >
                <div>
                  <p className="text-sm font-medium text-primary">Contract</p>
                  <p className="text-xs text-meta font-mono mt-0.5">{contract.id}</p>
                  <p className="text-xs text-secondary mt-1">
                    Created {format(new Date(contract.created_at), 'dd MMM yyyy')} by {contract.created_by}
                  </p>
                </div>
                <svg className="w-4 h-4 text-meta shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            ))}
          </div>
        )}

        {/* Evidence tab */}
        {tab === 'evidence' && (contracts as ContractData[]).length > 0 && (
          <div className="space-y-6">
            {(contracts as ContractData[]).map((contract) => (
              <div key={contract.id}>
                <p className="text-xs text-secondary font-mono mb-2">
                  Contract: {contract.id}
                </p>
                <EvidencePanel
                  contractId={contract.id}
                  canAdd
                  canRequestDeletion
                  canApprove
                />
              </div>
            ))}
          </div>
        )}
        {tab === 'evidence' && (contracts as ContractData[]).length === 0 && (
          <p className="text-sm text-secondary">No contracts yet — create a contract to add evidence.</p>
        )}

        {/* Members tab */}
        {tab === 'members' && project && (
          <div className="space-y-4">
            <div className="card">
              <div className="card-header flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-semibold text-primary">Project Members</h3>
                  <p className="text-xs text-secondary mt-0.5">
                    {(members as MemberData[]).length} member{(members as MemberData[]).length !== 1 ? 's' : ''} · role-based access
                  </p>
                </div>
              </div>
              <div className="card-body divide-y divide-border">
                {(members as MemberData[]).length === 0 && (
                  <p className="text-xs text-meta py-4 text-center">No members yet.</p>
                )}
                {(members as MemberData[]).map((m) => {
                  const isMe = m.user_id === session?.user_id;
                  const roleLabel = {
                    worker_manager: 'Worker Manager',
                    worker: 'Worker',
                    legal_rep: 'Legal Rep',
                    client: 'Client',
                    guest: 'Guest',
                  }[m.role_id] ?? m.role_id;
                  return (
                    <div key={m.id} className="flex items-center gap-3 py-3">
                      <div className="w-8 h-8 rounded-full bg-accent-light flex items-center justify-center shrink-0">
                        <span className="text-xs font-semibold text-accent">
                          {m.user_id.slice(0, 2).toUpperCase()}
                        </span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-primary font-mono truncate">
                          {m.user_id}{isMe && <span className="ml-1 text-xs text-accent">(you)</span>}
                        </p>
                        <p className="text-xs text-secondary">{roleLabel}</p>
                      </div>
                      {!isMe && (
                        <div className="flex items-center gap-2 shrink-0">
                          <button
                            className="text-xs text-accent hover:text-accent-hover"
                            onClick={() => {
                              setChangeRoleTarget(m);
                              setNewRole(m.role_id);
                              setChangeRoleOpen(true);
                            }}
                          >
                            Change Role
                          </button>
                          <button
                            className="text-xs text-disputed hover:underline"
                            onClick={() => {
                              if (window.confirm('Remove this member from the project?')) {
                                removeMemberMutation.mutate(m.user_id);
                              }
                            }}
                          >
                            Remove
                          </button>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Change Role Modal */}
        <Modal open={changeRoleOpen} onClose={() => setChangeRoleOpen(false)} title="Change Member Role">
          <div className="space-y-4">
            <p className="text-xs text-secondary font-mono">{changeRoleTarget?.user_id}</p>
            <div>
              <label className="form-label">New Role</label>
              <select value={newRole} onChange={(e) => setNewRole(e.target.value)} className="form-input">
                <option value="worker_manager">Worker Manager — full access + manage workers</option>
                <option value="worker">Worker — create/revise contracts, add evidence, sign</option>
                <option value="legal_rep">Legal Rep — approve revisions, add evidence, sign</option>
                <option value="client">Client — sign contracts, view</option>
                <option value="guest">Guest — view only</option>
              </select>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="secondary" size="sm" onClick={() => setChangeRoleOpen(false)}>Cancel</Button>
              <Button
                variant="primary" size="sm"
                loading={changeRoleMutation.isPending}
                onClick={() => changeRoleTarget && changeRoleMutation.mutate({ userId: changeRoleTarget.user_id, role: newRole })}
              >Save</Button>
            </div>
          </div>
        </Modal>

        {/* Settings tab */}
        {tab === 'settings' && project && (
          <div className="space-y-4">
            <div className="card">
              <div className="card-header">
                <h3 className="text-sm font-semibold text-primary">Invite Member</h3>
                <p className="text-xs text-secondary mt-0.5">
                  Invite a user to this project and assign their role.
                </p>
              </div>
              <div className="card-body space-y-3">
                <div>
                  <label className="form-label">User ID or Email</label>
                  <input
                    type="text"
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    className="form-input"
                    placeholder="user-id or email@example.com"
                  />
                </div>
                <div>
                  <label className="form-label">Role</label>
                  <select
                    value={inviteRole}
                    onChange={(e) => setInviteRole(e.target.value)}
                    className="form-input"
                  >
                    <option value="worker_manager">Worker Manager — full access + manage workers</option>
                    <option value="worker">Worker — create/revise contracts, add evidence, sign</option>
                    <option value="legal_rep">Legal Rep — approve revisions, add evidence, sign</option>
                    <option value="client">Client — sign contracts, view</option>
                    <option value="guest">Guest — view only</option>
                  </select>
                </div>
                <div className="flex justify-end">
                  <Button
                    variant="primary"
                    size="sm"
                    disabled={!inviteEmail.trim()}
                    onClick={() => {
                      if (projectId && inviteEmail.trim()) {
                        projectsApi.inviteUser(projectId, inviteEmail.trim(), inviteRole)
                          .then(() => { toast.success('Invitation sent.'); setInviteEmail(''); })
                          .catch(() => toast.error('Invitation failed.'));
                      }
                    }}
                  >
                    Send Invitation
                  </Button>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <h3 className="text-sm font-semibold text-primary">Project Info</h3>
              </div>
              <div className="card-body space-y-2">
                <div>
                  <p className="text-xs text-meta uppercase tracking-wide">Project ID</p>
                  <p className="text-sm font-mono text-primary mt-0.5">{project.id}</p>
                </div>
                <div>
                  <p className="text-xs text-meta uppercase tracking-wide">Main Party</p>
                  <p className="text-sm font-mono text-primary mt-0.5">{project.main_party_id}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Create Contract Modal */}
      <Modal
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        title="Create New Contract"
        size="xl"
      >
        <div className="space-y-4">
          <div className="legal-notice text-xs">
            The contract text you provide will form the initial version (v1). All parties must
            sign this version. Changes must be proposed as revisions and require unanimous approval.
          </div>

          <div>
            <label className="form-label">Contract Text</label>
            <textarea
              value={contractContent}
              onChange={(e) => setContractContent(e.target.value)}
              rows={14}
              className="form-textarea font-mono text-xs"
              placeholder="Enter the full contract text here…"
            />
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => setCreateOpen(false)}>Cancel</Button>
            <Button
              variant="primary"
              loading={createContractMutation.isPending}
              disabled={!contractContent.trim()}
              onClick={() => createContractMutation.mutate()}
            >
              Create Contract
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
