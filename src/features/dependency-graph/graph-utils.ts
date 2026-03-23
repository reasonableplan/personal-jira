import type {
  DependencyGraphData,
  GraphElements,
  IssueGraphNode,
  IssueGraphEdge,
} from "./types";
import { GRAPH_LAYOUT, EDGE_STYLE } from "./constants";

export function buildGraphElements(
  data: DependencyGraphData,
  focusedIssueId?: string,
): GraphElements {
  if (data.issues.length === 0) {
    return { nodes: [], edges: [] };
  }

  const adjacency = new Map<string, string[]>();
  const inDegree = new Map<string, number>();

  data.issues.forEach((issue) => {
    adjacency.set(issue.id, []);
    inDegree.set(issue.id, 0);
  });

  data.dependencies.forEach((dep) => {
    adjacency.get(dep.from_issue_id)?.push(dep.to_issue_id);
    inDegree.set(
      dep.to_issue_id,
      (inDegree.get(dep.to_issue_id) ?? 0) + 1,
    );
  });

  const levels = computeLevels(data.issues.map((i) => i.id), adjacency, inDegree);

  const nodes: IssueGraphNode[] = data.issues.map((issue) => {
    const { col, row } = levels.get(issue.id) ?? { col: 0, row: 0 };
    return {
      id: issue.id,
      type: "issueNode" as const,
      position: {
        x: col * (GRAPH_LAYOUT.NODE_WIDTH + GRAPH_LAYOUT.HORIZONTAL_GAP),
        y: row * (GRAPH_LAYOUT.NODE_HEIGHT + GRAPH_LAYOUT.VERTICAL_GAP),
      },
      data: {
        ...issue,
        isFocused: issue.id === focusedIssueId,
      },
    };
  });

  const edges: IssueGraphEdge[] = data.dependencies.map((dep) => ({
    id: `${dep.from_issue_id}-${dep.to_issue_id}`,
    source: dep.from_issue_id,
    target: dep.to_issue_id,
    animated: dep.type === "BLOCKED_BY",
    style: EDGE_STYLE,
    label: dep.type === "BLOCKED_BY" ? "blocked by" : "blocks",
  }));

  return { nodes, edges };
}

function computeLevels(
  issueIds: string[],
  adjacency: Map<string, string[]>,
  inDegree: Map<string, number>,
): Map<string, { col: number; row: number }> {
  const result = new Map<string, { col: number; row: number }>();
  const queue: string[] = [];
  const deg = new Map(inDegree);

  issueIds.forEach((id) => {
    if ((deg.get(id) ?? 0) === 0) queue.push(id);
  });

  let col = 0;
  while (queue.length > 0) {
    const levelSize = queue.length;
    for (let row = 0; row < levelSize; row++) {
      const id = queue.shift()!;
      result.set(id, { col, row });
      adjacency.get(id)?.forEach((target) => {
        const d = (deg.get(target) ?? 1) - 1;
        deg.set(target, d);
        if (d === 0) queue.push(target);
      });
    }
    col++;
  }

  issueIds.forEach((id) => {
    if (!result.has(id)) {
      result.set(id, { col, row: result.size });
    }
  });

  return result;
}
