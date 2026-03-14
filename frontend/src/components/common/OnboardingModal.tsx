import { useState } from 'react';

interface Step {
  title: string;
  description: string;
  icon: string; // svg path d=
  action?: string;
}

const STEPS: Step[] = [
  {
    title: 'Create a project',
    description:
      'Projects are the top-level containers for your agreements, evidence, and parties. Start by giving your project a name — e.g. "Service Agreement Q3".',
    icon: 'M3 7a2 2 0 012-2h14a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2-2V7zm4 0v10m10-10v10M9 7h6',
    action: 'Create a project with the "+ New Project" button above.',
  },
  {
    title: 'Draft your agreement',
    description:
      'Inside a project you can create contracts. Write your terms directly in the editor — every revision is version-controlled and cryptographically linked to the previous one.',
    icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    action: 'Open a project → New Contract.',
  },
  {
    title: 'Invite a collaborator',
    description:
      'Add the other party or a legal rep to your project. They will receive a notification and need to verify their identity before they can sign anything.',
    icon: 'M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z',
    action: 'Project → Members → Invite.',
  },
  {
    title: 'Upload evidence',
    description:
      'Attach supporting documents, photos, or files to any contract version. Uploaded files are stored immutably and included in the signed audit chain.',
    icon: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12',
    action: 'Contract → Evidence → Upload File.',
  },
  {
    title: 'Sign the contract',
    description:
      'When all parties are ready, each signer authenticates with their TOTP code. ClearClaim records a tamper-evident signature snapshot with a full audit certificate.',
    icon: 'M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z',
    action: 'Contract → Sign → Verify with your authenticator app.',
  },
];

interface Props {
  onClose: () => void;
}

export function OnboardingModal({ onClose }: Props) {
  const [step, setStep] = useState(0);
  const current = STEPS[step];
  const isLast = step === STEPS.length - 1;
  const progress = ((step + 1) / STEPS.length) * 100;

  function dismiss() {
    localStorage.setItem('cc_onboarding_done', '1');
    onClose();
  }

  return (
    /* Backdrop */
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
      role="dialog"
      aria-modal="true"
      aria-label="Getting started"
    >
      <div className="relative w-full max-w-lg bg-card rounded-2xl shadow-2xl border border-border overflow-hidden">
        {/* Progress bar */}
        <div className="h-1 bg-border">
          <div
            className="h-full bg-accent transition-all duration-300"
            style={{ width: `${progress}%` }}
            aria-hidden="true"
          />
        </div>

        {/* Header */}
        <div className="flex items-center justify-between px-6 pt-5 pb-2">
          <p className="text-xs font-medium text-meta uppercase tracking-wide">
            Step {step + 1} of {STEPS.length}
          </p>
          <button
            onClick={dismiss}
            className="text-meta hover:text-secondary transition-colors p-1 -mr-1"
            aria-label="Close"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="px-6 pb-6 pt-2 text-center">
          {/* Icon */}
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-accent/10 border border-accent/20">
            <svg className="w-7 h-7 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={current.icon} />
            </svg>
          </div>

          <h2 className="text-lg font-semibold text-primary mb-2">{current.title}</h2>
          <p className="text-sm text-secondary leading-relaxed">{current.description}</p>

          {current.action && (
            <div className="mt-4 rounded-lg bg-section border border-border px-4 py-3 text-left">
              <p className="text-xs text-meta font-medium uppercase tracking-wide mb-0.5">How to do it</p>
              <p className="text-sm text-primary">{current.action}</p>
            </div>
          )}
        </div>

        {/* Step dots */}
        <div className="flex justify-center gap-1.5 pb-4">
          {STEPS.map((_, i) => (
            <button
              key={i}
              onClick={() => setStep(i)}
              className={`h-1.5 rounded-full transition-all ${
                i === step ? 'w-5 bg-accent' : 'w-1.5 bg-border'
              }`}
              aria-label={`Go to step ${i + 1}`}
            />
          ))}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-6 pb-6 gap-3">
          <button
            onClick={() => setStep((s) => s - 1)}
            disabled={step === 0}
            className="text-sm text-meta hover:text-secondary disabled:invisible transition-colors"
          >
            ← Back
          </button>

          <div className="flex gap-2">
            <button
              onClick={dismiss}
              className="text-sm text-meta hover:text-secondary transition-colors px-3 py-1.5"
            >
              Skip tour
            </button>
            {isLast ? (
              <button
                onClick={dismiss}
                className="btn-primary text-sm px-4 py-1.5"
              >
                Get started
              </button>
            ) : (
              <button
                onClick={() => setStep((s) => s + 1)}
                className="btn-primary text-sm px-4 py-1.5"
              >
                Next →
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
