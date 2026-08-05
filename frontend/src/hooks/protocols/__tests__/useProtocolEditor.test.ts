import { describe, it, expect, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { graphToYaml, yamlToGraph, isParseError, useProtocolEditor } from '../useProtocolEditor';
import type { GraphState } from '../useProtocolEditor';

const sampleGraph: GraphState = {
  nodes: [
    {
      id: 1,
      task_id: 't1',
      task_type: 'search',
      label: 'Search',
      description: 'Run search',
      is_required: true,
      position_x: 100,
      position_y: 200,
      inputs: [],
      outputs: [],
      quality_gates: [],
      assignees: [],
    },
  ],
  edges: [
    {
      id: 1,
      edge_id: 'e1',
      source_task_id: 't1',
      source_output_name: 'papers',
      target_task_id: 't2',
      target_input_name: 'candidates',
      condition: null,
    },
  ],
};

const sampleProtocol = {
  id: 1,
  name: 'Test',
  study_type: 'sms',
  is_default_template: false,
  owner_user_id: 1,
  version_id: 1,
  description: null,
  nodes: sampleGraph.nodes,
  edges: sampleGraph.edges,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

describe('graphToYaml', () => {
  it('serializes graph to YAML string', () => {
    const yaml = graphToYaml(sampleGraph);
    expect(yaml).toContain('task_id: t1');
    expect(yaml).toContain('edge_id: e1');
  });
});

describe('yamlToGraph', () => {
  it('parses valid YAML back to graph', () => {
    const yaml = graphToYaml(sampleGraph);
    const result = yamlToGraph(yaml);
    expect(isParseError(result)).toBe(false);
    if (!isParseError(result)) {
      expect(result.nodes).toHaveLength(1);
      expect(result.edges).toHaveLength(1);
    }
  });

  it('returns error for non-object YAML', () => {
    const result = yamlToGraph('just a string');
    expect(isParseError(result)).toBe(true);
  });

  it('returns error for invalid YAML syntax', () => {
    const result = yamlToGraph('{{invalid');
    expect(isParseError(result)).toBe(true);
  });
});

describe('isParseError', () => {
  it('returns true for error objects', () => {
    expect(isParseError({ error: 'fail' })).toBe(true);
  });

  it('returns false for graph objects', () => {
    expect(isParseError({ nodes: [], edges: [] })).toBe(false);
  });
});

describe('useProtocolEditor', () => {
  it('initializes from protocol', () => {
    const { result } = renderHook(() => useProtocolEditor(sampleProtocol as never));
    expect(result.current.graph.nodes).toHaveLength(1);
    expect(result.current.yamlText).toContain('t1');
    expect(result.current.yamlError).toBeNull();
    expect(result.current.selectedNode).toBeNull();
  });

  it('dispatches SET_GRAPH action', () => {
    const { result } = renderHook(() => useProtocolEditor(sampleProtocol as never));
    act(() => {
      result.current.dispatch({ type: 'SET_GRAPH', payload: { nodes: [], edges: [] } });
    });
    expect(result.current.graph.nodes).toHaveLength(0);
  });

  it('dispatches SELECT_NODE action', () => {
    const { result } = renderHook(() => useProtocolEditor(sampleProtocol as never));
    act(() => {
      result.current.dispatch({ type: 'SELECT_NODE', payload: { task_id: 't1' } });
    });
    expect(result.current.selectedNode).not.toBeNull();
    expect(result.current.selectedNode?.task_id).toBe('t1');
  });

  it('dispatchYamlDebounced updates after delay', async () => {
    vi.useFakeTimers();
    const { result } = renderHook(() => useProtocolEditor(sampleProtocol as never));
    act(() => {
      result.current.dispatchYamlDebounced('nodes: []\nedges: []\n');
    });
    act(() => {
      vi.advanceTimersByTime(350);
    });
    expect(result.current.graph.nodes).toHaveLength(0);
    vi.useRealTimers();
  });
});
