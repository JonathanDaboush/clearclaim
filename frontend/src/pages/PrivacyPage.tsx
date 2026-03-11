import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { authApi } from '@/api/auth';
import { Button } from '@/components/common/Button';
import { Modal } from '@/components/common/Modal';
import { useAuthStore } from '@/stores/authStore';
import { StatusBadge } from '@/components/common/StatusBadge';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';

export default function PrivacyPage() {
  const { session, clearSession } = useAuthStore();
  const navigate = useNavigate();
  const [deleteOpen,  setDeleteOpen]  = useState(false);
  const [confirm,     setConfirm]     = useState('');
  const [deleteError, setDeleteError] = useState('');

  const identityMutation = useMutation({
    mutationFn: () => authApi.startIdentityVerification(session!.user_id),
    onSuccess: (res: any) => {
      if (res?.verification_url) {
        window.open(res.verification_url, '_blank');
      } else {
        toast.info('Identity verification initiated. Check your email for instructions.');
      }
    },
    onError: () => toast.error('Could not start identity verification.'),
  });

  const exportMutation = useMutation({
    mutationFn: async () => {
      const data = {
        user_id: session?.user_id,
        email: session?.email,
        verification_status: session?.verification_status,
        exported_at: new Date().toISOString(),
      };
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'clearclaim-my-data.json';
      a.click();
      URL.revokeObjectURL(url);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => authApi.removeAccount(session!.user_id),
    onSuccess: () => {
      clearSession();
      navigate('/login');
    },
    onError: () => setDeleteError('Account deletion failed. Please try again or contact support.'),
  });

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Privacy &amp; Data</h1>
        <p className="page-subtitle">
          Manage your personal data, identity verification, and account deletion.
          Your rights under PIPEDA and applicable privacy legislation are supported here.
        </p>
      </div>

      <div className="px-6 pb-10 space-y-6 max-w-2xl">

        {/* Identity Verification */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-sm font-semibold text-primary">Identity Verification</h2>
          </div>
          <div className="card-body space-y-3">
            <div className="flex items-center gap-3">
              <StatusBadge status={session?.verification_status ?? 'unverified'} />
            </div>

            <p className="text-sm text-secondary">
              Government ID verification increases the legal assurance level of agreements
              you sign. Your raw identification documents are never stored â€” only verification
              status, provider, and timestamp are retained.
            </p>

            {session?.verification_status !== 'verified' && (
              <Button
                variant="primary"
                size="sm"
                loading={identityMutation.isPending}
                onClick={() => identityMutation.mutate()}
              >
                Start Identity Verification
              </Button>
            )}
          </div>
        </div>

        {/* Data Export */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-sm font-semibold text-primary">Export Your Data</h2>
          </div>
          <div className="card-body space-y-3">
            <p className="text-sm text-secondary">
              You have the right to access and portably export the personal data held about
              you on this platform, in accordance with PIPEDA and the CCPA.
            </p>
            <p className="text-xs text-meta">
              This export includes your account details and verification status.
              Contract records, evidence, and audit logs belong to the project and are exported
              per-contract from within that contract's record.
            </p>
            <Button
              variant="secondary"
              size="sm"
              loading={exportMutation.isPending}
              onClick={() => exportMutation.mutate()}
            >
              Download My Data (JSON)
            </Button>
          </div>
        </div>

        {/* Account deletion */}
        <div className="card border-disputed/30">
          <div className="card-header bg-[color-mix(in_srgb,#C05656_8%,#fff)] rounded-t-lg">
            <h2 className="text-sm font-semibold text-disputed">Delete Account</h2>
          </div>
          <div className="card-body space-y-3">
            <div className="legal-notice text-xs">
              Account deletion is subject to evidence retention requirements. If you are a
              signatory to active agreements, your participation record (name, signature hashes,
              timestamps) is preserved as part of the immutable agreement record as required by
              applicable law. You will be removed from future signing or evidence obligations.
            </div>
            <p className="text-sm text-secondary">
              Your personal contact information and login credentials will be removed.
              You will lose access to this account and all associated projects.
            </p>
            <Button
              variant="danger"
              size="sm"
              onClick={() => setDeleteOpen(true)}
            >
              Request Account Deletion
            </Button>
          </div>
        </div>
      </div>

      {/* Delete confirmation modal */}
      <Modal
        open={deleteOpen}
        onClose={() => setDeleteOpen(false)}
        title="Confirm Account Deletion"
        blocking
      >
        <div className="space-y-4">
          <div className="legal-notice text-xs">
            This action permanently removes your login credentials and personal data. It cannot
            be reversed. Evidence and signatures you created in legally binding agreements are retained
            per applicable retention requirements.
          </div>

          <p className="text-sm text-secondary">
            Type <strong>DELETE</strong> to confirm you authorise permanent account deletion.
          </p>

          <div>
            <label className="form-label">Confirmation</label>
            <input
              type="text"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              className="form-input uppercase tracking-widest"
              placeholder="DELETE"
              autoFocus
            />
          </div>

          {deleteError && <p className="form-error">{deleteError}</p>}

          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => { setDeleteOpen(false); setConfirm(''); setDeleteError(''); }}>
              Cancel
            </Button>
            <Button
              variant="danger"
              loading={deleteMutation.isPending}
              disabled={confirm !== 'DELETE'}
              onClick={() => deleteMutation.mutate()}
            >
              Permanently Delete Account
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
