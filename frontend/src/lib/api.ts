/**
 * AIDEN REST API Client
 *
 * Typed API client that wraps fetch with error handling, JSON parsing,
 * and auth token injection. Aligned with backend FastAPI endpoints.
 */

// ---------------------------------------------------------------------------
// Base configuration
// ---------------------------------------------------------------------------

const BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api/v1";

// ---------------------------------------------------------------------------
// Types  (mirror backend Pydantic schemas)
// ---------------------------------------------------------------------------

/** Standard success envelope returned by the backend. */
export interface SuccessResponse<T> {
  success: true;
  data: T;
}

/** Paginated response envelope. */
export interface PaginatedResponse<T> {
  success: true;
  data: T[];
  meta: {
    page: number;
    page_size: number;
    total: number;
  };
}

/** Standard error envelope returned by the backend. */
export interface ErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
}

// --- Project ---

export interface ProjectCreate {
  name: string;
  description?: string | null;
  config?: Record<string, unknown>;
}

export interface ProjectUpdate {
  name?: string | null;
  description?: string | null;
  config?: Record<string, unknown> | null;
  status?: string | null;
}

export interface ProjectResponse {
  id: string;
  name: string;
  description: string | null;
  status: string;
  owner_id: string | null;
  config: Record<string, unknown>;
  current_phase: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectDetailResponse extends ProjectResponse {
  phases: PhaseResponse[];
}

// --- Phase ---

export interface PhaseResponse {
  id: string;
  project_id: string;
  phase_type: string;
  phase_order: number;
  status: string;
  agent_name: string | null;
  started_at: string | null;
  completed_at: string | null;
  config: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface PhaseStatusResponse {
  id: string;
  phase_type: string;
  status: string;
  agent_name: string | null;
  progress: Record<string, unknown>;
}

// --- Document ---

export interface DocumentResponse {
  id: string;
  project_id: string;
  title: string;
  doc_type: string;
  file_name: string | null;
  file_size: number | null;
  mime_type: string | null;
  content_text: string | null;
  is_indexed: boolean;
  metadata_: Record<string, unknown>;
  uploaded_by: string | null;
  created_at: string;
  updated_at: string;
}

export interface DocumentUploadResponse {
  id: string;
  project_id: string;
  title: string;
  doc_type: string;
  file_name: string | null;
  file_size: number | null;
  mime_type: string | null;
  is_indexed: boolean;
  created_at: string;
}

// --- Deliverable ---

export interface DeliverableResponse {
  id: string;
  phase_id: string;
  title: string;
  deliverable_type: string;
  status: string;
  current_version: number;
  format: string | null;
  metadata_: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface DeliverableVersionResponse {
  id: string;
  deliverable_id: string;
  version_number: number;
  content: string;
  content_structured: Record<string, unknown> | null;
  change_summary: string | null;
  created_by: string | null;
  created_at: string;
}

// --- Agent ---

export interface AgentExecutionResponse {
  id: string;
  phase_id: string;
  agent_name: string;
  thread_id: string;
  status: string;
  config: Record<string, unknown>;
  total_tokens: number;
  total_cost: number;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface AgentLogResponse {
  id: string;
  execution_id: string;
  log_level: string;
  node_name: string | null;
  event_type: string;
  message: string;
  data: Record<string, unknown>;
  created_at: string;
}

// --- HITL Review ---

export interface HITLReviewResponse {
  id: string;
  execution_id: string | null;
  task_id: string | null;
  review_type: string;
  status: string;
  content_snapshot: Record<string, unknown>;
  reviewer_id: string | null;
  assigned_at: string | null;
  decided_at: string | null;
  deadline_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ReviewDecisionResponse {
  id: string;
  review_id: string;
  decision: string;
  feedback: string | null;
  edits: Record<string, unknown> | null;
  decided_by: string | null;
  created_at: string;
}

// ---------------------------------------------------------------------------
// Custom error
// ---------------------------------------------------------------------------

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public details?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

// ---------------------------------------------------------------------------
// Core fetch helper
// ---------------------------------------------------------------------------

function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("aiden_token");
}

/**
 * Generic fetch wrapper with JSON parsing, auth header injection,
 * and structured error handling.
 */
export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const url = `${BASE_URL}${path}`;

  const headers = new Headers(options.headers);

