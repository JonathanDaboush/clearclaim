/**
 * TanStack Query hooks for notifications.
 *
 * Provides automatic polling so the notification badge updates without
 * requiring explicit refreshes.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { notificationsApi, type NotificationData } from '@/api/notifications';

export const notificationKeys = {
  all:     () => ['notifications'] as const,
  forUser: (userId: string) => ['notifications', 'user', userId] as const,
};

export function useNotifications(userId: string) {
  return useQuery<NotificationData[]>({
    queryKey: notificationKeys.forUser(userId),
    queryFn:  () => notificationsApi.getAll(userId),
    enabled:  !!userId,
    staleTime: 10_000,
    refetchInterval: 30_000,  // poll every 30 s for new notifications
  });
}

export function useUnreadCount(userId: string) {
  const { data } = useNotifications(userId);
  return data?.filter((n) => !n.is_read).length ?? 0;
}

export function useMarkNotificationRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ notificationId }: { notificationId: string; userId: string }) =>
      notificationsApi.markRead(notificationId),
    // Optimistic update: flip is_read immediately in the cache
    onMutate: async ({ notificationId, userId }) => {
      await queryClient.cancelQueries({ queryKey: notificationKeys.forUser(userId) });
      const previous = queryClient.getQueryData<NotificationData[]>(
        notificationKeys.forUser(userId),
      );
      queryClient.setQueryData<NotificationData[]>(
        notificationKeys.forUser(userId),
        (old) => old?.map((n) => (n.id === notificationId ? { ...n, is_read: true } : n)),
      );
      return { previous };
    },
    onError: (_err, { userId }, context) => {
      if (context?.previous) {
        queryClient.setQueryData(notificationKeys.forUser(userId), context.previous);
      }
    },
    onSettled: (_data, _err, { userId }) => {
      queryClient.invalidateQueries({ queryKey: notificationKeys.forUser(userId) });
    },
  });
}
