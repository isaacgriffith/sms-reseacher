/**
 * TanStack Query hooks for task execution state polling (feature 010).
 *
 * Provides real-time task node status updates for the execution state view,
 * with configurable refetch intervals.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  approveTask,
  completeTask,
  getExecutionState,
  type CompleteTaskResponse,
  type ExecutionStateResponse,
} from '../../services/protocols/protocolsApi';

/**
 * Query hook for a study's full protocol execution state.
 *
 * Polls every 5 seconds while any task is ACTIVE. Stops polling when all
 * tasks are COMPLETE, SKIPPED, or the task list is empty.
 *
 * @param studyId - The integer study ID. Pass 0 to disable.
 * @returns TanStack Query result for the {@link ExecutionStateResponse}.
 */
export function useExecutionState(studyId: number) {
  return useQuery<ExecutionStateResponse>({
    queryKey: ['execution-state', studyId],
    queryFn: () => getExecutionState(studyId),
    enabled: studyId > 0,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (!data || data.tasks.length === 0) return false;
      const hasActive = data.tasks.some((t) => t.status === 'active');
      return hasActive ? 5000 : false;
    },
  });
}

/** Input type for the completeTask mutation. */
export interface CompleteTaskInput {
  studyId: number;
  taskId: string;
}

/**
 * Mutation hook for marking a task complete.
 *
 * Invalidates the execution-state query for the study on success.
 *
 * @returns TanStack Mutation result for {@link CompleteTaskResponse}.
 */
export function useCompleteTask() {
  const qc = useQueryClient();
  return useMutation<CompleteTaskResponse, Error, CompleteTaskInput>({
    mutationFn: ({ studyId, taskId }) => completeTask(studyId, taskId),
    onSuccess: (_, { studyId }) => {
      qc.invalidateQueries({ queryKey: ['execution-state', studyId] });
    },
  });
}

/**
 * Mutation hook for approving a human_sign_off gate failure.
 *
 * Invalidates the execution-state query for the study on success.
 *
 * @returns TanStack Mutation result for {@link CompleteTaskResponse}.
 */
export function useApproveTask() {
  const qc = useQueryClient();
  return useMutation<CompleteTaskResponse, Error, CompleteTaskInput>({
    mutationFn: ({ studyId, taskId }) => approveTask(studyId, taskId),
    onSuccess: (_, { studyId }) => {
      qc.invalidateQueries({ queryKey: ['execution-state', studyId] });
    },
  });
}
