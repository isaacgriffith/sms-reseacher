/**
 * ExtractionView: displays and inline-edits all extraction fields for one
 * accepted paper. Sends PATCH with the current version_id for optimistic
 * locking; calls onConflict when the server returns HTTP 409.
 */
// @ts-nocheck
function stryNS_9fa48() {
  var g = typeof globalThis === 'object' && globalThis && globalThis.Math === Math && globalThis || new Function("return this")();
  var ns = g.__stryker__ || (g.__stryker__ = {});
  if (ns.activeMutant === undefined && g.process && g.process.env && g.process.env.__STRYKER_ACTIVE_MUTANT__) {
    ns.activeMutant = g.process.env.__STRYKER_ACTIVE_MUTANT__;
  }
  function retrieveNS() {
    return ns;
  }
  stryNS_9fa48 = retrieveNS;
  return retrieveNS();
}
stryNS_9fa48();
function stryCov_9fa48() {
  var ns = stryNS_9fa48();
  var cov = ns.mutantCoverage || (ns.mutantCoverage = {
    static: {},
    perTest: {}
  });
  function cover() {
    var c = cov.static;
    if (ns.currentTestId) {
      c = cov.perTest[ns.currentTestId] = cov.perTest[ns.currentTestId] || {};
    }
    var a = arguments;
    for (var i = 0; i < a.length; i++) {
      c[a[i]] = (c[a[i]] || 0) + 1;
    }
  }
  stryCov_9fa48 = cover;
  cover.apply(null, arguments);
}
function stryMutAct_9fa48(id) {
  var ns = stryNS_9fa48();
  function isActive(id) {
    if (ns.activeMutant === id) {
      if (ns.hitCount !== void 0 && ++ns.hitCount > ns.hitLimit) {
        throw new Error('Stryker: Hit count limit reached (' + ns.hitCount + ')');
      }
      return true;
    }
    return false;
  }
  stryMutAct_9fa48 = isActive;
  return isActive(id);
}
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, ApiError } from '../../services/api';
interface Extraction {
  id: number;
  candidate_paper_id: number;
  research_type: string;
  venue_type: string;
  venue_name: string | null;
  author_details: Array<{
    name: string;
    institution: string | null;
    locale: string | null;
  }> | null;
  summary: string | null;
  open_codings: Array<{
    code: string;
    definition: string;
    evidence_quote: string;
  }> | null;
  keywords: string[] | null;
  question_data: Record<string, unknown> | null;
  extraction_status: 'pending' | 'ai_complete' | 'validated' | 'human_reviewed';
  version_id: number;
  extracted_by_agent: string | null;
  conflict_flag: boolean;
}
interface ConflictPayload {
  error: string;
  your_version: Record<string, unknown>;
  current_version: Record<string, unknown>;
}
interface PatchBody {
  version_id: number;
  venue_type?: string;
  venue_name?: string | null;
  summary?: string | null;
  research_type?: string;
  keywords?: string[] | null;
}
interface ExtractionViewProps {
  studyId: number;
  extractionId: number;
  /** Called with the 409 payload when a concurrent edit conflict is detected. */
  onConflict: (payload: ConflictPayload) => void;
}
const STATUS_COLORS: Record<string, string> = {
  pending: '#d97706',
  ai_complete: '#2563eb',
  validated: '#16a34a',
  human_reviewed: '#7c3aed'
};
const RESEARCH_TYPES = stryMutAct_9fa48("1230") ? [] : (stryCov_9fa48("1230"), ['evaluation', 'solution_proposal', 'validation', 'philosophical', 'opinion', 'personal_experience', 'unknown']);
export default function ExtractionView({
  studyId,
  extractionId,
  onConflict
}: ExtractionViewProps) {
  if (stryMutAct_9fa48("1238")) {
    {}
  } else {
    stryCov_9fa48("1238");
    const queryClient = useQueryClient();
    const [editingField, setEditingField] = useState<string | null>(null);
    const {
      data: extraction,
      isLoading,
      error
    } = useQuery<Extraction>({
      queryKey: stryMutAct_9fa48("1240") ? [] : (stryCov_9fa48("1240"), ['extraction', studyId, extractionId]),
      queryFn: stryMutAct_9fa48("1242") ? () => undefined : (stryCov_9fa48("1242"), () => api.get<Extraction>(`/api/v1/studies/${studyId}/extractions/${extractionId}`))
    });
    const {
      register,
      handleSubmit,
      reset
    } = useForm<PatchBody>();
    const mutation = useMutation({
      mutationFn: stryMutAct_9fa48("1245") ? () => undefined : (stryCov_9fa48("1245"), (body: PatchBody) => api.patch<Extraction>(`/api/v1/studies/${studyId}/extractions/${extractionId}`, body)),
      onSuccess: () => {
        if (stryMutAct_9fa48("1247")) {
          {}
        } else {
          stryCov_9fa48("1247");
          queryClient.invalidateQueries({
            queryKey: stryMutAct_9fa48("1249") ? [] : (stryCov_9fa48("1249"), ['extraction', studyId, extractionId])
          });
          setEditingField(null);
        }
      },
      onError: (err: unknown) => {
        if (stryMutAct_9fa48("1251")) {
          {}
        } else {
          stryCov_9fa48("1251");
          if (stryMutAct_9fa48("1254") ? err instanceof ApiError || err.status === 409 : stryMutAct_9fa48("1253") ? false : stryMutAct_9fa48("1252") ? true : (stryCov_9fa48("1252", "1253", "1254"), err instanceof ApiError && (stryMutAct_9fa48("1256") ? err.status !== 409 : stryMutAct_9fa48("1255") ? true : (stryCov_9fa48("1255", "1256"), err.status === 409)))) {
            if (stryMutAct_9fa48("1257")) {
              {}
            } else {
              stryCov_9fa48("1257");
              const payload = err.detail as unknown as ConflictPayload;
              onConflict(payload);
            }
          }
        }
      }
    });
    const handleSave = handleSubmit(data => {
      if (stryMutAct_9fa48("1258")) {
        {}
      } else {
        stryCov_9fa48("1258");
        if (stryMutAct_9fa48("1261") ? false : stryMutAct_9fa48("1260") ? true : stryMutAct_9fa48("1259") ? extraction : (stryCov_9fa48("1259", "1260", "1261"), !extraction)) return;
        mutation.mutate({
          ...data,
          version_id: extraction.version_id
        });
        reset();
      }
    });
    const handleCancel = () => {
      if (stryMutAct_9fa48("1263")) {
        {}
      } else {
        stryCov_9fa48("1263");
        setEditingField(null);
        reset();
      }
    };
    if (stryMutAct_9fa48("1265") ? false : stryMutAct_9fa48("1264") ? true : (stryCov_9fa48("1264", "1265"), isLoading)) return <p style={{
      color: '#6b7280',
      fontSize: '0.875rem'
    }}>Loading extraction…</p>;
    if (stryMutAct_9fa48("1271") ? error && !extraction : stryMutAct_9fa48("1270") ? false : stryMutAct_9fa48("1269") ? true : (stryCov_9fa48("1269", "1270", "1271"), error || (stryMutAct_9fa48("1272") ? extraction : (stryCov_9fa48("1272"), !extraction)))) return <p style={{
      color: '#ef4444',
      fontSize: '0.875rem'
    }}>Failed to load extraction.</p>;
    const statusColor = stryMutAct_9fa48("1276") ? STATUS_COLORS[extraction.extraction_status] && '#6b7280' : (stryCov_9fa48("1276"), STATUS_COLORS[extraction.extraction_status] ?? '#6b7280');
    return <div style={{
      fontFamily: 'inherit'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '1.25rem'
      }}>
        <h3 style={{
          margin: 0,
          fontSize: '1rem',
          color: '#111827'
        }}>Data Extraction</h3>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          {stryMutAct_9fa48("1294") ? extraction.conflict_flag || <span style={{
            padding: '0.125rem 0.5rem',
            background: '#fef2f2',
            color: '#dc2626',
            borderRadius: '9999px',
            fontSize: '0.75rem',
            fontWeight: 600
          }}>
              Conflict
            </span> : stryMutAct_9fa48("1293") ? false : stryMutAct_9fa48("1292") ? true : (stryCov_9fa48("1292", "1293", "1294"), extraction.conflict_flag && <span style={{
            padding: '0.125rem 0.5rem',
            background: '#fef2f2',
            color: '#dc2626',
            borderRadius: '9999px',
            fontSize: '0.75rem',
            fontWeight: 600
          }}>
              Conflict
            </span>)}
          <span style={{
            padding: '0.125rem 0.5rem',
            background: `${statusColor}18`,
            color: statusColor,
            borderRadius: '9999px',
            fontSize: '0.75rem',
            fontWeight: 600,
            textTransform: 'capitalize'
          }}>
            {extraction.extraction_status.replace('_', ' ')}
          </span>
        </div>
      </div>

      <form onSubmit={handleSave}>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem'
        }}>
          {/* Research Type */}
          <Field label="Research Type" fieldKey="research_type" editingField={editingField} onEdit={setEditingField} onCancel={handleCancel} onSave={handleSave} display={<span style={{
            textTransform: 'capitalize'
          }}>{extraction.research_type.replace('_', ' ')}</span>} input={<select {...register('research_type')} defaultValue={extraction.research_type} style={selectStyle}>
                {RESEARCH_TYPES.map(stryMutAct_9fa48("1318") ? () => undefined : (stryCov_9fa48("1318"), rt => <option key={rt} value={rt}>{rt.replace('_', ' ')}</option>))}
              </select>} />

          {/* Venue Type */}
          <Field label="Venue Type" fieldKey="venue_type" editingField={editingField} onEdit={setEditingField} onCancel={handleCancel} onSave={handleSave} display={<span>{stryMutAct_9fa48("1323") ? extraction.venue_type && '—' : stryMutAct_9fa48("1322") ? false : stryMutAct_9fa48("1321") ? true : (stryCov_9fa48("1321", "1322", "1323"), extraction.venue_type || '—')}</span>} input={<input {...register('venue_type')} defaultValue={extraction.venue_type} style={inputStyle} />} />

          {/* Venue Name */}
          <Field label="Venue Name" fieldKey="venue_name" editingField={editingField} onEdit={setEditingField} onCancel={handleCancel} onSave={handleSave} display={<span>{stryMutAct_9fa48("1326") ? extraction.venue_name && '—' : (stryCov_9fa48("1326"), extraction.venue_name ?? '—')}</span>} input={<input {...register('venue_name')} defaultValue={stryMutAct_9fa48("1329") ? extraction.venue_name && '' : (stryCov_9fa48("1329"), extraction.venue_name ?? '')} style={inputStyle} />} />

          {/* Summary */}
          <Field label="Summary" fieldKey="summary" editingField={editingField} onEdit={setEditingField} onCancel={handleCancel} onSave={handleSave} display={<p style={{
            margin: 0,
            fontSize: '0.875rem',
            color: '#374151',
            lineHeight: 1.6
          }}>
                {stryMutAct_9fa48("1334") ? extraction.summary && '—' : (stryCov_9fa48("1334"), extraction.summary ?? '—')}
              </p>} input={<textarea {...register('summary')} defaultValue={stryMutAct_9fa48("1337") ? extraction.summary && '' : (stryCov_9fa48("1337"), extraction.summary ?? '')} rows={4} style={{
            ...inputStyle,
            resize: 'vertical'
          }} />} />

          {/* Keywords (read-only display for now; inline edit of comma-separated) */}
          <Field label="Keywords" fieldKey="keywords" editingField={editingField} onEdit={setEditingField} onCancel={handleCancel} onSave={handleSave} display={<div style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '0.375rem'
          }}>
                {stryMutAct_9fa48("1345") ? extraction.keywords?.map(kw => <span key={kw} style={tagStyle}>{kw}</span>) && <span style={{
              color: '#9ca3af'
            }}>—</span> : (stryCov_9fa48("1345"), (stryMutAct_9fa48("1346") ? extraction.keywords.map(kw => <span key={kw} style={tagStyle}>{kw}</span>) : (stryCov_9fa48("1346"), extraction.keywords?.map(stryMutAct_9fa48("1347") ? () => undefined : (stryCov_9fa48("1347"), kw => <span key={kw} style={tagStyle}>{kw}</span>)))) ?? <span style={{
              color: '#9ca3af'
            }}>—</span>)}
              </div>} input={<input {...register('keywords', {
            setValueAs: stryMutAct_9fa48("1352") ? () => undefined : (stryCov_9fa48("1352"), (v: string) => stryMutAct_9fa48("1353") ? v.split(',').map(s => s.trim()) : (stryCov_9fa48("1353"), v.split(',').map(stryMutAct_9fa48("1355") ? () => undefined : (stryCov_9fa48("1355"), s => stryMutAct_9fa48("1356") ? s : (stryCov_9fa48("1356"), s.trim()))).filter(Boolean)))
          })} defaultValue={stryMutAct_9fa48("1357") ? extraction.keywords?.join(', ') && '' : (stryCov_9fa48("1357"), (stryMutAct_9fa48("1358") ? extraction.keywords.join(', ') : (stryCov_9fa48("1358"), extraction.keywords?.join(', '))) ?? '')} placeholder="comma-separated keywords" style={inputStyle} />} />

          {/* Open Codings — read-only list */}
          <div style={fieldContainerStyle}>
            <label style={labelStyle}>Open Codings</label>
            <div style={{
              marginTop: '0.375rem'
            }}>
              {(stryMutAct_9fa48("1363") ? extraction.open_codings.length : (stryCov_9fa48("1363"), extraction.open_codings?.length)) ? extraction.open_codings.map(stryMutAct_9fa48("1364") ? () => undefined : (stryCov_9fa48("1364"), (oc, i) => <div key={i} style={{
                marginBottom: '0.625rem',
                padding: '0.625rem',
                background: '#f8fafc',
                borderRadius: '0.375rem'
              }}>
                    <div style={{
                  fontWeight: 600,
                  fontSize: '0.8125rem',
                  color: '#1e293b'
                }}>{oc.code}</div>
                    <div style={{
                  fontSize: '0.8125rem',
                  color: '#475569',
                  marginTop: '0.25rem'
                }}>{oc.definition}</div>
                    {stryMutAct_9fa48("1379") ? oc.evidence_quote || <blockquote style={{
                  margin: '0.375rem 0 0',
                  padding: '0.375rem 0.625rem',
                  borderLeft: '3px solid #cbd5e1',
                  color: '#64748b',
                  fontSize: '0.8125rem',
                  fontStyle: 'italic'
                }}>
                        {oc.evidence_quote}
                      </blockquote> : stryMutAct_9fa48("1378") ? false : stryMutAct_9fa48("1377") ? true : (stryCov_9fa48("1377", "1378", "1379"), oc.evidence_quote && <blockquote style={{
                  margin: '0.375rem 0 0',
                  padding: '0.375rem 0.625rem',
                  borderLeft: '3px solid #cbd5e1',
                  color: '#64748b',
                  fontSize: '0.8125rem',
                  fontStyle: 'italic'
                }}>
                        {oc.evidence_quote}
                      </blockquote>)}
                  </div>)) : <span style={{
                color: '#9ca3af',
                fontSize: '0.875rem'
              }}>No open codings yet.</span>}
            </div>
          </div>

          {/* Question Data — read-only table */}
          {stryMutAct_9fa48("1392") ? extraction.question_data && Object.keys(extraction.question_data).length > 0 || <div style={fieldContainerStyle}>
              <label style={labelStyle}>Research Question Answers</label>
              <div style={{
              marginTop: '0.375rem'
            }}>
                {Object.entries(extraction.question_data).map(([qid, answer]) => <div key={qid} style={{
                display: 'grid',
                gridTemplateColumns: '8rem 1fr',
                gap: '0.5rem',
                marginBottom: '0.5rem',
                fontSize: '0.875rem'
              }}>
                    <span style={{
                  fontWeight: 600,
                  color: '#374151'
                }}>{qid}</span>
                    <span style={{
                  color: '#4b5563'
                }}>{answer != null ? String(answer) : '—'}</span>
                  </div>)}
              </div>
            </div> : stryMutAct_9fa48("1391") ? false : stryMutAct_9fa48("1390") ? true : (stryCov_9fa48("1390", "1391", "1392"), (stryMutAct_9fa48("1394") ? extraction.question_data || Object.keys(extraction.question_data).length > 0 : stryMutAct_9fa48("1393") ? true : (stryCov_9fa48("1393", "1394"), extraction.question_data && (stryMutAct_9fa48("1397") ? Object.keys(extraction.question_data).length <= 0 : stryMutAct_9fa48("1396") ? Object.keys(extraction.question_data).length >= 0 : stryMutAct_9fa48("1395") ? true : (stryCov_9fa48("1395", "1396", "1397"), Object.keys(extraction.question_data).length > 0)))) && <div style={fieldContainerStyle}>
              <label style={labelStyle}>Research Question Answers</label>
              <div style={{
              marginTop: '0.375rem'
            }}>
                {Object.entries(extraction.question_data).map(stryMutAct_9fa48("1400") ? () => undefined : (stryCov_9fa48("1400"), ([qid, answer]) => <div key={qid} style={{
                display: 'grid',
                gridTemplateColumns: '8rem 1fr',
                gap: '0.5rem',
                marginBottom: '0.5rem',
                fontSize: '0.875rem'
              }}>
                    <span style={{
                  fontWeight: 600,
                  color: '#374151'
                }}>{qid}</span>
                    <span style={{
                  color: '#4b5563'
                }}>{(stryMutAct_9fa48("1413") ? answer == null : stryMutAct_9fa48("1412") ? false : stryMutAct_9fa48("1411") ? true : (stryCov_9fa48("1411", "1412", "1413"), answer != null)) ? String(answer) : '—'}</span>
                  </div>))}
              </div>
            </div>)}
        </div>

        {stryMutAct_9fa48("1417") ? mutation.isError && !(mutation.error instanceof ApiError && (mutation.error as ApiError).status === 409) || <p style={{
          color: '#ef4444',
          fontSize: '0.8125rem',
          marginTop: '0.5rem'
        }}>Save failed. Please try again.</p> : stryMutAct_9fa48("1416") ? false : stryMutAct_9fa48("1415") ? true : (stryCov_9fa48("1415", "1416", "1417"), (stryMutAct_9fa48("1419") ? mutation.isError || !(mutation.error instanceof ApiError && (mutation.error as ApiError).status === 409) : stryMutAct_9fa48("1418") ? true : (stryCov_9fa48("1418", "1419"), mutation.isError && (stryMutAct_9fa48("1420") ? mutation.error instanceof ApiError && (mutation.error as ApiError).status === 409 : (stryCov_9fa48("1420"), !(stryMutAct_9fa48("1423") ? mutation.error instanceof ApiError || (mutation.error as ApiError).status === 409 : stryMutAct_9fa48("1422") ? false : stryMutAct_9fa48("1421") ? true : (stryCov_9fa48("1421", "1422", "1423"), mutation.error instanceof ApiError && (stryMutAct_9fa48("1425") ? (mutation.error as ApiError).status !== 409 : stryMutAct_9fa48("1424") ? true : (stryCov_9fa48("1424", "1425"), (mutation.error as ApiError).status === 409)))))))) && <p style={{
          color: '#ef4444',
          fontSize: '0.8125rem',
          marginTop: '0.5rem'
        }}>Save failed. Please try again.</p>)}
      </form>

      {stryMutAct_9fa48("1432") ? extraction.extracted_by_agent || <p style={{
        marginTop: '1rem',
        fontSize: '0.75rem',
        color: '#9ca3af'
      }}>
          Extracted by: {extraction.extracted_by_agent} · version {extraction.version_id}
        </p> : stryMutAct_9fa48("1431") ? false : stryMutAct_9fa48("1430") ? true : (stryCov_9fa48("1430", "1431", "1432"), extraction.extracted_by_agent && <p style={{
        marginTop: '1rem',
        fontSize: '0.75rem',
        color: '#9ca3af'
      }}>
          Extracted by: {extraction.extracted_by_agent} · version {extraction.version_id}
        </p>)}
    </div>;
  }
}

