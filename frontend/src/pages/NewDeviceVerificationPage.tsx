import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { authApi } from '@/api/auth';
import { useAuthStore } from '@/stores/authStore';
import { toast } from 'react-toastify';
import { format } from 'date-fns';

export default function NewDeviceVerificationPage() {
  const navigate       = useNavigate();
  const { session }    = useAuthStore();
  const [done, setDone] = useState(false);

  // Device fingerprint for current browser/OS
  const deviceInfo = {
    browser: navigator.userAgent,
    platform: navigator.platform,
    language: navigator.language,
    timestamp: new Date().toISOString(),
  };

  const approveMutation = useMutation({
    mutationFn: async () => {
      if (!session?.user_id) throw new Error('Not authenticated');
      const result = await authApi.addDevice(session.user_id, JSON.stringify(deviceInfo));
      if (result.device_id) {
        await authApi.verifyNewDevice(session.user_id, result.device_id);
      }
    },
    onSuccess: () => {
      toast.success('Device approved and verified.');
      setDone(true);
    },
    onError: (err: Error) => {
      toast.error(err.message || 'Failed to approve device.');
    },
  });

  if (done) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="card max-w-sm w-full text-center p-8 space-y-4">
          <div className="w-12 h-12 rounded-full bg-[color-mix(in_srgb,#4F8A6F_15%,#fff)] flex items-center justify-center mx-auto">
            <svg className="w-6 h-6 text-confirmed" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-lg font-semibold text-primary">Device Approved</h2>
          <p className="text-sm text-secondary">
            This device has been added to your trusted devices list.
          </p>
          <button className="btn-primary w-full" onClick={() => navigate('/dashboard')}>
            Continue to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="card max-w-md w-full">
        {/* Header */}
        <div className="card-header flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-[color-mix(in_srgb,#C89B3C_15%,#fff)] flex items-center justify-center shrink-0">
            <svg className="w-5 h-5 text-pending" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <div>
            <h1 className="text-base font-semibold text-primary">New Device Detected</h1>
            <p className="text-xs text-meta">A sign-in attempt from an unrecognized device</p>
          </div>
        </div>

        <div className="card-body space-y-5">
          {/* Device details */}
          <div className="space-y-2">
            <p className="text-xs font-semibold text-secondary uppercase tracking-wider">Device Info</p>
            <div className="bg-section rounded-lg p-3 space-y-1.5 text-xs text-secondary">
              <p><span className="text-meta">Platform:</span> {deviceInfo.platform || 'Unknown'}</p>
              <p><span className="text-meta">Language:</span> {deviceInfo.language}</p>
              <p>
                <span className="text-meta">Timestamp:</span>{' '}
                {format(new Date(deviceInfo.timestamp), 'dd MMM yyyy, HH:mm:ss')}
              </p>
              <p className="truncate">
                <span className="text-meta">User Agent:</span> {navigator.userAgent.slice(0, 60)}…
              </p>
            </div>
          </div>

          {/* Security note */}
          <div className="rounded-lg border border-border-strong bg-section p-3 text-xs text-secondary leading-relaxed">
            <strong className="text-primary">Approve this device?</strong> If this sign-in was you,
            click <em>Approve</em> to register this device as trusted. If not, click{' '}
            <em>Deny</em> to block it and secure your account.
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-1">
            <button
              className="btn-primary flex-1"
              disabled={approveMutation.isPending}
              onClick={() => approveMutation.mutate()}
            >
              {approveMutation.isPending ? 'Approving…' : 'Approve Device'}
            </button>
            <button
              className="btn-secondary flex-1"
              disabled={approveMutation.isPending}
              onClick={() => navigate('/login')}
            >
              Deny
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
