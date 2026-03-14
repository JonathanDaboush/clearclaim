import { useState } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { authApi } from '@/api/auth';
import { useAuthStore, type Session } from '@/stores/authStore';
import { Button } from '@/components/common/Button';

type Phase = 'credentials' | 'totp';

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const enrolled = (location.state as { enrolled?: boolean } | null)?.enrolled ?? false;
  const { setSession } = useAuthStore();
  const [phase,       setPhase]       = useState<Phase>('credentials');
  const [email,       setEmail]       = useState('');
  const [password,    setPassword]    = useState('');
  const [totpCode,    setTotpCode]    = useState('');
  const [pendingData, setPendingData] = useState<{ user_id: string; totp_secret: string; verification_status: string } | null>(null);
  const [error,       setError]       = useState('');

  const loginMutation = useMutation({
    mutationFn: () => authApi.login(email, password),
    onSuccess: (res) => {
      if (res.status === 'error' || !res.user_id) {
        setError(res.message ?? 'Invalid email or password.');
        return;
      }
      setPendingData({
        user_id: res.user_id!,
        totp_secret: res.totp_secret ?? '',
        verification_status: res.verification_status ?? 'unverified',
      });
      setPhase('totp');
      setError('');
    },
    onError: () => setError('Invalid email or password.'),
  });

  const totpMutation = useMutation({
    mutationFn: () =>
      authApi.verifyTotp(pendingData!.user_id, pendingData!.totp_secret, totpCode),
    onSuccess: (valid) => {
      if (!valid?.valid) {
        setError('Authentication code invalid or expired.');
        return;
      }
      const s: Session = {
        user_id: pendingData!.user_id,
        email,
        totp_secret: pendingData!.totp_secret,
        device_id: '',
        verification_status: pendingData!.verification_status,
        access_token: valid.access_token ?? '',
        refresh_token: valid.refresh_token ?? '',
        expires_at: Date.now() + (valid.expires_in ?? 900) * 1000,
      };
      setSession(s);
      navigate('/dashboard');
    },
    onError: () => setError('Authentication code invalid or expired.'),
  });

  return (
    <div className="min-h-screen bg-bg flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        {/* Brand */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-10 h-10 rounded-lg bg-accent mb-3">
            <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
            </svg>
          </div>
          <h1 className="text-xl font-semibold text-primary">ClearClaim</h1>
          <p className="text-sm text-secondary mt-1">Legal Agreement Platform</p>
        </div>

        {enrolled && (
          <div className="mb-4 rounded-lg bg-green-50 border border-green-200 px-4 py-3 text-sm text-green-800">
            Authenticator enrolled successfully. Sign in below.
          </div>
        )}

        <div className="card">
          <div className="card-body space-y-5">
            {phase === 'credentials' ? (
              <>
                <h2 className="text-base font-semibold text-primary">Sign In</h2>

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
                  />
                </div>

                <div>
                  <label className="form-label" htmlFor="password">Password</label>
                  <input
                    id="password"
                    type="password"
                    autoComplete="current-password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="form-input"
                    onKeyDown={(e) => e.key === 'Enter' && loginMutation.mutate()}
                  />
                </div>

                {error && <p className="form-error">{error}</p>}

                <Button
                  variant="primary"
                  className="w-full justify-center"
                  loading={loginMutation.isPending}
                  onClick={() => loginMutation.mutate()}
                >
                  Continue
                </Button>
              </>
            ) : (
              <>
                <h2 className="text-base font-semibold text-primary">Two-Factor Authentication</h2>
                <p className="text-sm text-secondary">
                  Open your authenticator app and enter the current 6-digit code.
                </p>

                <div>
                  <label className="form-label" htmlFor="totp">Authenticator Code</label>
                  <input
                    id="totp"
                    type="text"
                    inputMode="numeric"
                    maxLength={6}
                    autoComplete="one-time-code"
                    value={totpCode}
                    onChange={(e) => setTotpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    className="form-input text-center text-2xl tracking-widest font-mono"
                    autoFocus
                  />
                </div>

                {error && <p className="form-error">{error}</p>}

                <Button
                  variant="primary"
                  className="w-full justify-center"
                  loading={totpMutation.isPending}
                  disabled={totpCode.length !== 6}
                  onClick={() => totpMutation.mutate()}
                >
                  Verify &amp; Sign In
                </Button>

                <button
                  onClick={() => { setPhase('credentials'); setError(''); }}
                  className="block w-full text-center text-xs text-accent hover:text-accent-hover"
                >
                  ← Back
                </button>
              </>
            )}
          </div>
        </div>

        <p className="text-center text-xs text-meta mt-6">
          Don't have an account?{' '}
          <Link to="/signup" className="text-accent hover:text-accent-hover">Create one</Link>
        </p>
        <p className="text-center text-xs text-meta mt-2">
          <Link to="/forgot-password" className="text-accent hover:text-accent-hover">Forgot your password?</Link>
        </p>
      </div>
    </div>
  );
}
