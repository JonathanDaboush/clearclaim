import { clsx } from 'clsx';

interface Step {
  id: string;
  label: string;
}

interface Props {
  steps: Step[];
  current: string;
  completed: string[];
}

export function StepIndicator({ steps, current, completed }: Props) {
  return (
    <div className="flex items-center gap-0 mb-8">
      {steps.map((step, i) => {
        const isDone    = completed.includes(step.id);
        const isCurrent = step.id === current;

        return (
          <div key={step.id} className="flex items-center flex-1 last:flex-none">
            {/* Circle */}
            <div className="flex flex-col items-center">
              <div
                className={clsx(
                  'step-dot',
                  isDone    && 'step-dot-complete',
                  isCurrent && !isDone && 'step-dot-active',
                  !isDone && !isCurrent && 'step-dot-pending'
                )}
              >
                {isDone ? (
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <span>{i + 1}</span>
                )}
              </div>
              <span
                className={clsx(
                  'text-xs mt-1 whitespace-nowrap',
                  isCurrent ? 'text-accent font-semibold' : 'text-meta'
                )}
              >
                {step.label}
              </span>
            </div>

            {/* Connector */}
            {i < steps.length - 1 && (
              <div
                className={clsx(
                  'flex-1 h-px mx-2 mt-[-1rem]',
                  isDone ? 'bg-confirmed' : 'bg-border'
                )}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
