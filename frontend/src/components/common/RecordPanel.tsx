import { format } from 'date-fns';

interface Field {
  label: string;
  value: string;
  mono?: boolean;
}

interface Props {
  title: string;
  fields: Field[];
  icon?: React.ReactNode;
  variant?: 'default' | 'success' | 'warning';
}

const variantStyles = {
  default: 'bg-section border-border',
  success: 'border-border',
  warning: 'border-border',
};

const variantIconColors = {
  default: '',
  success: 'text-confirmed',
  warning: 'text-pending',
};

/** A structured record display used for audit-trail entries, receipts, and legal records. */
export function RecordPanel({ title, fields, icon, variant = 'default' }: Props) {
  return (
    <div className={`rounded border p-4 ${variantStyles[variant]}`}>
      <div className="flex items-center gap-2 mb-3">
        {icon && <span className={variantIconColors[variant]}>{icon}</span>}
        <h4 className="text-sm font-semibold text-primary">{title}</h4>
      </div>
      <dl className="grid grid-cols-1 gap-2">
        {fields.map((f) => (
          <div key={f.label} className="flex flex-wrap gap-x-3">
            <dt className="text-xs text-secondary w-36 shrink-0">{f.label}</dt>
            <dd className={`text-xs text-primary flex-1 ${f.mono ? 'font-mono break-all' : ''}`}>
              {f.value}
            </dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
