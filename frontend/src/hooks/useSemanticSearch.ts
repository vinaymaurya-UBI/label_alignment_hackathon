import { useState, useCallback } from "react";
import { api } from "../services/api";
import type { SemanticSearchResult } from "../types";

export function useSemanticSearch() {
  const [data, setData] = useState<SemanticSearchResult[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const search = useCallback(async (query: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.post<SemanticSearchResult[]>("/api/v1/search/semantic", { query, top_k: 8 });
      setData(res.data);
    } catch {
      setError("Search failed. Please try again.");
      setData(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { data, isLoading, error, search };
}