// ---------------------------------------------------------------------------
// Field sub-component
// ---------------------------------------------------------------------------

interface FieldProps {
  label: string;
  fieldKey: string;
  editingField: string | null;
  onEdit: (key: string) => void;
  onCancel: () => void;
  onSave: () => void;
  display: React.ReactNode;
  input: React.ReactNode;
}
function Field({
  label,
  fieldKey,
  editingField,
  onEdit,
  onCancel,
  onSave,
  display,
  input
}: FieldProps) {
  if (stryMutAct_9fa48("1437")) {
    {}
  } else {
    stryCov_9fa48("1437");
    const isEditing = stryMutAct_9fa48("1440") ? editingField !== fieldKey : stryMutAct_9fa48("1439") ? false : stryMutAct_9fa48("1438") ? true : (stryCov_9fa48("1438", "1439", "1440"), editingField === fieldKey);
    return <div style={fieldContainerStyle}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '0.25rem'
      }}>
        <label style={labelStyle}>{label}</label>
        {stryMutAct_9fa48("1448") ? !isEditing || <button type="button" onClick={() => onEdit(fieldKey)} style={editBtnStyle}>
            Edit
          </button> : stryMutAct_9fa48("1447") ? false : stryMutAct_9fa48("1446") ? true : (stryCov_9fa48("1446", "1447", "1448"), (stryMutAct_9fa48("1449") ? isEditing : (stryCov_9fa48("1449"), !isEditing)) && <button type="button" onClick={stryMutAct_9fa48("1450") ? () => undefined : (stryCov_9fa48("1450"), () => onEdit(fieldKey))} style={editBtnStyle}>
            Edit
          </button>)}
      </div>
      {isEditing ? <div>
          {input}
          <div style={{
          display: 'flex',
          gap: '0.5rem',
          marginTop: '0.5rem'
        }}>
            <button type="button" onClick={onSave} style={saveBtnStyle}>Save</button>
            <button type="button" onClick={onCancel} style={cancelBtnStyle}>Cancel</button>
          </div>
        </div> : <div style={{
        fontSize: '0.875rem',
        color: '#374151'
      }}>{display}</div>}
    </div>;
  }
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const fieldContainerStyle: React.CSSProperties = {
  padding: '0.75rem',
  border: '1px solid #e2e8f0',
  borderRadius: '0.5rem',
  background: '#fff'
};
const labelStyle: React.CSSProperties = {
  fontSize: '0.75rem',
  fontWeight: 600,
  color: '#6b7280',
  textTransform: 'uppercase',
  letterSpacing: '0.05em'
};
const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '0.375rem 0.625rem',
  border: '1px solid #d1d5db',
  borderRadius: '0.375rem',
  fontSize: '0.875rem',
  boxSizing: 'border-box'
};
const selectStyle: React.CSSProperties = {
  ...inputStyle,
  background: '#fff',
  cursor: 'pointer'
};
const tagStyle: React.CSSProperties = {
  padding: '0.125rem 0.5rem',
  background: '#eff6ff',
  color: '#1d4ed8',
  borderRadius: '9999px',
  fontSize: '0.75rem'
};
const editBtnStyle: React.CSSProperties = {
  padding: '0.125rem 0.5rem',
  background: 'transparent',
  border: '1px solid #d1d5db',
  borderRadius: '0.25rem',
  cursor: 'pointer',
  fontSize: '0.75rem',
  color: '#374151'
};
const saveBtnStyle: React.CSSProperties = {
  padding: '0.25rem 0.75rem',
  background: '#2563eb',
  color: '#fff',
  border: 'none',
  borderRadius: '0.375rem',
  cursor: 'pointer',
  fontSize: '0.8125rem'
};
const cancelBtnStyle: React.CSSProperties = {
  padding: '0.25rem 0.75rem',
  background: 'transparent',
  color: '#374151',
  border: '1px solid #d1d5db',
  borderRadius: '0.375rem',
  cursor: 'pointer',
  fontSize: '0.8125rem'
};