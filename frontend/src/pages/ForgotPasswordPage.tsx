import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { authApi } from '@/api/auth';
import { Button } from '@/components/common/Button';

type Phase = 'email' | 'reset';

export default function ForgotPasswordPage() {
  const [phase,       setPhase]       = useState<Phase>('email');
  const [email,       setEmail]       = useState('');
  const [token,       setToken]       = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [newPassword2, setNewPassword2] = useState('');
  const [error,       setError]       = useState('');
  const [done,        setDone]        = useState(false);

  const initiateMutation = useMutation({
    mutationFn: () => authApi.initiatePasswordReset(email),
    onSuccess: () => {
      setPhase('reset');
      setError('');
    },
    onError: () => setError('Could not send reset code. Check your email address.'),
  });

  const completeMutation = useMutation({
    mutationFn: () => authApi.completePasswordReset(token, newPassword),
    onSuccess: () => setDone(true),
    onError: () => setError('Reset failed. The token may be expired or invalid.'),
  });

  const handleComplete = () => {
    if (newPassword.length < 12) { setError('Password must be at least 12 characters.'); return; }
    if (newPassword !== newPassword2) { setError('Passwords do not match.'); return; }
    completeMutation.mutate();
  };

  return (
    <div className="min-h-screen bg-bg flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-10 h-10 rounded-lg bg-accent mb-3">
            <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
            </svg>
          </div>
          <h1 className="text-xl font-semibold text-primary">ClearClaim</h1>
          <p className="text-sm text-secondary mt-1">Password Reset</p>
        </div>

        <div className="card">
          <div className="card-body space-y-5">
            {done ? (
              <>
                <div className="flex flex-col items-center gap-3 py-4">
                  <svg className="w-10 h-10 text-confirmed" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-sm font-medium text-primary text-center">Password updated successfully.</p>
                  <p className="text-xs text-secondary text-center">You can now sign in with your new password.</p>
                </div>
                <Link to="/login">
                  <Button variant="primary" className="w-full justify-center">
                    Sign In
                  </Button>
                </Link>
              </>
            ) : phase === 'email' ? (
              <>
                <h2 className="text-base font-semibold text-primary">Forgot Password</h2>
                <p className="text-sm text-secondary">
                  Enter your email address. We'll send a reset token you can use to set a new password.
                </p>
                <div>
                  <label className="form-label" htmlFor="email">Email Address</label>
                  <input
                    id="email"
                    type="email"
                    autoComplete="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="form-input"
                    placeholder="you@example.com"
                    onKeyDown={(e) => e.key === 'Enter' && initiateMutation.mutate()}
                  />
                </div>
                {error && <p className="form-error">{error}</p>}
                <Button
                  variant="primary"
                  className="w-full justify-center"
                  loading={initiateMutation.isPending}
                  disabled={!email.includes('@')}
                  onClick={() => initiateMutation.mutate()}
                >
                  Send Reset Token
                </Button>
              </>
            ) : (
              <>
                <h2 className="text-base font-semibold text-primary">Enter Reset Token</h2>
                <p className="text-sm text-secondary">
                  Check your email for the reset token, then enter it along with your new password.
                </p>
                <div>
                  <label className="form-label" htmlFor="token">Reset Token</label>
                  <input
                    id="token"
                    type="text"
                    value={token}
                    onChange={(e) => setToken(e.target.value)}
                    className="form-input font-mono"
                    placeholder="Paste token from email"
                  />
                </div>
                <div>
                  <label className="form-label" htmlFor="pw">New Password</label>
                  <input
                    id="pw"
                    type="password"
                    autoComplete="new-password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="form-input"
                  />
                  <p className="text-xs text-meta mt-1">Minimum 12 characters</p>
                </div>
                <div>
                  <label className="form-label" htmlFor="pw2">Confirm New Password</label>
                  <input
                    id="pw2"
                    type="password"
                    autoComplete="new-password"
                    value={newPassword2}
                    onChange={(e) => setNewPassword2(e.target.value)}
                    className="form-input"
                    onKeyDown={(e) => e.key === 'Enter' && handleComplete()}
                  />
                </div>
                {error && <p className="form-error">{error}</p>}
                <Button
                  variant="primary"
                  className="w-full justify-center"
                  loading={completeMutation.isPending}
                  disabled={!token.trim() || !newPassword}
                  onClick={handleComplete}
                >
                  Set New Password
                </Button>
                <button
                  onClick={() => { setPhase('email'); setError(''); }}
                  className="block w-full text-center text-xs text-accent hover:text-accent-hover"
                >
                  ← Back
                </button>
              </>
            )}
          </div>
        </div>

        <p className="text-center text-xs text-meta mt-6">
          Remember your password?{' '}
          <Link to="/login" className="text-accent hover:text-accent-hover">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
