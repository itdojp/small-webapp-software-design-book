export type AssignTaskDeps = {
  now: () => Date;
  saveAssignment: (input: {
    taskId: string;
    assigneeId: string;
    assignedAt: Date;
  }) => Promise<void>;
  enqueueAssignedNotification: (input: {
    taskId: string;
    assigneeId: string;
    assignedAt: Date;
  }) => Promise<void>;
};

export async function assignTask(
  deps: AssignTaskDeps,
  input: { taskId: string; assigneeId: string }
): Promise<void> {
  const assignedAt = deps.now();
  await deps.saveAssignment({ ...input, assignedAt });
  // 送信そのものではなく、通知要求（outbox/queue等）の記録までを責務とする。
  await deps.enqueueAssignedNotification({ ...input, assignedAt });
}
