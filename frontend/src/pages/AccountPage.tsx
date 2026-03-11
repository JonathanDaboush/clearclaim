import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { authApi } from '@/api/auth';
import { Button } from '@/components/common/Button';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Modal } from '@/components/common/Modal';
import { useAuthStore } from '@/stores/authStore';
import { toast } from 'react-toastify';

// Accessibility preferences stored in localStorage
const A11Y_KEY = 'cc_a11y';
interface A11yPrefs {
  highContrast: boolean;
  reducedMotion: boolean;
  largeText: boolean;
  screenReader: boolean;
  captions: boolean;
}
function loadA11y(): A11yPrefs {
  try { return { highContrast: false, reducedMotion: false, largeText: false, screenReader: false, captions: false, ...JSON.parse(localStorage.getItem(A11Y_KEY) ?? '{}') }; }
  catch { return { highContrast: false, reducedMotion: false, largeText: false, screenReader: false, captions: false }; }
}
function saveA11y(p: A11yPrefs) {
  localStorage.setItem(A11Y_KEY, JSON.stringify(p));
  // Apply immediately
  document.documentElement.classList.toggle('high-contrast', p.highContrast);
  document.documentElement.classList.toggle('reduce-motion', p.reducedMotion);
  document.documentElement.classList.toggle('large-text', p.largeText);
}

