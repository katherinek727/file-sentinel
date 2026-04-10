const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const isFormData = init?.body instanceof FormData;

  const response = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: isFormData
      ? undefined  // let the browser set Content-Type + boundary automatically
      : {
          "Content-Type": "application/json",
          ...init?.headers,
        },
  });

  if (!response.ok) {
    const detail = await response
      .json()
      .then((d) => {
        if (typeof d?.detail === "string") return d.detail;
        if (Array.isArray(d?.detail)) {
          return d.detail.map((e: { msg?: string }) => e.msg ?? String(e)).join(", ");
        }
        return response.statusText;
      })
      .catch(() => response.statusText);
    throw new ApiError(response.status, detail);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export const apiClient = {
  get: <T>(path: string) => request<T>(path),

  post: <T>(path: string, body: unknown) =>
    request<T>(path, {
      method: "POST",
      body: JSON.stringify(body),
    }),

  postForm: <T>(path: string, formData: FormData) =>
    request<T>(path, {
      method: "POST",
      body: formData,
    }),

  patch: <T>(path: string, body: unknown) =>
    request<T>(path, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),

  delete: <T>(path: string) =>
    request<T>(path, { method: "DELETE" }),
};
