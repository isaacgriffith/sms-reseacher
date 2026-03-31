/**
 * D3 force simulation and drag setup hook for the protocol graph editor (feature 010).
 *
 * Extracts all D3 imperative setup from ProtocolGraph.tsx so the component
 * stays within the JSX line limit. Returns an SVG ref and a render callback.
 */

import { useRef, useCallback, useEffect } from 'react';
import * as d3 from 'd3';
import type { EditorNode, EditorEdge } from './useProtocolEditor';

export interface D3SimNode extends d3.SimulationNodeDatum {
  id: string;
  label: string;
  data: EditorNode;
}

export interface D3SimLink extends d3.SimulationLinkDatum<D3SimNode> {
  data: EditorEdge;
}

const NODE_W = 140;
const NODE_H = 44;

/**
 * Hook that owns the D3 force simulation lifecycle.
 *
 * @param onPositionChange - Called when a node is dragged to a new position.
 * @returns svgRef to attach to the SVG element, and a render function.
 */
export function useProtocolD3(onPositionChange?: (taskId: string, x: number, y: number) => void) {
  const svgRef = useRef<SVGSVGElement>(null);
  const simRef = useRef<d3.Simulation<D3SimNode, D3SimLink> | null>(null);

  useEffect(() => {
    return () => {
      simRef.current?.stop();
    };
  }, []);

  const render = useCallback(
    (
      nodes: EditorNode[],
      edges: EditorEdge[],
      width: number,
      height: number,
      onNodeClick?: (node: EditorNode) => void,
      editMode = false,
    ) => {
      const svg = d3.select(svgRef.current);
      svg.selectAll('*').remove();
      simRef.current?.stop();

      if (nodes.length === 0) return;

      svg
        .append('defs')
        .append('marker')
        .attr('id', 'arrow')
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', NODE_W / 2 + 6)
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', '#888');

      const simNodes: D3SimNode[] = nodes.map((n) => ({
        id: n.task_id,
        label: n.label,
        data: n,
        x: n.position_x || undefined,
        y: n.position_y || undefined,
      }));

      const nodeById = new Map(simNodes.map((n) => [n.id, n]));

      const simLinks: D3SimLink[] = edges
        .map((e) => ({
          source: nodeById.get(e.source_task_id) ?? e.source_task_id,
          target: nodeById.get(e.target_task_id) ?? e.target_task_id,
          data: e,
        }))
        .filter((l) => typeof l.source === 'object' && typeof l.target === 'object');

      const linkSel = svg
        .append('g')
        .selectAll<SVGLineElement, D3SimLink>('line')
        .data(simLinks)
        .join('line')
        .attr('stroke', '#aaa')
        .attr('stroke-width', 1.5)
        .attr('marker-end', 'url(#arrow)');

      const nodeSel = svg
        .append('g')
        .selectAll<SVGGElement, D3SimNode>('g')
        .data(simNodes)
        .join('g')
        .attr('cursor', onNodeClick ? 'pointer' : 'default')
        .on('click', (_ev, d) => onNodeClick?.(d.data));

      nodeSel
        .append('rect')
        .attr('width', NODE_W)
        .attr('height', NODE_H)
        .attr('rx', 6)
        .attr('fill', '#fff')
        .attr('stroke', '#1976d2')
        .attr('stroke-width', 1.5);

      nodeSel
        .append('text')
        .attr('x', NODE_W / 2)
        .attr('y', NODE_H / 2 + 1)
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'middle')
        .attr('font-size', 12)
        .attr('fill', '#1a1a1a')
        .text((d) => d.label);

      if (editMode && onPositionChange) {
        const drag = d3
          .drag<SVGGElement, D3SimNode>()
          .on('start', (_ev, d) => {
            simRef.current?.alphaTarget(0.1).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on('drag', (ev, d) => {
            d.fx = ev.x;
            d.fy = ev.y;
          })
          .on('end', (_ev, d) => {
            simRef.current?.alphaTarget(0);
            d.fx = null;
            d.fy = null;
            if (d.x !== undefined && d.y !== undefined) {
              onPositionChange(d.id, d.x, d.y);
            }
          });
        nodeSel.call(drag);
      }

      const sim = d3
        .forceSimulation<D3SimNode, D3SimLink>(simNodes)
        .force(
          'link',
          d3
            .forceLink<D3SimNode, D3SimLink>(simLinks)
            .id((d) => d.id)
            .distance(160),
        )
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide(80))
        .on('tick', () => {
          linkSel
            .attr('x1', (d) => ((d.source as D3SimNode).x ?? 0) + NODE_W / 2)
            .attr('y1', (d) => ((d.source as D3SimNode).y ?? 0) + NODE_H / 2)
            .attr('x2', (d) => ((d.target as D3SimNode).x ?? 0) + NODE_W / 2)
            .attr('y2', (d) => ((d.target as D3SimNode).y ?? 0) + NODE_H / 2);
          nodeSel.attr('transform', (d) => `translate(${d.x ?? 0},${d.y ?? 0})`);
        });

      simRef.current = sim;
    },
    [onPositionChange],
  );

  return { svgRef, render };
}