export default function AccountPage() {
  const { session, updateSession, clearSession } = useAuthStore();
  const qc = useQueryClient();

  const [pwOpen,     setPwOpen]     = useState(false);
  const [newPw,      setNewPw]      = useState('');
  const [newPw2,     setNewPw2]     = useState('');
  const [pwError,    setPwError]    = useState('');
  const [resetToken, setResetToken] = useState('');
  const [tokenSent,  setTokenSent]  = useState(false);
  const [a11y,       setA11y]       = useState<A11yPrefs>(loadA11y);

  const toggleA11y = (key: keyof A11yPrefs) => {
    const next = { ...a11y, [key]: !a11y[key] };
    setA11y(next);
    saveA11y(next);
  };

  // Fetch fresh identity status
  const { data: identityStatus } = useQuery({
    queryKey: ['identity-status', session?.user_id],
    queryFn: () => authApi.checkIdentityVerificationStatus(session!.user_id),
    enabled: !!session?.user_id,
  });
  const verStatus = identityStatus?.status ?? session?.verification_status ?? 'unverified';

  const sendResetMutation = useMutation({
    mutationFn: () => authApi.initiatePasswordReset(session!.email),
    onSuccess: () => {
      setTokenSent(true);
      toast.success('Password reset code sent to your email.');
    },
    onError: () => toast.error('Could not send reset code.'),
  });

  const completePwMutation = useMutation({
    mutationFn: () => authApi.completePasswordReset(resetToken, newPw),
    onSuccess: () => {
      toast.success('Password updated successfully.');
      setPwOpen(false);
      setNewPw('');
      setNewPw2('');
      setResetToken('');
      setTokenSent(false);
    },
    onError: () => setPwError('Password reset failed. Check your token and try again.'),
  });

  const identityMutation = useMutation({
    mutationFn: () => authApi.startIdentityVerification(session!.user_id),
    onSuccess: (res: any) => {
      if (res?.verification_url) {
        window.open(res.verification_url, '_blank');
      } else {
        toast.info('Identity verification initiated. Check your email.');
      }
      qc.invalidateQueries({ queryKey: ['identity-status', session?.user_id] });
    },
    onError: () => toast.error('Could not start identity verification.'),
  });

  const handlePwSubmit = () => {
    if (newPw.length < 12) { setPwError('Password must be at least 12 characters.'); return; }
    if (newPw !== newPw2)  { setPwError('Passwords do not match.'); return; }
    setPwError('');
    completePwMutation.mutate();
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Account Settings</h1>
        <p className="page-subtitle">
          Manage your profile, password, and identity verification.
        </p>
      </div>

      <div className="px-6 pb-10 space-y-6 max-w-2xl">

        {/* Profile */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-sm font-semibold text-primary">Profile</h2>
          </div>
          <div className="card-body space-y-3">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-accent flex items-center justify-center text-white text-lg font-semibold shrink-0">
                {session?.email?.[0]?.toUpperCase() ?? '?'}
              </div>
              <div>
                <p className="text-sm font-medium text-primary">{session?.email}</p>
                <p className="text-xs text-meta">{session?.user_id}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Identity Verification */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-sm font-semibold text-primary">Identity Verification</h2>
          </div>
          <div className="card-body space-y-3">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm text-secondary leading-relaxed">
                  Government ID verification increases the legal assurance of agreements you sign.
                  Verification results are stored by status only — no raw ID data is retained.
                </p>
              </div>
              <StatusBadge status={verStatus} />
            </div>
            {verStatus !== 'verified' && (
              <Button
                variant="primary"
                size="sm"
                loading={identityMutation.isPending}
                onClick={() => identityMutation.mutate()}
              >
                Start Verification
              </Button>
            )}
          </div>
        </div>

        {/* Two-Factor Authentication */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-sm font-semibold text-primary">Two-Factor Authentication</h2>
          </div>
          <div className="card-body">
            <div className="flex items-center justify-between gap-4">
              <p className="text-sm text-secondary">
                An authenticator app is required for login and every signing action.
                TOTP is permanently enabled on this account.
              </p>
              <StatusBadge status="verified" />
            </div>
          </div>
        </div>

        {/* Change Password */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-sm font-semibold text-primary">Password</h2>
          </div>
          <div className="card-body">
            <p className="text-sm text-secondary mb-3">
              A reset code will be sent to <strong>{session?.email}</strong>.
            </p>
            <Button variant="secondary" size="sm" onClick={() => { setPwOpen(true); setTokenSent(false); }}>
              Change Password
            </Button>
          </div>
        </div>

        {/* Accessibility Settings */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-sm font-semibold text-primary">Accessibility</h2>
          </div>
          <div className="card-body space-y-3">
            {([
              { key: 'highContrast',  label: 'High Contrast Mode',  desc: 'Increase contrast for better visibility.' },
              { key: 'largeText',     label: 'Larger Text',         desc: 'Increase base font size throughout the app.' },
              { key: 'reducedMotion', label: 'Reduce Motion',       desc: 'Minimize animations and transitions.' },
              { key: 'screenReader',  label: 'Screen Reader Mode',  desc: 'Optimize layout cues for screen readers.' },
              { key: 'captions',      label: 'Captions / Subtitles', desc: 'Show captions for audio and video evidence.' },
            ] as const).map(({ key, label, desc }) => (
              <div key={key} className="flex items-center justify-between gap-4 py-1 border-b border-border last:border-0">
                <div>
                  <p className="text-sm font-medium text-primary">{label}</p>
                  <p className="text-xs text-meta">{desc}</p>
                </div>
                <button
                  role="switch"
                  aria-checked={a11y[key]}
                  onClick={() => toggleA11y(key)}
                  className={`relative inline-flex h-5 w-9 shrink-0 rounded-full border-2 border-transparent transition-colors focus:outline-none focus:ring-2 focus:ring-accent ${a11y[key] ? 'bg-accent' : 'bg-border-strong'}`}
                >
                  <span className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${a11y[key] ? 'translate-x-4' : 'translate-x-0'}`} />
                </button>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Change-password modal */}
      <Modal open={pwOpen} onClose={() => setPwOpen(false)} title="Change Password">
        <div className="space-y-4">
          {!tokenSent ? (
            <>
              <p className="text-sm text-secondary">
                A one-time reset token will be sent to your email address.
              </p>
              <div className="flex justify-end gap-2">
                <Button variant="ghost" onClick={() => setPwOpen(false)}>Cancel</Button>
                <Button
                  variant="primary"
                  loading={sendResetMutation.isPending}
                  onClick={() => sendResetMutation.mutate()}
                >
                  Send Reset Token
                </Button>
              </div>
            </>
          ) : (
            <>
              <div>
                <label className="form-label">Reset Token (from email)</label>
                <input
                  type="text"
                  value={resetToken}
                  onChange={(e) => setResetToken(e.target.value)}
                  className="form-input font-mono"
                  placeholder="Paste token here"
                />
              </div>
              <div>
                <label className="form-label">New Password</label>
                <input
                  type="password"
                  value={newPw}
                  onChange={(e) => setNewPw(e.target.value)}
                  className="form-input"
                  autoComplete="new-password"
                />
                <p className="text-xs text-meta mt-1">Minimum 12 characters</p>
              </div>
              <div>
                <label className="form-label">Confirm New Password</label>
                <input
                  type="password"
                  value={newPw2}
                  onChange={(e) => setNewPw2(e.target.value)}
                  className="form-input"
                  autoComplete="new-password"
                />
              </div>
              {pwError && <p className="form-error">{pwError}</p>}
              <div className="flex justify-end gap-2">
                <Button variant="ghost" onClick={() => setPwOpen(false)}>Cancel</Button>
                <Button
                  variant="primary"
                  loading={completePwMutation.isPending}
                  disabled={!resetToken || !newPw}
                  onClick={handlePwSubmit}
                >
                  Update Password
                </Button>
              </div>
            </>
          )}
        </div>
      </Modal>
    </div>
  );
}
