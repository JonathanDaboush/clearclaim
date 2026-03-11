import { rpcGet, rpcPost } from './client';

export interface NotificationData {
  id: string;
  user_id: string;
  type: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export const notificationsApi = {
  /** GET /notification/get_user_notifications ?user_id=... */
  getAll: (user_id: string) =>
    rpcGet<NotificationData[]>('/notification/get_user_notifications', { user_id }),

  /** POST /notification/mark_read args=[notification_id] */
  markRead: (notification_id: string) =>
    rpcPost('/notification/mark_read', [notification_id]),
};
