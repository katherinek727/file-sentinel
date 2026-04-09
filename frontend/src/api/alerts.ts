import { apiClient } from "./client";
import type { AlertItem } from "@/types/alert";
import type { PagedResponse, PaginationParams } from "@/types/pagination";

export const alertsApi = {
  list: (params: PaginationParams): Promise<PagedResponse<AlertItem>> =>
    apiClient.get(
      `/api/v1/alerts?page=${params.page}&page_size=${params.pageSize}`,
    ),
};
