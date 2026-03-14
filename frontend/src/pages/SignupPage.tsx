import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { authApi } from '@/api/auth';
import { Button } from '@/components/common/Button';

type Phase = 'form' | 'totp_setup';

export default function SignupPage() {
  const navigate = useNavigate();
  const [phase,       setPhase]       = useState<Phase>('form');
  const [email,       setEmail]       = useState('');
  const [password,    setPassword]    = useState('');
  const [password2,   setPassword2]   = useState('');
  const [totpSecret,  setTotpSecret]  = useState('');
  const [totpConfirm, setTotpConfirm] = useState('');
  const [tosAccepted, setTosAccepted] = useState(false);
  const [error,       setError]       = useState('');
  const [userId,      setUserId]      = useState('');

  const signupMutation = useMutation({
    mutationFn: () => authApi.signup(email, password),
    onSuccess: (res) => {
      if (res.status !== 'User created' || !res.user_id) {
        setError(res.message ?? 'Registration failed.');
        return;
      }
      setUserId(res.user_id!);
      setTotpSecret(res.totp_secret ?? '');
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
    if (!tosAccepted) return 'You must accept the Terms of Service and E-Sign Disclosure to continue.';
    return '';
  };

  const handleSubmit = () => {
    const err = validate();
    if (err) { setError(err); return; }
    signupMutation.mutate();
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

                <label className="flex items-start gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={tosAccepted}
                    onChange={(e) => setTosAccepted(e.target.checked)}
                    className="mt-0.5 h-4 w-4 rounded border-border accent-accent"
                  />
                  <span className="text-xs text-secondary leading-relaxed">
                    I agree to the{' '}
                    <Link to="/legal/terms" className="text-accent hover:underline">Terms of Service</Link>
                    {' '}and{' '}
                    <Link to="/legal/esignature" className="text-accent hover:underline">E-Sign Disclosure</Link>.
                    I understand that my electronic signature has the same legal effect as a handwritten signature
                    under ESIGN and UETA.
                  </span>
                </label>

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
                  Add the key below manually into Google Authenticator, Authy, or any TOTP-compatible app.
                </p>

                {totpSecret && (
                  <div className="flex flex-col items-center gap-2 py-2">
                    <p className="text-xs text-meta">Manual entry key (never share this):</p>
                    <code className="record-box block w-full text-center px-4 py-3 select-all text-sm break-all">{totpSecret}</code>
                  </div>
                )}

                <div className="space-y-1">
                  <label className="form-label" htmlFor="totp-confirm">
                    Enter the 6-digit code from your app to confirm setup
                  </label>
                  <input
                    id="totp-confirm"
                    type="text"
                    inputMode="numeric"
                    maxLength={6}
                    value={totpConfirm}
                    onChange={(e) => { setTotpConfirm(e.target.value.replace(/\D/g, '')); setError(''); }}
                    className="form-input tracking-widest text-center text-lg"
                    placeholder="000000"
                    autoComplete="one-time-code"
                  />
                </div>

                <div className="legal-notice text-xs">
                  Keep your authenticator app accessible. It is required for every login and
                  every contract signing. If you lose access, account recovery requires
                  identity verification.
                </div>

                {error && <p className="form-error">{error}</p>}

                <Button
                  variant="primary"
                  className="w-full justify-center"
                  disabled={totpConfirm.length !== 6}
                  onClick={() => {
                    authApi.verifyTotp(userId, totpSecret, totpConfirm).then((result) => {
                      if (result?.valid) {
                        navigate('/login', { state: { enrolled: true } });
                      } else {
                        setError('Code did not match. Check your app and try again.');
                        setTotpConfirm('');
                      }
                    }).catch(() => setError('Verification failed. Try again.'));
                  }}
                >
                  Confirm and Continue to Login
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
