import { useQuery } from "react-query";
import { api } from "../services/api";
import type { DrugComparison } from "../types";

export function useDrugComparison(drugId: string | undefined) {
  return useQuery<DrugComparison>({
    queryKey: ["drug-comparison", drugId],
    queryFn: async () => {
      const res = await api.get(`/api/v1/drugs/${drugId}/compare`);
      return res.data;
    },
    enabled: !!drugId,
  });
}
