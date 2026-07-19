export type TaskStatus = "todo" | "in_progress" | "done";

export function canTransition(from: TaskStatus, to: TaskStatus): boolean {
  const allowed: Record<TaskStatus, TaskStatus[]> = {
    todo: ["in_progress"],
    in_progress: ["done"],
    done: [],
  };
  return allowed[from].includes(to);
}
