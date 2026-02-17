/**
 * AIDEN Frontend Utility Functions
 */

import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { format, formatDistanceToNow } from "date-fns";
import { ko } from "date-fns/locale";

// ---------------------------------------------------------------------------
// Class name helper
// ---------------------------------------------------------------------------

/**
 * Merge class names using clsx + tailwind-merge.
 * Handles conditional classes and resolves Tailwind conflicts.
 *
 * @example
 * cn("px-4 py-2", isActive && "bg-blue-500", "px-6")
 * // => "py-2 px-6 bg-blue-500" (px-6 overrides px-4)
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

// ---------------------------------------------------------------------------
// Date formatting
// ---------------------------------------------------------------------------

/**
 * Format a date string or Date object into a human-readable form.
 *
 * @param date - ISO string or Date instance
 * @param pattern - date-fns format pattern (default: "yyyy-MM-dd HH:mm")
 * @returns Formatted date string
 *
 * @example
 * formatDate("2025-01-15T09:30:00Z") // => "2025-01-15 09:30"
 */
export function formatDate(
  date: string | Date,
  pattern: string = "yyyy-MM-dd HH:mm",
): string {
  const d = typeof date === "string" ? new Date(date) : date;
  return format(d, pattern, { locale: ko });
}

/**
 * Format a date as a relative time string in Korean.
 *
 * @param date - ISO string or Date instance
 * @returns Relative time (e.g. "3분 전", "2시간 전", "어제")
 *
 * @example
 * formatRelativeTime("2025-01-15T09:25:00Z") // => "5분 전"
 */
export function formatRelativeTime(date: string | Date): string {
  const d = typeof date === "string" ? new Date(date) : date;
  return formatDistanceToNow(d, { addSuffix: true, locale: ko });
}

// ---------------------------------------------------------------------------
// Phase & status colours
// ---------------------------------------------------------------------------

/** Map of SDLC phase types to Tailwind colour classes. */
const PHASE_COLORS: Record<string, string> = {
  analysis: "text-blue-600 bg-blue-50 border-blue-200",
  design: "text-purple-600 bg-purple-50 border-purple-200",
  development: "text-green-600 bg-green-50 border-green-200",
  testing: "text-orange-600 bg-orange-50 border-orange-200",
};

/**
 * Return Tailwind colour classes for a given SDLC phase type.
 *
 * @param phase - Phase type string (analysis, design, development, testing)
 * @returns Tailwind class string for text, bg, and border
 */
export function getPhaseColor(phase: string): string {
  return PHASE_COLORS[phase.toLowerCase()] ?? "text-gray-600 bg-gray-50 border-gray-200";
}

/** Map of status values to Tailwind colour classes. */
const STATUS_COLORS: Record<string, string> = {
  // General
  created: "text-gray-600 bg-gray-50 border-gray-200",
  pending: "text-yellow-600 bg-yellow-50 border-yellow-200",
  in_progress: "text-blue-600 bg-blue-50 border-blue-200",
  running: "text-blue-600 bg-blue-50 border-blue-200",
  completed: "text-green-600 bg-green-50 border-green-200",
  failed: "text-red-600 bg-red-50 border-red-200",
  error: "text-red-600 bg-red-50 border-red-200",
  cancelled: "text-gray-500 bg-gray-50 border-gray-200",
  archived: "text-gray-400 bg-gray-50 border-gray-200",

  // HITL-specific
  approved: "text-green-600 bg-green-50 border-green-200",
  rejected: "text-red-600 bg-red-50 border-red-200",
  revision_requested: "text-amber-600 bg-amber-50 border-amber-200",

  // Agent-specific
  initialized: "text-gray-600 bg-gray-50 border-gray-200",
  waiting_for_review: "text-amber-600 bg-amber-50 border-amber-200",

  // Deliverable-specific
  draft: "text-gray-600 bg-gray-50 border-gray-200",
  review: "text-amber-600 bg-amber-50 border-amber-200",
  final: "text-green-600 bg-green-50 border-green-200",
};

/**
 * Return Tailwind colour classes for a given status string.
 *
 * @param status - Status string (e.g. "in_progress", "completed")
 * @returns Tailwind class string for text, bg, and border
 */
export function getStatusColor(status: string): string {
  return STATUS_COLORS[status.toLowerCase()] ?? "text-gray-600 bg-gray-50 border-gray-200";
}

// ---------------------------------------------------------------------------
// Status labels (Korean)
// ---------------------------------------------------------------------------

/** Map of status values to Korean display labels. */
const STATUS_LABELS: Record<string, string> = {
  // General workflow
  created: "생성됨",
  pending: "대기 중",
  in_progress: "진행 중",
  running: "실행 중",
  completed: "완료",
  failed: "실패",
  error: "오류",
  cancelled: "취소됨",
  archived: "보관됨",

  // HITL
  approved: "승인됨",
  rejected: "거부됨",
  revision_requested: "수정 요청됨",

  // Agent
  initialized: "초기화됨",
  waiting_for_review: "검토 대기",

  // Deliverable
  draft: "초안",
  review: "검토 중",
  final: "최종",

  // Phase types (also useful as labels)
  analysis: "분석",
  design: "설계",
  development: "개발",
  testing: "테스트",
};

/**
 * Return the Korean display label for a status string.
 *
 * @param status - Status string (e.g. "in_progress", "completed")
 * @returns Korean label, or the original string if no mapping exists
 */
export function getStatusLabel(status: string): string {
  return STATUS_LABELS[status.toLowerCase()] ?? status;
}

// ---------------------------------------------------------------------------
// Text utilities
// ---------------------------------------------------------------------------

/**
 * Truncate text to a maximum length, appending ellipsis if truncated.
 *
 * @param text - Source text
 * @param maxLength - Maximum character length (default: 100)
 * @returns Truncated string with "..." if it exceeds maxLength
 *
 * @example
 * truncateText("Hello, World!", 5) // => "Hello..."
 */
export function truncateText(text: string, maxLength: number = 100): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + "...";
}
