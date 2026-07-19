export type DueStatus = "ok" | "due_soon" | "overdue";

export function calcDueStatus(now: Date, dueAt?: Date): DueStatus {
  if (!dueAt) return "ok";
  const diffMs = dueAt.getTime() - now.getTime();
  const dayMs = 24 * 60 * 60 * 1000; // 24時間（暦日基準ではない）
  if (diffMs < 0) return "overdue";
  if (diffMs <= 2 * dayMs) return "due_soon";
  return "ok";
}
