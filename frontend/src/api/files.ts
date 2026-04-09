import { apiClient } from "./client";
import type { FileItem, CreateFilePayload } from "@/types/file";
import type { PagedResponse, PaginationParams } from "@/types/pagination";

export const filesApi = {
  list: (params: PaginationParams): Promise<PagedResponse<FileItem>> =>
    apiClient.get(
      `/api/v1/files?page=${params.page}&page_size=${params.pageSize}`,
    ),

  get: (id: string): Promise<FileItem> =>
    apiClient.get(`/api/v1/files/${id}`),

  create: ({ title, file }: CreateFilePayload): Promise<FileItem> => {
    const formData = new FormData();
    formData.append("title", title);
    formData.append("file", file);
    return apiClient.postForm("/api/v1/files", formData);
  },

  update: (id: string, title: string): Promise<FileItem> =>
    apiClient.patch(`/api/v1/files/${id}`, { title }),

  delete: (id: string): Promise<void> =>
    apiClient.delete(`/api/v1/files/${id}`),

  downloadUrl: (id: string): string =>
    `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/v1/files/${id}/download`,
};
