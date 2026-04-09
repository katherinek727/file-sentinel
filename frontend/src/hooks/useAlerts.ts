"use client";

import { useCallback, useState } from "react";
import { alertsApi } from "@/api/alerts";
import type { AlertItem } from "@/types/alert";
import type { PagedResponse, PaginationParams } from "@/types/pagination";

interface UseAlertsReturn {
  data: PagedResponse<AlertItem> | null;
  isLoading: boolean;
  error: string | null;
  fetch: (params: PaginationParams) => Promise<void>;
}

export function useAlerts(): UseAlertsReturn {
  const [data, setData] = useState<PagedResponse<AlertItem> | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async (params: PaginationParams) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await alertsApi.list(params);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load alerts");
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { data, isLoading, error, fetch };
}
