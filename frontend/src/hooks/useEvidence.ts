/**
 * TanStack Query hooks for evidence.
 *
 * Covers the full evidence lifecycle: upload, approval, and chain-of-custody
 * data needed for legal disputes.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { evidenceApi, type EvidenceData } from '@/api/evidence';

export const evidenceKeys = {
  all:         () => ['evidence'] as const,
  forContract: (contractId: string) => ['evidence', 'contract', contractId] as const,
  forUser:     (userId: string) => ['evidence', 'user', userId] as const,
};

export function useContractEvidence(contractId: string) {
  return useQuery<EvidenceData[]>({
    queryKey: evidenceKeys.forContract(contractId),
    queryFn:  () => evidenceApi.getContractEvidence(contractId),
    enabled:  !!contractId,
    staleTime: 30_000,
  });
}

export function useUserEvidence(userId: string) {
  return useQuery<EvidenceData[]>({
    queryKey: evidenceKeys.forUser(userId),
    queryFn:  () => evidenceApi.getAll(userId),
    enabled:  !!userId,
    staleTime: 30_000,
  });
}

export function useUploadEvidence() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      contractId,
      fileUrl,
      fileType,
      fileSize,
      addedBy,
      fileBytes,
    }: {
      contractId: string;
      fileUrl: string;
      fileType: string;
      fileSize: number;
      addedBy: string;
      fileBytes?: string;
    }) => evidenceApi.upload(contractId, fileUrl, fileType, fileSize, addedBy, fileBytes),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: evidenceKeys.forContract(variables.contractId) });
      queryClient.invalidateQueries({ queryKey: evidenceKeys.forUser(variables.addedBy) });
    },
  });
}

export function useApproveEvidence() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      evidenceId,
      userId,
      contractId,
    }: {
      evidenceId: string;
      userId: string;
      contractId: string;
    }) => evidenceApi.approve(evidenceId, userId),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: evidenceKeys.forContract(variables.contractId) });
    },
  });
}

export function useRequestEvidenceDeletion() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      evidenceId,
      userId,
      contractId,
    }: {
      evidenceId: string;
      userId: string;
      contractId: string;
    }) => evidenceApi.requestDeletion(evidenceId, userId),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: evidenceKeys.forContract(variables.contractId) });
    },
  });
}
