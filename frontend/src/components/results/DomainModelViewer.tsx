/**
 * DomainModelViewer: renders a D3.js force-directed graph of the domain model
 * concepts and relationships. Provides an "Export SVG" button that serialises
 * the current SVG node to a downloadable file.
 */

import { useEffect, useRef } from 'react';

interface Concept {
  name: string;
  definition: string;
  attributes: string[];
}

interface Relationship {
  from: string;
  to: string;
  label: string;
  type: string;
}

interface DomainModel {
  id: number;
  version: number;
  concepts: Concept[] | null;
  relationships: Relationship[] | null;
}

interface DomainModelViewerProps {
  domainModel: DomainModel;
}

export default function DomainModelViewer({ domainModel }: DomainModelViewerProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const concepts = domainModel.concepts ?? [];
  const relationships = domainModel.relationships ?? [];

  useEffect(() => {
    if (!svgRef.current || concepts.length === 0) return;

    void renderGraph(svgRef.current, concepts, relationships);
  }, [concepts, relationships]);

  const handleExportSvg = () => {
    if (!svgRef.current) return;
    const serialiser = new XMLSerializer();
    const svgStr = serialiser.serializeToString(svgRef.current);
    const blob = new Blob([svgStr], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `domain_model_v${domainModel.version}.svg`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (concepts.length === 0) {
    return (
      <div style={emptyStyle}>
        Domain model not available. Generate results first.
      </div>
    );
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
        <span style={{ fontSize: '0.8125rem', color: '#6b7280' }}>
          {concepts.length} concepts · {relationships.length} relationships · v{domainModel.version}
        </span>
        <button onClick={handleExportSvg} style={exportBtnStyle}>
          Export SVG
        </button>
      </div>
      <div style={svgContainerStyle}>
        <svg
          ref={svgRef}
          width="100%"
          height="480"
          style={{ display: 'block' }}
        />
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// D3 graph renderer (dynamic import to avoid SSR issues)
// ---------------------------------------------------------------------------

async function renderGraph(
  svgEl: SVGSVGElement,
  concepts: Concept[],
  relationships: Relationship[],
): Promise<void> {
  const d3 = await import('d3');

  // Clear any previous render
  d3.select(svgEl).selectAll('*').remove();

  const width = svgEl.clientWidth || 700;
  const height = 480;

  const nodeById = new Map(concepts.map((c) => [c.name, c]));

  // Build D3 nodes and links
  const nodes = concepts.map((c) => ({ id: c.name, definition: c.definition }));
  const links = relationships
    .filter((r) => nodeById.has(r.from) && nodeById.has(r.to))
    .map((r) => ({ source: r.from, target: r.to, label: r.label, type: r.type }));

  const simulation = d3
    .forceSimulation(nodes as d3.SimulationNodeDatum[])
    .force('link', d3.forceLink(links).id((d: any) => d.id).distance(120))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide(40));

  const svg = d3.select(svgEl).attr('viewBox', `0 0 ${width} ${height}`);

  // Arrow marker
  svg
    .append('defs')
    .append('marker')
    .attr('id', 'arrowhead')
    .attr('viewBox', '0 -5 10 10')
    .attr('refX', 24)
    .attr('refY', 0)
    .attr('markerWidth', 6)
    .attr('markerHeight', 6)
    .attr('orient', 'auto')
    .append('path')
    .attr('d', 'M0,-5L10,0L0,5')
    .attr('fill', '#94a3b8');

  const link = svg
    .append('g')
    .selectAll('line')
    .data(links)
    .enter()
    .append('line')
    .attr('stroke', '#94a3b8')
    .attr('stroke-width', 1.5)
    .attr('marker-end', 'url(#arrowhead)');

  const linkLabel = svg
    .append('g')
    .selectAll('text')
    .data(links)
    .enter()
    .append('text')
    .text((d: any) => d.label)
    .attr('font-size', '9px')
    .attr('fill', '#64748b')
    .attr('text-anchor', 'middle');

  const nodeGroup = svg
    .append('g')
    .selectAll('g')
    .data(nodes)
    .enter()
    .append('g')
    .call(
      d3
        .drag<SVGGElement, any>()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }),
    );

  nodeGroup
    .append('circle')
    .attr('r', 22)
    .attr('fill', '#dbeafe')
    .attr('stroke', '#3b82f6')
    .attr('stroke-width', 1.5);

  nodeGroup
    .append('text')
    .text((d: any) => d.id.length > 12 ? d.id.slice(0, 11) + '…' : d.id)
    .attr('text-anchor', 'middle')
    .attr('dy', '0.35em')
    .attr('font-size', '9px')
    .attr('fill', '#1e40af');

  nodeGroup.append('title').text((d: any) => d.definition || d.id);

  simulation.on('tick', () => {
    link
      .attr('x1', (d: any) => d.source.x)
      .attr('y1', (d: any) => d.source.y)
      .attr('x2', (d: any) => d.target.x)
      .attr('y2', (d: any) => d.target.y);

    linkLabel
      .attr('x', (d: any) => (d.source.x + d.target.x) / 2)
      .attr('y', (d: any) => (d.source.y + d.target.y) / 2);

    nodeGroup.attr('transform', (d: any) => `translate(${d.x},${d.y})`);
  });
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const svgContainerStyle: React.CSSProperties = {
  border: '1px solid #e2e8f0',
  borderRadius: '0.5rem',
  background: '#f8fafc',
  overflow: 'hidden',
};

const exportBtnStyle: React.CSSProperties = {
  padding: '0.25rem 0.75rem',
  background: '#eff6ff',
  color: '#2563eb',
  border: '1px solid #bfdbfe',
  borderRadius: '0.375rem',
  cursor: 'pointer',
  fontSize: '0.8125rem',
  fontWeight: 600,
};

const emptyStyle: React.CSSProperties = {
  padding: '2rem',
  textAlign: 'center',
  color: '#6b7280',
  fontSize: '0.875rem',
  border: '1px dashed #d1d5db',
  borderRadius: '0.5rem',
};
