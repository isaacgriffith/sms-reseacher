/**
 * Graph editor state management hook for the dual-pane protocol editor (feature 010).
 *
 * Uses useReducer with a graphReducer to manage node/edge mutations.
 * Provides bidirectional sync between graph state and YAML text representation.
 *
 * YAML serialization uses js-yaml (available as transitive dependency).
 * Graph↔YAML sync: typing in YAML triggers graphState update after 300ms debounce;
 * graph edits immediately update yamlText.
 */

import { useReducer, useCallback, useMemo, useRef } from 'react';
import * as jsyaml from 'js-yaml';
import type {
  ProtocolDetail,
  ProtocolNode,
  ProtocolEdge,
} from '../../services/protocols/protocolsApi';

// ---------------------------------------------------------------------------
// State shape
// ---------------------------------------------------------------------------

/** Mutable copy of a protocol node for editor use. */
export interface EditorNode extends ProtocolNode {
  position_x: number;
  position_y: number;
}

/** Mutable copy of a protocol edge for editor use. */
export type EditorEdge = ProtocolEdge;

/** Complete graph state managed by the editor reducer. */
export interface GraphState {
  nodes: EditorNode[];
  edges: EditorEdge[];
}

// ---------------------------------------------------------------------------
// T046 — YAML serialization utilities
// ---------------------------------------------------------------------------

/** Parse error returned when YAML text cannot be converted to a valid GraphState. */
export interface ParseError {
  error: string;
}

/**
 * Serialize a graph state to YAML string.
 *
 * @param graph - Graph state to serialize.
 * @returns YAML string representation.
 */
export function graphToYaml(graph: GraphState): string {
  return jsyaml.dump(
    {
      nodes: graph.nodes.map((n) => ({
        task_id: n.task_id,
        task_type: n.task_type,
        label: n.label,
        description: n.description,
        is_required: n.is_required,
        position_x: n.position_x,
        position_y: n.position_y,
        inputs: n.inputs,
        outputs: n.outputs,
        quality_gates: n.quality_gates,
        assignees: n.assignees,
      })),
      edges: graph.edges.map((e) => ({
        edge_id: e.edge_id,
        source_task_id: e.source_task_id,
        source_output_name: e.source_output_name,
        target_task_id: e.target_task_id,
        target_input_name: e.target_input_name,
        condition: e.condition ?? null,
      })),
    },
    { lineWidth: -1 },
  );
}

/**
 * Parse a YAML string into a GraphState.
 *
 * @param yaml - YAML text to parse.
 * @returns Parsed {@link GraphState} or a {@link ParseError} if parsing fails.
 */
export function yamlToGraph(yaml: string): GraphState | ParseError {
  try {
    const raw = jsyaml.load(yaml) as Record<string, unknown>;
    if (!raw || typeof raw !== 'object') {
      return { error: 'YAML must represent a mapping with nodes and edges.' };
    }
    const nodes = (raw['nodes'] as EditorNode[]) ?? [];
    const edges = (raw['edges'] as EditorEdge[]) ?? [];
    if (!Array.isArray(nodes) || !Array.isArray(edges)) {
      return { error: "'nodes' and 'edges' must be arrays." };
    }
    return {
      nodes: nodes.map((n) => ({
        ...n,
        id: n.id ?? 0,
        inputs: n.inputs ?? [],
        outputs: n.outputs ?? [],
        quality_gates: n.quality_gates ?? [],
        assignees: n.assignees ?? [],
        position_x: n.position_x ?? 0,
        position_y: n.position_y ?? 0,
      })),
      edges: edges.map((e) => ({
        ...e,
        id: e.id ?? 0,
        condition: e.condition ?? null,
      })),
    };
  } catch (err) {
    return { error: String(err) };
  }
}

/** Type guard for ParseError. */
export function isParseError(v: GraphState | ParseError): v is ParseError {
  return 'error' in v;
}

// ---------------------------------------------------------------------------
// T045 — Reducer actions
// ---------------------------------------------------------------------------

type Action =
  | { type: 'SET_GRAPH'; payload: GraphState }
  | { type: 'ADD_NODE'; payload: EditorNode }
  | { type: 'REMOVE_NODE'; payload: { task_id: string } }
  | { type: 'UPDATE_NODE'; payload: Partial<EditorNode> & { task_id: string } }
  | { type: 'ADD_EDGE'; payload: EditorEdge }
  | { type: 'REMOVE_EDGE'; payload: { edge_id: string } }
  | { type: 'UPDATE_EDGE'; payload: Partial<EditorEdge> & { edge_id: string } }
  | { type: 'SELECT_NODE'; payload: { task_id: string | null } }
  | { type: 'SET_YAML'; payload: { yaml: string } };

