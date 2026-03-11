import { useQuery } from '@tanstack/react-query';
import { billingApi, type PaymentData, type BillingMetrics } from '@/api/billing';
import { useAuthStore } from '@/stores/authStore';
import { format } from 'date-fns';
import { StatusBadge } from '@/components/common/StatusBadge';

function MetricTile({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="card p-5">
      <p className="text-xs text-meta uppercase tracking-wide mb-1">{label}</p>
      <p className="text-2xl font-semibold text-primary">{value}</p>
      {sub && <p className="text-xs text-secondary mt-0.5">{sub}</p>}
    </div>
  );
}

export default function BillingPage() {
  const { session } = useAuthStore();

  const { data: payments = [], isLoading: loadingPayments } = useQuery<PaymentData[]>({
    queryKey: ['payments', session?.user_id],
    queryFn: () => billingApi.getPaymentHistory(session!.user_id),
    enabled: !!session?.user_id,
  });

  const { data: metrics } = useQuery<BillingMetrics>({
    queryKey: ['billing-metrics', session?.user_id],
    queryFn: () => billingApi.getMetrics(session!.user_id),
    enabled: !!session?.user_id,
  });

  const totalPaid = metrics?.total_paid ?? 0;
  const tier = metrics?.current_tier ?? 'guest';
  const subStatus = metrics?.subscription_status ?? 'none';
  const nextPayment = metrics?.next_payment_date ?? null;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Billing &amp; Subscription</h1>
        <p className="page-subtitle">
          Your payment history and subscription details. Guest accounts are free. Business
          accounts pay a monthly subscription based on usage tier.
        </p>
      </div>

      <div className="px-6 pb-10 space-y-6">

        {/* Summary metrics */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <MetricTile
            label="Current Plan"
            value={tier.charAt(0).toUpperCase() + tier.slice(1)}
            sub={subStatus !== 'none' ? `Status: ${subStatus}` : 'No active subscription'}
          />
          <MetricTile
            label="Total Paid"
            value={`$${totalPaid.toFixed(2)}`}
            sub="All time"
          />
          <MetricTile
            label="Payments"
            value={String(metrics?.payment_count ?? 0)}
            sub="Recorded transactions"
          />
          <MetricTile
            label="Next Payment Date"
            value={nextPayment ? format(new Date(nextPayment), 'dd MMM yyyy') : '—'}
            sub={subStatus === 'active' ? 'Subscription renews' : 'No active subscription'}
          />
        </div>

        {/* Pricing model explanation */}
        <div className="legal-notice text-xs space-y-1">
          <p className="font-medium text-primary text-sm">Pricing Model</p>
          <p>• <strong>Guest accounts</strong> are free — no subscription required.</p>
          <p>• <strong>Client / business accounts</strong> pay a monthly subscription based on tier.</p>
          <p>• Workers and participants may be included depending on the subscription tier.</p>
          <p>Each charge is itemised below with a full description of what it covers.</p>
        </div>

        {/* Payment chart */}
        {(payments as PaymentData[]).length > 0 && (() => {
          const recent = [...(payments as PaymentData[])].slice(-8);
          const maxAmt = Math.max(...recent.map((p) => Number(p.amount)), 1);
          const BAR_H = 80;
          const BAR_W = 28;
          const GAP   = 10;
          const totalW = recent.length * (BAR_W + GAP) - GAP;
          return (
            <div className="card">
              <div className="card-header">
                <h2 className="text-sm font-semibold text-primary">Payment Activity</h2>
                <p className="text-xs text-secondary mt-0.5">Last {recent.length} transactions</p>
              </div>
              <div className="card-body">
                <svg
                  role="img"
                  aria-label="Bar chart of recent payment amounts"
                  viewBox={`0 0 ${totalW} ${BAR_H + 24}`}
                  className="w-full max-w-sm"
                  style={{ height: BAR_H + 24 }}
                >
                  {recent.map((p, i) => {
                    const amt  = Number(p.amount);
                    const barH = Math.max(4, Math.round((amt / maxAmt) * BAR_H));
                    const x    = i * (BAR_W + GAP);
                    const y    = BAR_H - barH;
                    return (
                      <g key={p.id}>
                        <rect
                          x={x} y={y} width={BAR_W} height={barH}
                          rx={3}
                          fill={p.status === 'completed' ? '#4F8A6F' : '#C89B3C'}
                          aria-label={`$${amt.toFixed(2)}`}
                        />
                        <text
                          x={x + BAR_W / 2} y={BAR_H + 16}
                          textAnchor="middle"
                          fontSize={9}
                          fill="#7B8A94"
                        >
                          ${amt.toFixed(0)}
                        </text>
                      </g>
                    );
                  })}
                </svg>
                <p className="text-xs text-meta mt-2">Green = completed · Yellow = pending</p>
              </div>
            </div>
          );
        })()}

        {/* Payment history */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-sm font-semibold text-primary">Payment History</h2>
          </div>
          <div className="divide-y divide-border">
            {loadingPayments && (
              <p className="px-5 py-4 text-sm text-secondary">Loading…</p>
            )}
            {!loadingPayments && (payments as PaymentData[]).length === 0 && (
              <p className="px-5 py-8 text-sm text-secondary text-center">No payments recorded.</p>
            )}
            {(payments as PaymentData[]).map((p) => (
              <div key={p.id} className="px-5 py-4 flex items-center gap-4">
                <div className="flex-1">
                  <p className="text-sm font-medium text-primary">
                    ${Number(p.amount).toFixed(2)}{' '}
                    <span className="text-meta font-normal">via {p.method}</span>
                  </p>
                  <p className="text-xs text-meta mt-0.5">
                    {format(new Date(p.paid_at), 'dd MMM yyyy, HH:mm')}
                  </p>
                  {p.metrics && (
                    <p className="text-xs text-secondary mt-0.5 font-mono break-all">{p.metrics}</p>
                  )}
                </div>
                <StatusBadge status={p.status === 'completed' ? 'verified' : 'pending'} />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
