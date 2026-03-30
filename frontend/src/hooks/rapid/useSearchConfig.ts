/**
 * TanStack Query hooks for Rapid Review search configuration (feature 008).
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { updateSearchConfig, SearchConfigRequest } from '../../services/rapid/searchConfigApi';
import { rrThreatsKey } from './useRRProtocol';

export function useUpdateSearchConfig(studyId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: SearchConfigRequest) => updateSearchConfig(studyId, data),
    onSuccess: (threats) => {
      queryClient.setQueryData(rrThreatsKey(studyId), threats);
    },
  });
}
