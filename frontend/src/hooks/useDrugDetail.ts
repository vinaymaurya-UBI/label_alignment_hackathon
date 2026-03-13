import { useQuery } from "react-query";
import { api } from "../services/api";
import type { DrugDetail } from "../types";

export function useDrugDetail(drugId: string | null) {
  return useQuery<DrugDetail>({
    queryKey: ["drug", drugId],
    queryFn: async () => {
      const res = await api.get(`/api/v1/drugs/${drugId}`);
      return res.data;
    },
    enabled: !!drugId,
  });
}
