import { Handle, Position } from "@xyflow/react";
import type { IssueNodeData } from "./types";
import { STATUS_COLORS, PRIORITY_COLORS } from "./constants";

interface IssueNodeProps {
  data: IssueNodeData;
}

export function IssueNode({ data }: IssueNodeProps) {
  return (
    <div
      data-testid="issue-node"
      style={{
        padding: "12px 16px",
        borderRadius: 8,
        border: data.isFocused ? "2px solid #3b82f6" : "1px solid #e2e8f0",
        backgroundColor: data.isFocused ? "#eff6ff" : "#ffffff",
        boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
        minWidth: 200,
      }}
    >
      <Handle type="target" position={Position.Left} />
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
        <span style={{ fontSize: 11, color: "#94a3b8" }}>#{data.id}</span>
        <span
          style={{
            fontSize: 10,
            fontWeight: 600,
            color: PRIORITY_COLORS[data.priority] ?? "#6b7280",
          }}
        >
          {data.priority}
        </span>
      </div>
      <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 6, color: "#1e293b" }}>
        {data.title}
      </div>
      <span
        data-testid="status-badge"
        style={{
          display: "inline-block",
          fontSize: 10,
          fontWeight: 600,
          padding: "2px 8px",
          borderRadius: 9999,
          color: "#ffffff",
          backgroundColor: STATUS_COLORS[data.status] ?? "#94a3b8",
        }}
      >
        {data.status}
      </span>
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