  // Inject auth token when available
  const token = getAuthToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  // Default content-type for JSON bodies (skip for FormData uploads)
  if (options.body && !(options.body instanceof FormData)) {
    if (!headers.has("Content-Type")) {
      headers.set("Content-Type", "application/json");
    }
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  // Handle non-JSON error responses
  if (!response.ok) {
    let errorBody: ErrorResponse | undefined;
    try {
      errorBody = (await response.json()) as ErrorResponse;
    } catch {
      throw new ApiError(
        response.status,
        "UNKNOWN_ERROR",
        response.statusText || "An unexpected error occurred",
      );
    }

    throw new ApiError(
      response.status,
      errorBody?.error?.code ?? "UNKNOWN_ERROR",
      errorBody?.error?.message ?? response.statusText,
      errorBody?.error?.details,
    );
  }

  // 204 No Content
  if (response.status === 204) {
    return undefined as unknown as T;
  }

  return (await response.json()) as T;
}

// ---------------------------------------------------------------------------
// API namespaces
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Unwrap helpers – extract `.data` from envelope so callers get plain values
// ---------------------------------------------------------------------------

async function unwrap<T>(promise: Promise<SuccessResponse<T>>): Promise<T> {
  const res = await promise;
  return res.data;
}

async function unwrapPaginated<T>(promise: Promise<PaginatedResponse<T>>): Promise<T[]> {
  const res = await promise;
  return res.data;
}

/** Projects CRUD + workflow actions. */
export const projectsApi = {
  /** List projects with pagination. */
  list(page = 1, pageSize = 20) {
    return unwrapPaginated(
      apiFetch<PaginatedResponse<ProjectResponse>>(
        `/projects?page=${page}&page_size=${pageSize}`,
      ),
    );
  },

  /** Get a single project with phases. */
  get(id: string) {
    return unwrap(
      apiFetch<SuccessResponse<ProjectDetailResponse>>(`/projects/${id}`),
    );
  },

  /** Create a new project. */
  create(data: ProjectCreate) {
    return unwrap(
      apiFetch<SuccessResponse<ProjectDetailResponse>>("/projects", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    );
  },

  /** Update project fields (partial). */
  update(id: string, data: ProjectUpdate) {
    return unwrap(
      apiFetch<SuccessResponse<ProjectDetailResponse>>(`/projects/${id}`, {
        method: "PATCH",
        body: JSON.stringify(data),
      }),
    );
  },

  /** Soft-delete (archive) a project. */
  delete(id: string) {
    return unwrap(
      apiFetch<SuccessResponse<{ message: string }>>(`/projects/${id}`, {
        method: "DELETE",
      }),
    );
  },

  /** Start the project workflow (begins analysis phase). */
  start(id: string) {
    return unwrap(
      apiFetch<SuccessResponse<ProjectDetailResponse>>(
        `/projects/${id}/start`,
        { method: "POST" },
      ),
    );
  },
};

/** Document management. */
export const documentsApi = {
  list(projectId: string) {
    return unwrap(
      apiFetch<SuccessResponse<DocumentResponse[]>>(`/documents/projects/${projectId}`),
    );
  },

  get(id: string) {
    return unwrap(apiFetch<SuccessResponse<DocumentResponse>>(`/documents/${id}`));
  },

  upload(projectId: string, file: File, title?: string, docType = "dev_request") {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", title ?? file.name);
    formData.append("doc_type", docType);
    return unwrap(
      apiFetch<SuccessResponse<DocumentUploadResponse>>(
        `/documents/projects/${projectId}/upload`,
        { method: "POST", body: formData },
      ),
    );
  },
};

/** Phase management. */
export const phasesApi = {
  list(projectId: string) {
    return unwrap(
      apiFetch<SuccessResponse<PhaseResponse[]>>(`/phases/projects/${projectId}`),
    );
  },

  get(id: string) {
    return unwrap(apiFetch<SuccessResponse<PhaseResponse>>(`/phases/${id}`));
  },

  getStatus(id: string) {
    return unwrap(
      apiFetch<SuccessResponse<PhaseStatusResponse>>(`/phases/${id}/status`),
    );
  },

  start(id: string) {
    return unwrap(
      apiFetch<SuccessResponse<PhaseResponse>>(`/phases/${id}/start`, { method: "POST" }),
    );
  },
};

/** Deliverable access. */
export const deliverablesApi = {
  list(phaseId: string) {
    return unwrap(
      apiFetch<SuccessResponse<DeliverableResponse[]>>(`/deliverables/phases/${phaseId}`),
    );
  },

  get(id: string) {
    return unwrap(apiFetch<SuccessResponse<DeliverableResponse>>(`/deliverables/${id}`));
  },

  getVersions(id: string) {
    return unwrap(
      apiFetch<SuccessResponse<DeliverableVersionResponse[]>>(`/deliverables/${id}/versions`),
    );
  },
};

/** Agent execution monitoring. */
export const agentsApi = {
  getExecution(id: string) {
    return unwrap(
      apiFetch<SuccessResponse<AgentExecutionResponse>>(`/agents/${id}`),
    );
  },

  getLogs(executionId: string, page = 1, pageSize = 50) {
    return unwrapPaginated(
      apiFetch<PaginatedResponse<AgentLogResponse>>(
        `/agents/${executionId}/logs?page=${page}&page_size=${pageSize}`,
      ),
    );
  },
};

/** HITL (Human-In-The-Loop) review management. */
export const hitlApi = {
  listPending() {
    return unwrap(apiFetch<SuccessResponse<HITLReviewResponse[]>>("/reviews"));
  },

  get(id: string) {
    return unwrap(apiFetch<SuccessResponse<HITLReviewResponse>>(`/reviews/${id}`));
  },

  approve(id: string, feedback?: string) {
    return unwrap(
      apiFetch<SuccessResponse<ReviewDecisionResponse>>(`/reviews/${id}/approve`, {
        method: "POST",
        body: JSON.stringify({ feedback: feedback ?? null }),
      }),
    );
  },

  reject(id: string, feedback: string) {
    return unwrap(
      apiFetch<SuccessResponse<ReviewDecisionResponse>>(`/reviews/${id}/reject`, {
        method: "POST",
        body: JSON.stringify({ feedback }),
      }),
    );
  },

  requestRevision(id: string, feedback: string, edits?: Record<string, unknown>) {
    return unwrap(
      apiFetch<SuccessResponse<ReviewDecisionResponse>>(`/reviews/${id}/request-revision`, {
        method: "POST",
        body: JSON.stringify({ feedback, edits: edits ?? {} }),
      }),
    );
  },
};
