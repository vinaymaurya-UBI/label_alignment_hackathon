import { useQuery, useMutation, useQueryClient } from "react-query";
import { api } from "../services/api";

export interface ActivityLog {
  id: string;
  type: string;
  title: string;
  subtitle?: string;
  status?: string;
  created_at: string;
  meta: any;
}

export const useActivity = (limit = 50) => {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: ["activity", limit],
    queryFn: async () => {
      const response = await api.get<ActivityLog[]>(`/api/v1/admin/activity?limit=${limit}`);
      return response.data;
    },
  });

  const clearMutation = useMutation({
    mutationFn: async () => {
      await api.delete("/api/v1/admin/activity");
    },
    onSuccess: () => {
      queryClient.setQueryData(["activity", limit], []);
      queryClient.invalidateQueries("activity");
    },
  });

  return {
    ...query,
    clearActivity: clearMutation.mutate,
    isClearing: clearMutation.isLoading,
  };
};

export const useAnalytics = () => {
  return useQuery({
    queryKey: ["analytics-summary"],
    queryFn: async () => {
      const response = await api.get("/api/v1/admin/analytics/summary");
      return response.data;
    },
  });
};
