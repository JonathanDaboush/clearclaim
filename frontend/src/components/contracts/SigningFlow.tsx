import { useState } from 'react';
import { format } from 'date-fns';
import { useMutation } from '@tanstack/react-query';
import { signingApi } from '@/api/signing';
import { ContractViewer } from './ContractViewer';
import { StepIndicator } from '@/components/common/StepIndicator';
import { RecordPanel } from '@/components/common/RecordPanel';
import { Button } from '@/components/common/Button';
import { useAuthStore } from '@/stores/authStore';
import type { ContractVersionData } from '@/api/contracts';

type SigningStep = 'review' | 'confirm_intent' | 'totp' | 'receipt';

const STEPS = [
  { id: 'review',         label: 'Review Contract' },
  { id: 'confirm_intent', label: 'Confirm Intent'  },
  { id: 'totp',           label: 'Authenticate'    },
  { id: 'receipt',        label: 'Receipt'         },
];

interface Props {
  version: ContractVersionData;
  onComplete?: () => void;
  onCancel: () => void;
}

/**
 * SigningFlow
 * â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
 * A deliberate, multi-step signing process that meets ESIGN / UETA / PIPEDA
 * requirements for:
 *  1. Informed consent (user must scroll & confirm they read the contract)
 *  2. Intent to sign  (explicit written confirmation step)
 *  3. Strong authentication (TOTP code required)
 *  4. Auditable receipt   (confirmation ID, signature hash, timestamp shown)
 *
 * No one-click or auto-sign is possible through this component.
 */
