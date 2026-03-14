import { useState, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { authApi } from '@/api/auth';
import { Button } from '@/components/common/Button';
import { Modal } from '@/components/common/Modal';
import { useAuthStore } from '@/stores/authStore';
import { StatusBadge } from '@/components/common/StatusBadge';
import { toast } from 'react-toastify';
import { useNavigate, Link } from 'react-router-dom';

const CONSENT_KEY = 'clearclaim_marketing_consent';

function ConsentManagement() {
  const [marketing, setMarketing] = useState<boolean>(() => {
    return localStorage.getItem(CONSENT_KEY) !== 'false';
  });

  useEffect(() => {
    localStorage.setItem(CONSENT_KEY, String(marketing));
  }, [marketing]);

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="text-sm font-semibold text-primary">Consent Management</h2>
      </div>
      <div className="card-body space-y-4">
        <p className="text-sm text-secondary">
          Manage your preferences for how ClearClaim uses your data beyond what is strictly
          necessary to operate the service. You can change these at any time.
        </p>

        {/* Marketing consent */}
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <p className="text-sm font-medium text-primary">Marketing &amp; product updates</p>
            <p className="text-xs text-secondary mt-0.5">
              Receive product announcements, feature highlights, and relevant legal-tech news
              by email. We will never sell your contact details.
            </p>
          </div>
          <button
            role="switch"
            aria-checked={marketing}
            aria-label="Toggle marketing emails"
            onClick={() => {
              setMarketing((v) => !v);
              toast.success(marketing ? 'Marketing emails disabled.' : 'Marketing emails enabled.');
            }}
            className={`relative inline-flex h-6 w-11 shrink-0 rounded-full border-2 border-transparent transition-colors focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 ${marketing ? 'bg-accent' : 'bg-border'}`}
          >
            <span
              className={`pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow ring-0 transition-transform ${marketing ? 'translate-x-5' : 'translate-x-0'}`}
            />
          </button>
        </div>

        {/* Essential notice */}
        <div className="legal-notice text-xs">
          Essential service communications (security alerts, account changes, legal agreement
          notifications) are not subject to marketing consent and will always be delivered.
        </div>
      </div>
    </div>
  );
}

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

        {/* Legal Documents */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-sm font-semibold text-primary">Legal Documents</h2>
          </div>
          <div className="card-body divide-y divide-border">
            {[
              { to: '/legal/terms',         label: 'Terms of Service',                        desc: 'Governing terms for use of the platform' },
              { to: '/privacy',             label: 'Privacy Policy',                          desc: 'How we collect, use, and protect your data (PIPEDA)' },
              { to: '/legal/esignature',    label: 'Electronic Signature Disclosure',         desc: 'ESIGN Act consent and how signatures are recorded' },
              { to: '/legal/data-retention',label: 'Data Retention Policy',                  desc: 'Retention periods for contracts, evidence, and audit logs' },
            ].map(({ to, label, desc }) => (
              <Link
                key={to}
                to={to}
                className="flex items-center justify-between gap-4 py-3 group"
              >
                <div>
                  <p className="text-sm font-medium text-primary group-hover:text-accent transition-colors">{label}</p>
                  <p className="text-xs text-meta mt-0.5">{desc}</p>
                </div>
                <svg className="w-3.5 h-3.5 text-meta shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            ))}
          </div>
        </div>

        {/* Privacy Policy & Terms of Service */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-sm font-semibold text-primary">Privacy Policy &amp; Terms of Service</h2>
          </div>
          <div className="card-body space-y-3 text-sm text-secondary">
            <p>
              ClearClaim operates under the Personal Information Protection and Electronic Documents Act
              (PIPEDA) and applicable provincial privacy legislation. Where users are located in California,
              the California Consumer Privacy Act (CCPA) rights apply. Electronic signatures are legally
              binding under ESIGN (USA), UETA (USA), and eIDAS (EU) as applicable.
            </p>
            <p>
              <strong className="text-primary">Your rights:</strong> You have the right to access, correct,
              and port your personal data. You may withdraw consent for non-essential processing at any time
              without affecting the lawfulness of prior processing. Requests can be submitted via the &ldquo;Export
              Your Data&rdquo; section above or by contacting{' '}
              <a href="mailto:privacy@clearclaim.io" className="text-accent underline">privacy@clearclaim.io</a>.
            </p>
            <p>
              <strong className="text-primary">Governing law:</strong> This agreement is governed by the laws
              of the Province of Ontario, Canada. Any disputes shall be resolved through binding arbitration
              in Toronto, Ontario, except where prohibited by applicable consumer-protection legislation.
            </p>
            <p>
              <strong className="text-primary">Data retention:</strong> Account data is retained for the
              duration of your account. Evidence, signatures, and audit logs tied to legally executed
              agreements are retained for a minimum of 7 years as required by applicable law, regardless
              of account status.
            </p>
          </div>
        </div>

        {/* Data Breach Notification */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-sm font-semibold text-primary">Data Breach Notification</h2>
          </div>
          <div className="card-body space-y-3 text-sm text-secondary">
            <p>
              In the event of a security incident that creates a real risk of significant harm, ClearClaim will
              notify affected users and the applicable privacy commissioner within <strong className="text-primary">72 hours</strong> of
              becoming aware of the breach, in accordance with PIPEDA Breach of Security Safeguards Regulations.
            </p>
            <p>
              Notifications will be sent to the email address registered with your account and will include:
              a description of the incident, the personal information involved, steps taken to reduce risk,
              and recommended actions you can take to protect yourself.
            </p>
            <p className="text-xs text-meta">
              To report a suspected security issue, contact{' '}
              <a href="mailto:security@clearclaim.io" className="text-accent underline">security@clearclaim.io</a>.
            </p>
          </div>
        </div>

        {/* Data Localization */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-sm font-semibold text-primary">Data Localization</h2>
          </div>
          <div className="card-body space-y-3 text-sm text-secondary">
            <p>
              ClearClaim stores all user data on servers located in <strong className="text-primary">Canada (Ontario)</strong>.
              No personal data is transferred outside Canada except where required to deliver a specific
              integration you have explicitly enabled (e.g. third-party identity verification providers).
              In such cases, equivalent safeguards are in place per PIPEDA Schedule 1 Principle 7.
            </p>
            <p className="text-xs text-meta">
              Compliance basis: PIPEDA — Schedule 1 Principles; SOC 2 Type II controls applied to
              infrastructure. Audit reports available on request.
            </p>
          </div>
        </div>

        {/* Consent Management */}
        <ConsentManagement />

        {/* Accessibility Statement */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-sm font-semibold text-primary">Accessibility Statement</h2>
          </div>
          <div className="card-body space-y-3 text-sm text-secondary">
            <p>
              ClearClaim is committed to ensuring digital accessibility for people with disabilities.
              This application aims to conform to the Web Content Accessibility Guidelines (WCAG) 2.1 Level AA.
              We continually evaluate and improve the user experience for everyone.
            </p>
            <p>
              If you experience accessibility barriers or require this content in an accessible format,
              please contact{' '}
              <a href="mailto:accessibility@clearclaim.io" className="text-accent underline">accessibility@clearclaim.io</a>.
              We aim to respond to accessibility requests within 2 business days.
            </p>
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
