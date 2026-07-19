export type AssignTaskInput = { taskId: string; assigneeId: string };
export type AssignTaskOutput = {
  taskId: string;
  assigneeId: string;
  assignedAt: string; // RFC3339（例: "2026-02-18T12:34:56Z" or "2026-02-18T21:34:56+09:00"）
};