export function SigningFlow({ version, onComplete, onCancel }: Props) {
  const { session } = useAuthStore();
  const [step,            setStep]           = useState<SigningStep>('review');
  const [reviewConfirmed, setReviewConfirmed] = useState(false);
  const [intentChecked,   setIntentChecked]  = useState(false);
  const [totpCode,        setTotpCode]       = useState('');
  const [signatureId,     setSignatureId]    = useState('');
  const [signedAt,        setSignedAt]       = useState('');
  const [docHash,         setDocHash]        = useState('');
  const [signingIp,       setSigningIp]      = useState('');
  const [error,           setError]          = useState('');

  const completedSteps = (): string[] => {
    const idx = STEPS.findIndex((s) => s.id === step);
    return STEPS.slice(0, idx).map((s) => s.id);
  };

  // Step 1 â†’ 2: register signing intent
  const requestMutation = useMutation({
    mutationFn: () => signingApi.request(version.id, session!.user_id),
    onSuccess: () => {
      setStep('confirm_intent');
      setError('');
    },
    onError: () => setError('Failed to initiate signing. Please try again.'),
  });

  // Step 3: verify TOTP then immediately sign
  const verifyAndSignMutation = useMutation({
    mutationFn: async () => {
      const ok = await signingApi.verifyTotp(session!.totp_secret, totpCode);
      if (!ok) throw new Error('TOTP verification failed');
      const result = await signingApi.sign(
        version.id,
        session!.user_id,
        session!.device_id || '',
        '',
        session!.totp_secret,
        totpCode
      );
      return result;
    },
    onSuccess: (res) => {
      setSignatureId(res.signature_id);
      setSignedAt(new Date().toISOString());
      if (res.ip) setSigningIp(res.ip);
      // hash the contract content client-side for the receipt display
      const encoder = new TextEncoder();
      const data = encoder.encode(version.content ?? version.id);
      crypto.subtle.digest('SHA-256', data).then((buf) => {
        const hex = Array.from(new Uint8Array(buf)).map((b) => b.toString(16).padStart(2, '0')).join('');
        setDocHash(hex);
      });
      setStep('receipt');
      onComplete?.();
      setError('');
    },
    onError: () => setError('Authentication failed or signing error. Check your TOTP code and try again.'),
  });

  return (
    <div className="max-w-3xl mx-auto py-6 px-4">
      <StepIndicator steps={STEPS} current={step} completed={completedSteps()} />

      {/* â”€â”€ Step 1: Review â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      {step === 'review' && (
        <div>
          <div className="legal-notice mb-5">
            <strong>Legal Notice:</strong> You are about to sign a legally binding agreement.
            Read the entire document carefully. Signing constitutes your formal consent and
            cannot be undone unilaterally.
          </div>

          <ContractViewer
            version={version}
            enforceReview
            onReviewConfirmed={() => setReviewConfirmed(true)}
          />

          <div className="flex justify-between mt-5">
            <Button variant="ghost" onClick={onCancel}>Cancel</Button>
            <Button
              variant="primary"
              disabled={!reviewConfirmed}
              loading={requestMutation.isPending}
              onClick={() => requestMutation.mutate()}
            >
              I Have Reviewed â€” Continue to Confirm Intent
            </Button>
          </div>
          {error && <p className="text-xs text-disputed mt-2">{error}</p>}
        </div>
      )}

      {/* â”€â”€ Step 2: Confirm Intent â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      {step === 'confirm_intent' && (
        <div className="card max-w-lg mx-auto">
          <div className="card-header">
            <h3 className="text-base font-semibold text-primary">Confirm Your Intent to Sign</h3>
          </div>
          <div className="card-body space-y-5">
            <p className="text-sm text-secondary leading-relaxed">
              By continuing, you are confirming that you intend to be legally bound by the
              agreement described in the document you just reviewed (Version {version.version_number}).
            </p>

            <RecordPanel
              title="Document being signed"
              fields={[
                { label: 'Version',     value: `v${version.version_number}` },
                { label: 'Prepared at', value: format(new Date(version.created_at), 'dd MMM yyyy, HH:mm z') },
                { label: 'Contract ID', value: version.contract_id, mono: true },
              ]}
            />

            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={intentChecked}
                onChange={(e) => setIntentChecked(e.target.checked)}
                className="mt-0.5 w-4 h-4 rounded border-border text-accent focus:ring-accent"
              />
              <span className="text-sm text-primary leading-snug">
                I, the undersigned, confirm that I intend to sign the above contract and that I
                understand this action is legally binding.
              </span>
            </label>

            <div className="flex justify-between">
              <Button variant="ghost" onClick={onCancel}>Cancel</Button>
              <Button
                variant="primary"
                disabled={!intentChecked}
                onClick={() => setStep('totp')}
              >
                Continue â€” Enter Authentication Code
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* â”€â”€ Step 3: TOTP Authentication â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      {step === 'totp' && (
        <div className="card max-w-sm mx-auto">
          <div className="card-header">
            <h3 className="text-base font-semibold text-primary">Authenticator Verification</h3>
          </div>
          <div className="card-body space-y-4">
            <p className="text-sm text-secondary">
              Open your authenticator app and enter the current 6-digit code to authorise
              this signature. This code is time-sensitive.
            </p>

            <div>
              <label className="form-label" htmlFor="totp-input">
                Authenticator Code
              </label>
              <input
                id="totp-input"
                type="text"
                inputMode="numeric"
                maxLength={6}
                autoComplete="one-time-code"
                placeholder="000000"
                value={totpCode}
                onChange={(e) => setTotpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                className="form-input text-center text-xl tracking-widest font-mono"
                autoFocus
              />
            </div>

            {error && <p className="text-xs text-disputed">{error}</p>}

            <div className="flex justify-between">
              <Button variant="ghost" onClick={onCancel}>Cancel</Button>
              <Button
                variant="primary"
                disabled={totpCode.length !== 6}
                loading={verifyAndSignMutation.isPending}
                onClick={() => verifyAndSignMutation.mutate()}
              >
                Verify &amp; Sign
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* â”€â”€ Step 4: Receipt â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      {step === 'receipt' && (
        <div className="card max-w-lg mx-auto">
          <div className="card-header">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-confirmed" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <h3 className="text-base font-semibold text-primary">Signature Recorded</h3>
            </div>
          </div>
          <div className="card-body space-y-5">
            <p className="text-sm text-secondary">
              Your signature has been recorded and is now part of the immutable audit record for
              this agreement. You may save or print this receipt as evidence of your signing.
            </p>

            <RecordPanel
              title="Signing Receipt"
              variant="success"
              fields={[
                { label: 'Signature ID',   value: signatureId, mono: true },
                { label: 'Signed by',      value: session?.email ?? session?.user_id ?? '' },
                { label: 'Timestamp',      value: format(new Date(signedAt || Date.now()), 'dd MMM yyyy, HH:mm:ss z') },
                { label: 'Device',         value: session?.device_id ? session.device_id.slice(0, 20) + '…' : 'current device', mono: true },
                { label: 'IP',             value: signingIp || 'recorded server-side' },
                { label: 'Document hash',  value: docHash ? docHash.slice(0, 32) + '…' : 'computing…', mono: true },
                { label: 'Version',        value: `v${version.version_number}` },
              ]}
            />

            <div className="flex gap-2 justify-end">
              <Button variant="secondary" onClick={() => window.print()}>
                Print Receipt
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
