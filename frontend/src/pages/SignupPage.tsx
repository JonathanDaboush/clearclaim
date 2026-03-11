import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { authApi } from '@/api/auth';
import { useAuthStore, type Session } from '@/stores/authStore';
import { Button } from '@/components/common/Button';

type Phase = 'form' | 'totp_setup';

export default function SignupPage() {
  const navigate = useNavigate();
  const { setSession } = useAuthStore();
  const [phase,       setPhase]       = useState<Phase>('form');
  const [email,       setEmail]       = useState('');
  const [password,    setPassword]    = useState('');
  const [password2,   setPassword2]   = useState('');
  const [totpSecret,  setTotpSecret]  = useState('');
  const [userId,      setUserId]      = useState('');
  const [error,       setError]       = useState('');

  const signupMutation = useMutation({
    mutationFn: () => authApi.signup(email, password),
    onSuccess: (res) => {
      if (res.status !== 'User created' || !res.user_id) {
        setError(res.message ?? 'Registration failed.');
        return;
      }
      setUserId(res.user_id!);
      setTotpSecret(res.totp_secret ?? '');
      // Save session so user can skip TOTP on first visit (they can log in with it)
      const s: Session = {
        user_id: res.user_id!,
        email,
        totp_secret: res.totp_secret ?? '',
        device_id: '',
        verification_status: 'unverified',
      };
      setSession(s);
      setPhase('totp_setup');
      setError('');
    },
    onError: () => {
      setError('Registration failed. Please try again.');
    },
  });

  const validate = () => {
    if (!email.includes('@')) return 'Enter a valid email address.';
    if (password.length < 12)  return 'Password must be at least 12 characters.';
    if (password !== password2) return 'Passwords do not match.';
    return '';
  };

  const handleSubmit = () => {
    const err = validate();
    if (err) { setError(err); return; }
    signupMutation.mutate();
  };

  // Generate a TOTP URI using the standard format so any authenticator app can scan it
  const totpUri = totpSecret
    ? `otpauth://totp/ClearClaim:${encodeURIComponent(email)}?secret=${totpSecret}&issuer=ClearClaim`
    : '';

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
          <p className="text-sm text-secondary mt-1">Create Account</p>
        </div>

        <div className="card">
          <div className="card-body space-y-5">
            {phase === 'form' && (
              <>
                <h2 className="text-base font-semibold text-primary">Create Your Account</h2>

                <div>
                  <label className="form-label" htmlFor="email">Email Address</label>
                  <input
                    id="email"
                    type="email"
                    autoComplete="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="form-input"
                  />
                </div>

                <div>
                  <label className="form-label" htmlFor="pw">Password</label>
                  <input
                    id="pw"
                    type="password"
                    autoComplete="new-password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="form-input"
                  />
                  <p className="text-xs text-meta mt-1">Minimum 12 characters</p>
                </div>

                <div>
                  <label className="form-label" htmlFor="pw2">Confirm Password</label>
                  <input
                    id="pw2"
                    type="password"
                    autoComplete="new-password"
                    value={password2}
                    onChange={(e) => setPassword2(e.target.value)}
                    className="form-input"
                    onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
                  />
                </div>

                {error && <p className="form-error">{error}</p>}

                <Button
                  variant="primary"
                  className="w-full justify-center"
                  loading={signupMutation.isPending}
                  onClick={handleSubmit}
                >
                  Create Account
                </Button>
              </>
            )}

            {phase === 'totp_setup' && (
              <>
                <h2 className="text-base font-semibold text-primary">Set Up Authenticator App</h2>
                <p className="text-sm text-secondary leading-relaxed">
                  This platform requires an authenticator app for login and every signing action.
                  Scan the QR code below with Google Authenticator, Authy, or any TOTP-compatible app.
                </p>

                {totpUri && (
                  <div className="flex flex-col items-center gap-3 py-2">
                    <img
                      src={`https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(totpUri)}`}
                      alt="TOTP QR Code â€” scan with authenticator app"
                      className="border border-border rounded p-2"
                      width={180}
                      height={180}
                    />
                    <p className="text-xs text-secondary">Manual entry key:</p>
                    <code className="record-box text-center px-4 py-2 select-all">{totpSecret}</code>
                  </div>
                )}

                <div className="legal-notice text-xs">
                  Keep your authenticator app accessible. It is required for every login and
                  every contract signing. If you lose access, account recovery requires
                  identity verification.
                </div>

                <Button
                  variant="primary"
                  className="w-full justify-center"
                  onClick={() => navigate('/dashboard')}
                >
                  I've Set Up My Authenticator â€” Continue
                </Button>
              </>
            )}
          </div>
        </div>

        <p className="text-center text-xs text-meta mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-accent hover:text-accent-hover">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
