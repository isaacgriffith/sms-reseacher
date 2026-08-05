/**
 * Unit tests for protocols/protocolsApi.ts (feature 010).
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  listProtocols,
  getProtocol,
  getProtocolAssignment,
  copyProtocol,
  createProtocol,
  updateProtocol,
  deleteProtocol,
  assignProtocol,
  getExecutionState,
  completeTask,
  approveTask,
  resetProtocol,
  exportProtocol,
  importProtocol,
} from '../protocolsApi';
import { api } from '../../api';

vi.mock('../../api', () => ({
  api: { get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() },
  ApiError: class extends Error {
    status: number;
    constructor(status: number, detail: string) {
      super(detail);
      this.status = status;
    }
  },
}));
vi.mock('../../auth', () => ({ getToken: vi.fn().mockReturnValue('tok') }));

const mockApi = vi.mocked(api);

const NODE = {
  id: 1,
  task_id: 't1',
  task_type: 'search',
  label: 'Search',
  description: null,
  is_required: true,
  position_x: null,
  position_y: null,
  inputs: [],
  outputs: [],
  assignees: [],
  quality_gates: [],
};

const DETAIL = {
  id: 1,
  name: 'Test',
  study_type: 'sms',
  is_default_template: true,
  owner_user_id: null,
  version_id: 1,
  description: null,
  nodes: [NODE],
  edges: [],
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

const LIST_ITEM = {
  id: 1,
  name: 'Test',
  study_type: 'sms',
  is_default_template: true,
  owner_user_id: null,
  version_id: 1,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

const ASSIGNMENT = {
  study_id: 42,
  protocol_id: 1,
  protocol_name: 'Test',
  is_default_template: true,
  assigned_at: '2026-01-01T00:00:00Z',
  assigned_by_user_id: null,
};

const EXEC_STATE = {
  study_id: 42,
  protocol_id: 1,
  tasks: [
    {
      node_id: 1,
      task_id: 't1',
      task_type: 'search',
      label: 'Search',
      status: 'pending',
      activated_at: null,
      completed_at: null,
      gate_failure_detail: null,
    },
  ],
};

const COMPLETE_RESP = {
  completed_task_id: 't1',
  gate_result: 'passed',
  gate_failure_detail: null,
  newly_activated_task_ids: ['t2'],
  all_tasks: EXEC_STATE.tasks,
};

describe('listProtocols', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('calls GET without filter', async () => {
    mockApi.get.mockResolvedValue([LIST_ITEM]);
    const result = await listProtocols();
    expect(mockApi.get).toHaveBeenCalledWith('/api/v1/protocols');
    expect(result).toHaveLength(1);
  });
  it('calls GET with study_type filter', async () => {
    mockApi.get.mockResolvedValue([LIST_ITEM]);
    await listProtocols('sms');
    expect(mockApi.get).toHaveBeenCalledWith('/api/v1/protocols?study_type=sms');
  });
});

describe('getProtocol', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('fetches and parses detail', async () => {
    mockApi.get.mockResolvedValue(DETAIL);
    const result = await getProtocol(1);
    expect(result.nodes).toHaveLength(1);
  });
});

describe('getProtocolAssignment', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('fetches assignment', async () => {
    mockApi.get.mockResolvedValue(ASSIGNMENT);
    const result = await getProtocolAssignment(42);
    expect(result.protocol_id).toBe(1);
  });
});

describe('copyProtocol', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('posts copy request', async () => {
    mockApi.post.mockResolvedValue(DETAIL);
    await copyProtocol({ name: 'Copy', copy_from_protocol_id: 1 });
    expect(mockApi.post).toHaveBeenCalledWith('/api/v1/protocols', {
      name: 'Copy',
      copy_from_protocol_id: 1,
    });
  });
});

describe('createProtocol', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('posts create request', async () => {
    mockApi.post.mockResolvedValue(DETAIL);
    await createProtocol({ name: 'New', study_type: 'sms', nodes: [], edges: [] });
    expect(mockApi.post).toHaveBeenCalled();
  });
});

describe('updateProtocol', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('puts update request', async () => {
    mockApi.put.mockResolvedValue(DETAIL);
    await updateProtocol({ id: 1, version_id: 1, name: 'Updated', nodes: [], edges: [] });
    expect(mockApi.put).toHaveBeenCalledWith('/api/v1/protocols/1', {
      version_id: 1,
      name: 'Updated',
      nodes: [],
      edges: [],
    });
  });
});

describe('deleteProtocol', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('deletes protocol', async () => {
    mockApi.delete.mockResolvedValue(undefined);
    await deleteProtocol(1);
    expect(mockApi.delete).toHaveBeenCalledWith('/api/v1/protocols/1');
  });
});

describe('assignProtocol', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('assigns protocol to study', async () => {
    mockApi.put.mockResolvedValue(ASSIGNMENT);
    const result = await assignProtocol(42, 1);
    expect(result.study_id).toBe(42);
  });
});

describe('getExecutionState', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('fetches execution state', async () => {
    mockApi.get.mockResolvedValue(EXEC_STATE);
    const result = await getExecutionState(42);
    expect(result.tasks).toHaveLength(1);
  });
});

describe('completeTask', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('posts complete request', async () => {
    mockApi.post.mockResolvedValue(COMPLETE_RESP);
    const result = await completeTask(42, 't1');
    expect(result.gate_result).toBe('passed');
  });
});

describe('approveTask', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('posts approve request', async () => {
    mockApi.post.mockResolvedValue(COMPLETE_RESP);
    const result = await approveTask(42, 't1');
    expect(result.completed_task_id).toBe('t1');
  });
});

describe('resetProtocol', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('sends DELETE with confirm_reset body', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(ASSIGNMENT),
    });
    vi.stubGlobal('fetch', mockFetch);
    const result = await resetProtocol(42);
    expect(mockFetch).toHaveBeenCalledWith(
      '/api/v1/studies/42/protocol-assignment',
      expect.objectContaining({ method: 'DELETE' }),
    );
    expect(result.study_id).toBe(42);
    vi.unstubAllGlobals();
  });

  it('throws ApiError on failure', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      statusText: 'Not Found',
      json: () => Promise.resolve({ detail: 'not found' }),
    });
    vi.stubGlobal('fetch', mockFetch);
    await expect(resetProtocol(42)).rejects.toThrow('not found');
    vi.unstubAllGlobals();
  });

  it('handles json parse failure in error path', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      statusText: 'Server Error',
      json: () => Promise.reject(new Error('bad json')),
    });
    vi.stubGlobal('fetch', mockFetch);
    await expect(resetProtocol(42)).rejects.toThrow('Server Error');
    vi.unstubAllGlobals();
  });
});

describe('exportProtocol', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('downloads blob as file', async () => {
    const mockBlob = new Blob(['yaml']);
    const mockClick = vi.fn();
    const mockCreateElement = vi.spyOn(document, 'createElement').mockReturnValue({
      href: '',
      download: '',
      click: mockClick,
    } as unknown as HTMLAnchorElement);
    const mockCreateObjectURL = vi.fn().mockReturnValue('blob:url');
    const mockRevokeObjectURL = vi.fn();
    vi.stubGlobal('URL', {
      createObjectURL: mockCreateObjectURL,
      revokeObjectURL: mockRevokeObjectURL,
    });

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      blob: () => Promise.resolve(mockBlob),
      headers: new Headers({ 'Content-Disposition': 'attachment; filename="proto.yaml"' }),
    });
    vi.stubGlobal('fetch', mockFetch);
    await exportProtocol(1);
    expect(mockClick).toHaveBeenCalled();
    mockCreateElement.mockRestore();
    vi.unstubAllGlobals();
  });

  it('throws on non-ok response', async () => {
    const mockFetch = vi.fn().mockResolvedValue({ ok: false, status: 500 });
    vi.stubGlobal('fetch', mockFetch);
    await expect(exportProtocol(1)).rejects.toThrow();
    vi.unstubAllGlobals();
  });
});

describe('importProtocol', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('uploads file and returns protocol', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(DETAIL),
    });
    vi.stubGlobal('fetch', mockFetch);
    const file = new File(['yaml'], 'test.yaml', { type: 'text/yaml' });
    const result = await importProtocol(file);
    expect(result.name).toBe('Test');
    vi.unstubAllGlobals();
  });

  it('throws on failure with detail', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 400,
      statusText: 'Bad Request',
      json: () => Promise.resolve({ detail: 'invalid yaml' }),
    });
    vi.stubGlobal('fetch', mockFetch);
    const file = new File(['bad'], 'test.yaml');
    await expect(importProtocol(file)).rejects.toThrow('invalid yaml');
    vi.unstubAllGlobals();
  });

  it('handles json parse failure in error path', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      statusText: 'Error',
      json: () => Promise.reject(new Error('bad')),
    });
    vi.stubGlobal('fetch', mockFetch);
    const file = new File(['bad'], 'test.yaml');
    await expect(importProtocol(file)).rejects.toThrow('Error');
    vi.unstubAllGlobals();
  });
});
