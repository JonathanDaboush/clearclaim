import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { notificationsApi, type NotificationData } from '@/api/notifications';
import { projectsApi } from '@/api/projects';
import { billingApi } from '@/api/billing';
import { useAuthStore } from '@/stores/authStore';
import { format } from 'date-fns';

export default function DashboardPage() {
  const { session } = useAuthStore();

  const { data: notifications = [] } = useQuery<NotificationData[]>({
    queryKey: ['notifications', session?.user_id],
    queryFn: () => notificationsApi.getAll(session!.user_id),
    enabled: !!session?.user_id,
  });

  const { data: projects = [] } = useQuery({
    queryKey: ['user-projects', session?.user_id],
    queryFn: () => projectsApi.getUserProjects(session!.user_id),
    enabled: !!session?.user_id,
  });

  const { data: billingMetrics } = useQuery({
    queryKey: ['billing-metrics', session?.user_id],
    queryFn: () => billingApi.getMetrics(session!.user_id),
    enabled: !!session?.user_id,
  });

  const unread = notifications.filter((n) => !n.is_read);
  const securityAlerts = notifications.filter(
    (n) => !n.is_read && ['new_device', 'security_alert', 'identity_check'].includes(n.type)
  );
  const pendingSignatures = notifications.filter(
    (n) => !n.is_read && n.type === 'signature_required'
  );
  const billingWarning =
    billingMetrics?.subscription_status &&
    !['active', 'trialing'].includes(billingMetrics.subscription_status)
      ? billingMetrics.subscription_status
      : null;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Welcome back, {session?.email}</p>
      </div>
      <div className="px-6 space-y-6 pb-10">
        {session?.verification_status !== 'verified' && (
          <div className="legal-notice flex items-start gap-3">
            <svg className="w-4 h-4 mt-0.5 shrink-0 text-pending" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div>
              <p className="font-medium text-sm text-primary">Identity not verified</p>
              <p className="text-xs mt-0.5 text-secondary">
                Government ID verification increases the legal assurance of your agreements.{' '}
                <Link to="/account" className="text-accent hover:text-accent-hover">Verify now</Link>
              </p>
            </div>
          </div>
        )}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <StatCard label="Projects" value={String(projects.length)} icon="folder" link="/projects" linkLabel="View" />
          <StatCard label="Pending Signatures" value={String(pendingSignatures.length)} icon="pen" link="/notifications" linkLabel="View" highlight={pendingSignatures.length > 0} />
          <StatCard label="Notifications" value={String(unread.length)} icon="bell" link="/notifications" linkLabel="View" highlight={unread.length > 0} />
          <StatCard label="Identity" value={session?.verification_status === 'verified' ? 'Verified' : 'Unverified'} icon="shield" link="/account" linkLabel="Manage" />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <section className="card">
            <div className="card-header flex items-center justify-between">
              <h2 className="text-sm font-semibold text-primary">Pending Signatures</h2>
              <Link to="/notifications" className="text-xs text-accent hover:text-accent-hover">View all</Link>
            </div>
            {pendingSignatures.length === 0 ? (
              <div className="card-body py-6 text-center"><p className="text-xs text-meta">No contracts awaiting your signature.</p></div>
            ) : (
              <div className="divide-y divide-border">
                {pendingSignatures.slice(0, 5).map((n) => (
                  <div key={n.id} className="px-5 py-3">
                    <p className="text-sm font-medium text-primary">{n.message}</p>
                    <p className="text-xs text-meta mt-1">{format(new Date(n.created_at), 'dd MMM yyyy, HH:mm')}</p>
                  </div>
                ))}
              </div>
            )}
          </section>
          <section className="card">
            <div className="card-header flex items-center justify-between">
              <h2 className="text-sm font-semibold text-primary">Security Alerts</h2>
              <Link to="/security-alerts" className="text-xs text-accent hover:text-accent-hover">Review &amp; act</Link>
            </div>
            {securityAlerts.length === 0 ? (
              <div className="card-body py-6 text-center"><p className="text-xs text-meta">No security alerts.</p></div>
            ) : (
              <div className="divide-y divide-border">
                {securityAlerts.slice(0, 5).map((n) => (
                  <div key={n.id} className="px-5 py-3">
                    <p className="text-sm text-primary">{n.message}</p>
                    <p className="text-xs text-meta mt-0.5">{format(new Date(n.created_at), 'dd MMM yyyy, HH:mm')}</p>
                  </div>
                ))}
              </div>
            )}
          </section>
          <section className="card">
            <div className="card-header flex items-center justify-between">
              <h2 className="text-sm font-semibold text-primary">Recent Evidence</h2>
              <Link to="/evidence" className="text-xs text-accent hover:text-accent-hover">Evidence library</Link>
            </div>
            <div className="card-body py-6 text-center">
              <p className="text-xs text-meta">Open a project to view and upload evidence.</p>
              <Link to="/projects" className="text-xs text-accent hover:text-accent-hover mt-1 inline-block">Go to Projects</Link>
            </div>
          </section>
          <section className="card">
            <div className="card-header flex items-center justify-between">
              <h2 className="text-sm font-semibold text-primary">Billing</h2>
              <Link to="/billing" className="text-xs text-accent hover:text-accent-hover">Manage</Link>
            </div>
            <div className="card-body space-y-3">
              {billingMetrics ? (
                <>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-meta">Plan</span>
                    <span className="font-medium text-primary capitalize">{billingMetrics.current_tier ?? 'Free'}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-meta">Status</span>
                    <span className={billingMetrics.subscription_status === 'active' ? 'text-xs px-2 py-0.5 rounded font-medium bg-green-50 text-confirmed' : 'text-xs px-2 py-0.5 rounded font-medium bg-yellow-50 text-pending'}>
                      {billingMetrics.subscription_status ?? 'inactive'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-meta">Total paid</span>
                    <span className="font-medium text-primary">${(billingMetrics.total_paid / 100).toFixed(2)}</span>
                  </div>
                  {billingWarning && (
                    <div className="legal-notice text-xs">
                      Subscription is <strong>{billingWarning}</strong>.{' '}
                      <Link to="/billing" className="text-accent hover:text-accent-hover">Renew now</Link>
                    </div>
                  )}
                </>
              ) : (
                <p className="text-xs text-meta py-4 text-center">Loading billing info...</p>
              )}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, icon, link, linkLabel, highlight }: {
  label: string; value?: string; icon: string; link: string; linkLabel: string; highlight?: boolean;
}) {
  const icons: Record<string, React.ReactNode> = {
    folder: (
      <svg className="w-4 h-4 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7a2 2 0 012-2h4l2 2h8a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2V7z" />
      </svg>
    ),
    pen: (
      <svg className="w-4 h-4 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
      </svg>
    ),
    bell: (
      <svg className="w-4 h-4 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
      </svg>
    ),
    shield: (
      <svg className="w-4 h-4 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
      </svg>
    ),
  };
  return (
    <div className={'card' + (highlight ? ' border-pending' : '')}>
      <div className="card-body flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-accent-light flex items-center justify-center shrink-0">
          {icons[icon]}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-xs text-meta">{label}</p>
          {value !== undefined && <p className={'text-sm font-semibold ' + (highlight ? 'text-pending' : 'text-primary')}>{value}</p>}
        </div>
        <Link to={link} className="text-xs text-accent hover:text-accent-hover whitespace-nowrap">{linkLabel}</Link>
      </div>
    </div>
  );
}
