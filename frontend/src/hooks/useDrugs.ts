import { useQuery } from "react-query";
import { api } from "../services/api";
import type { DrugListResponse, PlatformStats } from "../types";

export interface DrugFilters {
  search?: string;
  manufacturer?: string;
  country?: string;
  limit?: number;
  offset?: number;
}

export function useDrugs(filters: DrugFilters = {}) {
  return useQuery<DrugListResponse>({
    queryKey: ["drugs", filters],
    queryFn: async () => {
      const res = await api.get("/api/v1/drugs/", { params: filters });
      return res.data;
    },
    keepPreviousData: true,
  });
}

export function useManufacturers() {
  return useQuery<string[]>({
    queryKey: ["manufacturers"],
    queryFn: async () => {
      const res = await api.get("/api/v1/drugs/manufacturers");
      return res.data.manufacturers;
    },
  });
}

export function useStats() {
  return useQuery<PlatformStats>({
    queryKey: ["stats"],
    queryFn: async () => {
      const res = await api.get("/api/v1/drugs/stats");
      return res.data;
    },
  });
}
