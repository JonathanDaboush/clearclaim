/**
 * TanStack Query hooks for signing.
 *
 * Includes an optimistic update pattern for the signing action so the UI
 * shows the signature immediately while the server confirms in the background.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { signingApi, type SignatureData } from '@/api/signing';
import { contractKeys } from './useContracts';

export const signingKeys = {
  signatures: (versionId: string) => ['signing', 'signatures', versionId] as const,
};

export function useContractSignatures(versionId: string) {
  return useQuery<SignatureData[]>({
    queryKey: signingKeys.signatures(versionId),
    queryFn:  () => signingApi.getSignatures(versionId),
    enabled:  !!versionId,
    staleTime: 10_000,
  });
}

export function useSignContract() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      versionId,
      userId,
      deviceId,
      totpSecret,
      totpCode,
      idempotencyKey,
    }: {
      versionId: string;
      contractId: string;
      userId: string;
      deviceId: string;
      totpSecret?: string;
      totpCode?: string;
      idempotencyKey?: string;
    }) =>
      signingApi.sign(versionId, userId, deviceId, totpSecret, totpCode, idempotencyKey),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: signingKeys.signatures(variables.versionId) });
      queryClient.invalidateQueries({ queryKey: contractKeys.state(variables.contractId) });
      queryClient.invalidateQueries({ queryKey: contractKeys.detail(variables.contractId) });
    },
  });
}
