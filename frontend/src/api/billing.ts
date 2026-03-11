import { rpcGet, rpcPost } from './client';

export interface SubscriptionData {
  id: string;
  user_id: string;
  tier: string;
  start_date: string;
  end_date: string;
  status: string;
}

export interface PaymentData {
  id: string;
  user_id: string;
  amount: number;
  method: string;
  status: string;
  paid_at: string;
  metrics: string | null;
}

export interface BillingMetrics {
  total_paid: number;
  payment_count: number;
  current_tier: string | null;
  subscription_status: string | null;
  next_payment_date: string | null;
}

export const billingApi = {
  /** GET /billing/get_payment_history ?user_id=... */
  getPaymentHistory: (user_id: string) =>
    rpcGet<PaymentData[]>('/billing/get_payment_history', { user_id }),

  /** GET /billing/generate_metrics ?user_id=... */
  getMetrics: (user_id: string) =>
    rpcGet<BillingMetrics>('/billing/generate_metrics', { user_id }),

  /** POST /billing/create_subscription args=[user_id, tier] */
  createSubscription: (user_id: string, tier: string) =>
    rpcPost<{ status: string; subscription_id: string }>('/billing/create_subscription', [user_id, tier]),

  /** POST /billing/cancel_subscription args=[subscription_id] */
  cancelSubscription: (subscription_id: string) =>
    rpcPost('/billing/cancel_subscription', [subscription_id]),
};
