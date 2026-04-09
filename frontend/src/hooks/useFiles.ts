"use client";

import { useCallback, useState } from "react";
import { filesApi } from "@/api/files";
import type { FileItem, CreateFilePayload } from "@/types/file";
import type { PagedResponse, PaginationParams } from "@/types/pagination";

interface UseFilesReturn {
  data: PagedResponse<FileItem> | null;
  isLoading: boolean;
  error: string | null;
  fetch: (params: PaginationParams) => Promise<void>;
  create: (payload: CreateFilePayload) => Promise<void>;
  remove: (id: string) => Promise<void>;
}

export function useFiles(): UseFilesReturn {
  const [data, setData] = useState<PagedResponse<FileItem> | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async (params: PaginationParams) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await filesApi.list(params);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load files");
    } finally {
      setIsLoading(false);
    }
  }, []);

  const create = useCallback(async (payload: CreateFilePayload) => {
    await filesApi.create(payload);
  }, []);

  const remove = useCallback(async (id: string) => {
    await filesApi.delete(id);
  }, []);

  return { data, isLoading, error, fetch, create, remove };
}
