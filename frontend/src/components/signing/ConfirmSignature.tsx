/**
 * ConfirmSignature
 * ─────────────────────────────────────────────────────────────────────────────
 * Step 2 of the signing flow: the signer confirms their intent to sign
 * electronically, acknowledging ESIGN Act / UETA requirements.
 *
 * LEGAL: Per ESIGN §101(c)(1) an electronic signature requires affirmative
 * consumer consent. This component satisfies that requirement.
 */
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/common/Button';

interface Props {
  contractName: string;
  versionNumber: number;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmSignature({ contractName, versionNumber, onConfirm, onCancel }: Props) {
  const [intentChecked,    setIntentChecked]    = useState(false);
  const [disclosureChecked, setDisclosureChecked] = useState(false);
  const [typed,            setTyped]            = useState('');

  const CONFIRM_WORD = 'SIGN';
  const ready = intentChecked && disclosureChecked && typed.trim().toUpperCase() === CONFIRM_WORD;

  return (
    <div className="space-y-5">
      <div>
        <h3 className="text-base font-semibold text-primary">Confirm Your Electronic Signature</h3>
        <p className="text-sm text-secondary mt-1">
          You are about to sign <strong>{contractName}</strong> (version {versionNumber}) electronically.
          This action is legally binding and cannot be undone.
        </p>
      </div>

      <div className="rounded-lg bg-amber-50 border border-amber-200 px-4 py-3 text-xs text-amber-800 leading-relaxed">
        By signing electronically you agree that your signature on this document has the same
        legal effect as a handwritten signature under the{' '}
        <Link to="/legal/terms" className="underline">ESIGN Act</Link> and UETA.
      </div>

      <div className="space-y-3">
        <label className="flex items-start gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={intentChecked}
            onChange={(e) => setIntentChecked(e.target.checked)}
            className="mt-0.5 h-4 w-4 rounded border-border accent-accent"
          />
          <span className="text-sm text-secondary">
            I intend to sign this contract version electronically and understand this constitutes
            a legally binding agreement.
          </span>
        </label>

        <label className="flex items-start gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={disclosureChecked}
            onChange={(e) => setDisclosureChecked(e.target.checked)}
            className="mt-0.5 h-4 w-4 rounded border-border accent-accent"
          />
          <span className="text-sm text-secondary">
            I have read and agree to the{' '}
            <Link to="/legal/esignature" className="text-accent hover:underline">E-Sign Disclosure</Link>.
          </span>
        </label>
      </div>

      <div>
        <label className="form-label" htmlFor="confirm-word">
          Type <strong>{CONFIRM_WORD}</strong> to confirm your intent
        </label>
        <input
          id="confirm-word"
          type="text"
          value={typed}
          onChange={(e) => setTyped(e.target.value)}
          className="form-input uppercase tracking-widest"
          placeholder="SIGN"
          maxLength={4}
          autoComplete="off"
        />
      </div>

      <div className="flex gap-3">
        <Button variant="secondary" onClick={onCancel} className="flex-1 justify-center">
          Cancel
        </Button>
        <Button
          variant="primary"
          onClick={onConfirm}
          disabled={!ready}
          className="flex-1 justify-center"
        >
          Confirm &amp; Continue
        </Button>
      </div>
    </div>
  );
}
