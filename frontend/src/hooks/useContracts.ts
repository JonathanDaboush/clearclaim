/**
 * TanStack Query hooks for contracts.
 *
 * These replace manual useEffect/useState patterns with automatic caching,
 * background revalidation, and optimistic updates.
 */
import {
  useQuery,
  useMutation,
  useQueryClient,
  type UseQueryOptions,
} from '@tanstack/react-query';
import { contractsApi, type ContractData, type ContractVersionData } from '@/api/contracts';

// ── Query keys ────────────────────────────────────────────────────────────────

export const contractKeys = {
  all:         () => ['contracts'] as const,
  byProject:   (projectId: string) => ['contracts', 'project', projectId] as const,
  detail:      (contractId: string) => ['contracts', 'detail', contractId] as const,
  versions:    (contractId: string) => ['contracts', 'versions', contractId] as const,
  state:       (contractId: string) => ['contracts', 'state', contractId] as const,
  signatures:  (versionId: string)  => ['contracts', 'signatures', versionId] as const,
};

// ── Query hooks ───────────────────────────────────────────────────────────────

export function useContract(
  contractId: string,
  options?: Omit<UseQueryOptions<ContractData>, 'queryKey' | 'queryFn'>,
) {
  return useQuery<ContractData>({
    queryKey: contractKeys.detail(contractId),
    queryFn:  () => contractsApi.get(contractId),
    enabled:  !!contractId,
    staleTime: 30_000,
    ...options,
  });
}

export function useProjectContracts(projectId: string) {
  return useQuery<ContractData[]>({
    queryKey: contractKeys.byProject(projectId),
    queryFn:  () => contractsApi.getProjectContracts(projectId),
    enabled:  !!projectId,
    staleTime: 30_000,
  });
}

export function useContractVersions(contractId: string) {
  return useQuery<ContractVersionData[]>({
    queryKey: contractKeys.versions(contractId),
    queryFn:  () => contractsApi.getVersions(contractId),
    enabled:  !!contractId,
    staleTime: 15_000,
  });
}

export function useContractState(contractId: string) {
  return useQuery<string>({
    queryKey: contractKeys.state(contractId),
    queryFn:  () => contractsApi.getState(contractId),
    enabled:  !!contractId,
    staleTime: 10_000,
    refetchInterval: 30_000, // poll for state changes while the page is open
  });
}

// ── Mutation hooks ────────────────────────────────────────────────────────────

export function useCreateContract() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      projectId,
      createdBy,
      content,
      name,
    }: {
      projectId: string;
      createdBy: string;
      content: string;
      name?: string;
    }) => contractsApi.create(projectId, createdBy, content, name),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: contractKeys.byProject(variables.projectId) });
    },
  });
}

export function useReviseContract() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      contractId,
      newContent,
      userId,
    }: {
      contractId: string;
      newContent: string;
      userId: string;
    }) => contractsApi.revise(contractId, newContent, userId),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: contractKeys.versions(variables.contractId) });
      queryClient.invalidateQueries({ queryKey: contractKeys.state(variables.contractId) });
    },
  });
}

export function useApproveRevision() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      contractId,
      versionId,
      userId,
    }: {
      contractId: string;
      versionId: string;
      userId: string;
    }) => contractsApi.approveRevision(versionId, userId),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: contractKeys.versions(variables.contractId) });
    },
  });
}

export function useActivateVersion() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      contractId,
      versionId,
    }: {
      contractId: string;
      versionId: string;
    }) => contractsApi.activateVersion(contractId, versionId),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: contractKeys.detail(variables.contractId) });
      queryClient.invalidateQueries({ queryKey: contractKeys.state(variables.contractId) });
    },
  });
}

export function useTransitionContractState() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      contractId,
      newState,
    }: {
      contractId: string;
      newState: string;
    }) => contractsApi.transitionState(contractId, newState),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: contractKeys.state(variables.contractId) });
      queryClient.invalidateQueries({ queryKey: contractKeys.detail(variables.contractId) });
    },
  });
}
