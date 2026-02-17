// =============================================================================
// AIDEN Platform - Shared TypeScript Types
// =============================================================================
// These interfaces mirror the backend SQLAlchemy models and API response shapes.
// All UUID fields are represented as strings on the frontend.
// All datetime fields are ISO-8601 strings.
// =============================================================================

// ---------------------------------------------------------------------------
// Enums / Union Types
// ---------------------------------------------------------------------------

export type ProjectStatus =
  | 'created'
  | 'in_progress'
  | 'paused'
  | 'completed'
  | 'failed';

export type PhaseStatus =
  | 'pending'
  | 'in_progress'
  | 'completed'
  | 'failed';

export type ReviewStatus =
  | 'pending'
  | 'approved'
  | 'rejected'
  | 'revision_requested';

export type ExecutionStatus =
  | 'initialized'
  | 'running'
  | 'interrupted'
  | 'completed'
  | 'failed';

export type DeliverableStatus =
  | 'draft'
  | 'in_review'
  | 'approved'
  | 'final';

export type ReviewDecisionType =
  | 'approved'
  | 'rejected'
  | 'revision_requested';

export type LogLevel =
  | 'debug'
  | 'info'
  | 'warning'
  | 'error';

export type ConnectionStatus =
  | 'connecting'
  | 'connected'
  | 'disconnected'
  | 'error';

// ---------------------------------------------------------------------------
// Domain Models
// ---------------------------------------------------------------------------

export interface Project {
  id: string;
  name: string;
  description: string | null;
  status: ProjectStatus;
  owner_id: string | null;
  current_phase: string | null;
  config: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface ProjectPhase {
  id: string;
  project_id: string;
  phase_type: string;
  phase_order: number;
  status: PhaseStatus;
  agent_name: string | null;
  config: Record<string, unknown>;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Document {
  id: string;
  project_id: string;
  title: string;
  doc_type: string;
  file_path: string | null;
  file_name: string | null;
  file_size: number | null;
  mime_type: string | null;
  content_text: string | null;
  is_indexed: boolean;
  created_at: string;
  updated_at: string;
}

export interface Deliverable {
  id: string;
  phase_id: string;
  title: string;
  deliverable_type: string;
  status: DeliverableStatus;
  current_version: number;
  format: string | null;
  created_at: string;
  updated_at: string;
}

export interface DeliverableVersion {
  id: string;
  deliverable_id: string;
  version_number: number;
  content: string;
  content_structured: Record<string, unknown> | null;
  change_summary: string | null;
  created_by: string | null;
  created_at: string;
  updated_at: string;
}

export interface AgentExecution {
  id: string;
  phase_id: string;
  agent_name: string;
  thread_id: string;
  status: ExecutionStatus;
  config: Record<string, unknown>;
  total_tokens: number;
  total_cost: number;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface AgentLog {
  id: string;
  execution_id: string;
  log_level: LogLevel;
  node_name: string | null;
  event_type: string;
  message: string;
  data: Record<string, unknown>;
  created_at: string;
}

export interface HITLReview {
  id: string;
  execution_id: string | null;
  task_id: string | null;
  review_type: string;
  status: ReviewStatus;
  interrupt_id: string | null;
  content_snapshot: Record<string, unknown>;
  reviewer_id: string | null;
  assigned_at: string | null;
  decided_at: string | null;
  deadline_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ReviewDecision {
  id: string;
  review_id: string;
  decision: ReviewDecisionType;
  feedback: string | null;
  edits: Record<string, unknown> | null;
  decided_by: string | null;
  created_at: string;
}

export interface WebSocketEvent {
  event_type: string;
  project_id: string;
  data: Record<string, unknown>;
  timestamp: string;
  execution_id?: string;
  agent_name?: string;
}

// ---------------------------------------------------------------------------
// API Request / Response Helpers
// ---------------------------------------------------------------------------

export interface CreateProjectRequest {
  name: string;
  description?: string;
  config?: Record<string, unknown>;
}

export interface UpdateProjectRequest {
  name?: string;
  description?: string;
  config?: Record<string, unknown>;
}

export interface ReviewActionRequest {
  feedback?: string;
  edits?: Record<string, unknown>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}
