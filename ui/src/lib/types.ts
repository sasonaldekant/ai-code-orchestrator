export type EventType =
    | "log"
    | "thought"
    | "plan"
    | "milestone"
    | "task"
    | "artifact"
    | "error"
    | "done"
    | "info";

export interface LogEvent {
    type: EventType;
    content: string | any;
    agent: string;
    timestamp: string;
}

export interface Task {
    id: string;
    description: string;
    status: "pending" | "running" | "completed" | "failed";
}

export interface Milestone {
    id: string;
    tasks: Task[];
    status: "pending" | "running" | "completed" | "failed";
}

export interface ImplementationPlan {
    milestones: Milestone[];
}
