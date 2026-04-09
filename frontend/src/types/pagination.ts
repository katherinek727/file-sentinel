export interface PaginationParams {
  page: number;
  pageSize: number;
}

export interface PagedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
