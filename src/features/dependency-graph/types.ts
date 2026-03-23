import type { Node, Edge } from "@xyflow/react";

export interface IssueNodeData {
  id: string;
  title: string;
  status: IssueStatus;
  priority: IssuePriority;
  isFocused?: boolean;
}

export type IssueStatus =
  | "BACKLOG"
  | "READY"
  | "IN_PROGRESS"
  | "IN_REVIEW"
  | "BLOCKED"
  | "DONE"
  | "CANCELLED";

export type IssuePriority = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";

export type DependencyType = "BLOCKED_BY" | "BLOCKS";

export interface DependencyEdge {
  from_issue_id: string;
  to_issue_id: string;
  type: DependencyType;
}

export interface DependencyGraphData {
  issues: IssueNodeData[];
  dependencies: DependencyEdge[];
}

export type IssueGraphNode = Node<IssueNodeData, "issueNode">;
export type IssueGraphEdge = Edge;

export interface GraphElements {
  nodes: IssueGraphNode[];
  edges: IssueGraphEdge[];
}
