/**
 * D3 force-directed graph visualization component for research protocols (feature 010).
 *
 * Renders protocol nodes (rect+label) and directed edges (path+arrowhead) using
 * D3.js inside an SVG. Supports read-only view and edit mode (drag-to-reposition,
 * node/edge selection). D3 imperative setup is delegated to useProtocolD3.
 */

import { useEffect } from 'react';
import type { ProtocolDetail, ProtocolNode } from '../../services/protocols/protocolsApi';
import type { EditorNode, EditorEdge } from '../../hooks/protocols/useProtocolEditor';
import { useProtocolD3 } from '../../hooks/protocols/useProtocolD3';

interface ProtocolGraphProps {
  /** The protocol to render (read-only mode). */
  protocol?: ProtocolDetail;
  /** Nodes for edit mode (overrides protocol.nodes when provided). */
  nodes?: EditorNode[];
  /** Edges for edit mode (overrides protocol.edges when provided). */
  edges?: EditorEdge[];
  /** Called when a node is clicked. */
  onNodeClick?: (node: ProtocolNode | EditorNode) => void;
  /** Called when a node is dragged to a new position (edit mode). */
  onNodeMove?: (taskId: string, x: number, y: number) => void;
  /** Whether drag-to-reposition and edit actions are enabled. */
  editMode?: boolean;
  /** Width of the SVG canvas in pixels. */
  width?: number;
  /** Height of the SVG canvas in pixels. */
  height?: number;
}

/**
 * D3 force-directed visualization of a research protocol graph.
 *
 * Supports both read-only and edit modes. In edit mode nodes are draggable
 * and `onNodeMove` is called on drop.
 *
 * @param props - Component props.
 * @returns SVG graph element.
 */
export default function ProtocolGraph({
  protocol,
  nodes: editNodes,
  edges: editEdges,
  onNodeClick,
  onNodeMove,
  editMode = false,
  width = 800,
  height = 520,
}: ProtocolGraphProps) {
  const { svgRef, render } = useProtocolD3(onNodeMove);

  const resolvedNodes: EditorNode[] =
    editNodes ??
    protocol?.nodes.map((n) => ({
      ...n,
      position_x: n.position_x ?? 0,
      position_y: n.position_y ?? 0,
    })) ??
    [];

  const resolvedEdges: EditorEdge[] = editEdges ?? protocol?.edges ?? [];

  useEffect(() => {
    if (!svgRef.current) return;
    render(
      resolvedNodes,
      resolvedEdges,
      width,
      height,
      onNodeClick as (n: EditorNode) => void,
      editMode,
    );
  }, [render, resolvedNodes, resolvedEdges, width, height, onNodeClick, editMode]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <svg
      ref={svgRef}
      width={width}
      height={height}
      style={{ border: '1px solid #e2e8f0', borderRadius: 8, background: '#f8fafc' }}
    />
  );
}