interface EditorState {
  graph: GraphState;
  selectedTaskId: string | null;
  yamlText: string;
  yamlError: string | null;
}

function graphReducer(state: EditorState, action: Action): EditorState {
  switch (action.type) {
    case 'SET_GRAPH': {
      return {
        ...state,
        graph: action.payload,
        yamlText: graphToYaml(action.payload),
        yamlError: null,
      };
    }
    case 'ADD_NODE': {
      const graph = { ...state.graph, nodes: [...state.graph.nodes, action.payload] };
      return { ...state, graph, yamlText: graphToYaml(graph) };
    }
    case 'REMOVE_NODE': {
      const graph = {
        nodes: state.graph.nodes.filter((n) => n.task_id !== action.payload.task_id),
        edges: state.graph.edges.filter(
          (e) =>
            e.source_task_id !== action.payload.task_id &&
            e.target_task_id !== action.payload.task_id,
        ),
      };
      return { ...state, graph, yamlText: graphToYaml(graph) };
    }
    case 'UPDATE_NODE': {
      const graph = {
        ...state.graph,
        nodes: state.graph.nodes.map((n) =>
          n.task_id === action.payload.task_id ? { ...n, ...action.payload } : n,
        ),
      };
      return { ...state, graph, yamlText: graphToYaml(graph) };
    }
    case 'ADD_EDGE': {
      const graph = { ...state.graph, edges: [...state.graph.edges, action.payload] };
      return { ...state, graph, yamlText: graphToYaml(graph) };
    }
    case 'REMOVE_EDGE': {
      const graph = {
        ...state.graph,
        edges: state.graph.edges.filter((e) => e.edge_id !== action.payload.edge_id),
      };
      return { ...state, graph, yamlText: graphToYaml(graph) };
    }
    case 'UPDATE_EDGE': {
      const graph = {
        ...state.graph,
        edges: state.graph.edges.map((e) =>
          e.edge_id === action.payload.edge_id ? { ...e, ...action.payload } : e,
        ),
      };
      return { ...state, graph, yamlText: graphToYaml(graph) };
    }
    case 'SELECT_NODE': {
      return { ...state, selectedTaskId: action.payload.task_id };
    }
    case 'SET_YAML': {
      const parsed = yamlToGraph(action.payload.yaml);
      if (isParseError(parsed)) {
        return { ...state, yamlText: action.payload.yaml, yamlError: parsed.error };
      }
      return { ...state, yamlText: action.payload.yaml, graph: parsed, yamlError: null };
    }
    default:
      return state;
  }
}

// ---------------------------------------------------------------------------
// useProtocolEditor hook
// ---------------------------------------------------------------------------

function protocolToGraph(protocol: ProtocolDetail): GraphState {
  return {
    nodes: protocol.nodes.map((n) => ({
      ...n,
      position_x: n.position_x ?? 0,
      position_y: n.position_y ?? 0,
    })),
    edges: protocol.edges,
  };
}

/**
 * Editor state hook for the dual-pane protocol editor.
 *
 * Initialises from a {@link ProtocolDetail} and exposes graph state,
 * YAML text, parse errors, selected node, and a dispatch function.
 *
 * @param initial - Initial protocol detail to edit.
 * @returns Editor state and dispatch.
 */
export function useProtocolEditor(initial: ProtocolDetail) {
  const initGraph = useMemo(() => protocolToGraph(initial), []); // eslint-disable-line react-hooks/exhaustive-deps
  const [state, dispatch] = useReducer(graphReducer, {
    graph: initGraph,
    selectedTaskId: null,
    yamlText: graphToYaml(initGraph),
    yamlError: null,
  });

  // Debounced YAML dispatch — only used externally via debounce ref
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const dispatchYamlDebounced = useCallback((yaml: string) => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      dispatch({ type: 'SET_YAML', payload: { yaml } });
    }, 300);
  }, []);

  const selectedNode = useMemo(
    () => state.graph.nodes.find((n) => n.task_id === state.selectedTaskId) ?? null,
    [state.graph.nodes, state.selectedTaskId],
  );

  return {
    graph: state.graph,
    yamlText: state.yamlText,
    yamlError: state.yamlError,
    selectedNode,
    dispatch,
    dispatchYamlDebounced,
  };
}
