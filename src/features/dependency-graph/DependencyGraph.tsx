import { useCallback, useEffect, useMemo, useState } from "react";
import {
  ReactFlow,
  Controls,
  Background,
  BackgroundVariant,
  useNodesState,
  useEdgesState,
  type NodeTypes,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import type { DependencyGraphData } from "./types";
import { fetchDependencyGraph } from "./api";
import { buildGraphElements } from "./graph-utils";
import { IssueNode } from "./IssueNode";

interface DependencyGraphProps {
  issueId?: string;
}

const nodeTypes: NodeTypes = {
  issueNode: IssueNode,
};

export function DependencyGraph({ issueId }: DependencyGraphProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEmpty, setIsEmpty] = useState(false);

  const loadGraph = useCallback(async () => {
    setLoading(true);
    setError(null);
    setIsEmpty(false);
    try {
      const data: DependencyGraphData = await fetchDependencyGraph(issueId);
      if (data.issues.length === 0) {
        setIsEmpty(true);
        setNodes([]);
        setEdges([]);
      } else {
        const elements = buildGraphElements(data, issueId);
        setNodes(elements.nodes);
        setEdges(elements.edges);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error occurred");
    } finally {
      setLoading(false);
    }
  }, [issueId, setNodes, setEdges]);

  useEffect(() => {
    loadGraph();
  }, [loadGraph]);

  if (loading) {
    return (
      <div data-testid="dependency-graph-loading" style={containerStyle}>
        <span style={{ color: "#94a3b8" }}>Loading dependency graph...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div data-testid="dependency-graph-error" style={containerStyle}>
        <span style={{ color: "#ef4444" }}>{error}</span>
        <button onClick={loadGraph} style={retryButtonStyle}>Retry</button>
      </div>
    );
  }

  if (isEmpty) {
    return (
      <div data-testid="dependency-graph-empty" style={containerStyle}>
        <span style={{ color: "#94a3b8" }}>No dependencies found.</span>
      </div>
    );
  }

  return (
    <div data-testid="dependency-graph" style={{ width: "100%", height: "100%", minHeight: 500 }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        proOptions={{ hideAttribution: true }}
      >
        <Controls />
        <Background variant={BackgroundVariant.Dots} gap={16} size={1} />
      </ReactFlow>
    </div>
  );
}

const containerStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  height: "100%",
  minHeight: 300,
  gap: 12,
};

const retryButtonStyle: React.CSSProperties = {
  padding: "6px 16px",
  borderRadius: 6,
  border: "1px solid #e2e8f0",
  backgroundColor: "#ffffff",
  cursor: "pointer",
  fontSize: 13,
};
