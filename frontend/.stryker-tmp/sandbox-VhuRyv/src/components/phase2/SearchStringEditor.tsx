/**
 * SearchStringEditor: text area for search string, AI generation, version history.
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
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api, ApiError } from '../../services/api';
interface Iteration {
  id: number;
  iteration_number: number;
  result_set_count: number;
  test_set_recall: number;
  ai_adequacy_judgment: string | null;
  human_approved: boolean | null;
}
interface SearchString {
  id: number;
  study_id: number;
  version: number;
  string_text: string;
  is_active: boolean;
  created_by_agent: string | null;
  iterations: Iteration[];
}
interface SearchStringEditorProps {
  studyId: number;
  onSearchStringCreated?: (id: number) => void;
}
export default function SearchStringEditor({
  studyId,
  onSearchStringCreated
}: SearchStringEditorProps) {
  if (stryMutAct_9fa48("772")) {
    {}
  } else {
    stryCov_9fa48("772");
    const qc = useQueryClient();
    const [manualText, setManualText] = useState('');
    const [generateError, setGenerateError] = useState<string | null>(null);
    const [selectedId, setSelectedId] = useState<number | null>(null);
    const {
      data: strings = stryMutAct_9fa48("774") ? ["Stryker was here"] : (stryCov_9fa48("774"), []),
      isLoading
    } = useQuery<SearchString[]>({
      queryKey: stryMutAct_9fa48("776") ? [] : (stryCov_9fa48("776"), ['search-strings', studyId]),
      queryFn: stryMutAct_9fa48("778") ? () => undefined : (stryCov_9fa48("778"), () => api.get<SearchString[]>(`/api/v1/studies/${studyId}/search-strings`))
    });
    const createManual = useMutation({
      mutationFn: stryMutAct_9fa48("781") ? () => undefined : (stryCov_9fa48("781"), (text: string) => api.post<SearchString>(`/api/v1/studies/${studyId}/search-strings`, {
        string_text: text
      })),
      onSuccess: ss => {
        if (stryMutAct_9fa48("784")) {
          {}
        } else {
          stryCov_9fa48("784");
          qc.invalidateQueries({
            queryKey: stryMutAct_9fa48("786") ? [] : (stryCov_9fa48("786"), ['search-strings', studyId])
          });
          setManualText('');
          setSelectedId(ss.id);
          stryMutAct_9fa48("789") ? onSearchStringCreated(ss.id) : (stryCov_9fa48("789"), onSearchStringCreated?.(ss.id));
        }
      }
    });
    const generateAI = useMutation({
      mutationFn: stryMutAct_9fa48("791") ? () => undefined : (stryCov_9fa48("791"), () => api.post<SearchString>(`/api/v1/studies/${studyId}/search-strings/generate`, {})),
      onSuccess: ss => {
        if (stryMutAct_9fa48("793")) {
          {}
        } else {
          stryCov_9fa48("793");
          setGenerateError(null);
          qc.invalidateQueries({
            queryKey: stryMutAct_9fa48("795") ? [] : (stryCov_9fa48("795"), ['search-strings', studyId])
          });
          setSelectedId(ss.id);
          stryMutAct_9fa48("797") ? onSearchStringCreated(ss.id) : (stryCov_9fa48("797"), onSearchStringCreated?.(ss.id));
        }
      },
      onError: err => {
        if (stryMutAct_9fa48("798")) {
          {}
        } else {
          stryCov_9fa48("798");
          setGenerateError(err instanceof ApiError ? err.detail : 'Generation failed');
        }
      }
    });
    const selected = selectedId ? stryMutAct_9fa48("800") ? strings.find(s => s.id === selectedId) && strings[0] : (stryCov_9fa48("800"), strings.find(stryMutAct_9fa48("801") ? () => undefined : (stryCov_9fa48("801"), s => stryMutAct_9fa48("804") ? s.id !== selectedId : stryMutAct_9fa48("803") ? false : stryMutAct_9fa48("802") ? true : (stryCov_9fa48("802", "803", "804"), s.id === selectedId))) ?? strings[0]) : strings[0];
    return <div>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '1rem'
      }}>
        <h3 style={{
          margin: 0,
          fontSize: '1rem',
          color: '#111827'
        }}>Search String</h3>
        <button onClick={stryMutAct_9fa48("813") ? () => undefined : (stryCov_9fa48("813"), () => generateAI.mutate())} disabled={generateAI.isPending} style={{
          padding: '0.375rem 0.75rem',
          background: '#7c3aed',
          color: '#fff',
          border: 'none',
          borderRadius: '0.375rem',
          cursor: generateAI.isPending ? 'not-allowed' : 'pointer',
          fontSize: '0.875rem',
          opacity: generateAI.isPending ? 0.6 : 1
        }}>
          {generateAI.isPending ? 'Generating…' : '✨ Generate with AI'}
        </button>
      </div>

      {stryMutAct_9fa48("827") ? generateError || <p style={{
        color: '#ef4444',
        fontSize: '0.875rem',
        margin: '0 0 0.75rem'
      }}>{generateError}</p> : stryMutAct_9fa48("826") ? false : stryMutAct_9fa48("825") ? true : (stryCov_9fa48("825", "826", "827"), generateError && <p style={{
        color: '#ef4444',
        fontSize: '0.875rem',
        margin: '0 0 0.75rem'
      }}>{generateError}</p>)}

      {/* Manual entry */}
      <div style={{
        marginBottom: '1rem'
      }}>
        <textarea value={manualText} onChange={stryMutAct_9fa48("834") ? () => undefined : (stryCov_9fa48("834"), e => setManualText(e.target.value))} placeholder="Enter Boolean search string manually…" rows={4} style={{
          width: '100%',
          padding: '0.5rem',
          border: '1px solid #d1d5db',
          borderRadius: '0.375rem',
          fontSize: '0.875rem',
          fontFamily: 'monospace',
          resize: 'vertical',
          boxSizing: 'border-box'
        }} />
        <button onClick={stryMutAct_9fa48("844") ? () => undefined : (stryCov_9fa48("844"), () => createManual.mutate(manualText))} disabled={stryMutAct_9fa48("847") ? createManual.isPending && !manualText.trim() : stryMutAct_9fa48("846") ? false : stryMutAct_9fa48("845") ? true : (stryCov_9fa48("845", "846", "847"), createManual.isPending || (stryMutAct_9fa48("848") ? manualText.trim() : (stryCov_9fa48("848"), !(stryMutAct_9fa48("849") ? manualText : (stryCov_9fa48("849"), manualText.trim())))))} style={{
          marginTop: '0.5rem',
          padding: '0.375rem 0.75rem',
          background: '#2563eb',
          color: '#fff',
          border: 'none',
          borderRadius: '0.375rem',
          cursor: (stryMutAct_9fa48("859") ? createManual.isPending && !manualText.trim() : stryMutAct_9fa48("858") ? false : stryMutAct_9fa48("857") ? true : (stryCov_9fa48("857", "858", "859"), createManual.isPending || (stryMutAct_9fa48("860") ? manualText.trim() : (stryCov_9fa48("860"), !(stryMutAct_9fa48("861") ? manualText : (stryCov_9fa48("861"), manualText.trim())))))) ? 'not-allowed' : 'pointer',
          fontSize: '0.875rem',
          opacity: (stryMutAct_9fa48("867") ? createManual.isPending && !manualText.trim() : stryMutAct_9fa48("866") ? false : stryMutAct_9fa48("865") ? true : (stryCov_9fa48("865", "866", "867"), createManual.isPending || (stryMutAct_9fa48("868") ? manualText.trim() : (stryCov_9fa48("868"), !(stryMutAct_9fa48("869") ? manualText : (stryCov_9fa48("869"), manualText.trim())))))) ? 0.6 : 1
        }}>
          {createManual.isPending ? 'Saving…' : 'Save String'}
        </button>
      </div>

      {/* Version history */}
      {stryMutAct_9fa48("874") ? isLoading || <p style={{
        color: '#64748b',
        fontSize: '0.875rem'
      }}>Loading…</p> : stryMutAct_9fa48("873") ? false : stryMutAct_9fa48("872") ? true : (stryCov_9fa48("872", "873", "874"), isLoading && <p style={{
        color: '#64748b',
        fontSize: '0.875rem'
      }}>Loading…</p>)}
      {stryMutAct_9fa48("880") ? strings.length > 0 || <div>
          <h4 style={{
          margin: '0 0 0.5rem',
          fontSize: '0.875rem',
          color: '#374151'
        }}>
            Version History ({strings.length})
          </h4>
          <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '0.5rem'
        }}>
            {strings.map(ss => <div key={ss.id} onClick={() => setSelectedId(ss.id)} style={{
            border: `1px solid ${selected?.id === ss.id ? '#2563eb' : '#e2e8f0'}`,
            borderRadius: '0.375rem',
            padding: '0.625rem 0.75rem',
            cursor: 'pointer',
            background: selected?.id === ss.id ? '#eff6ff' : '#fff'
          }}>
                <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginBottom: '0.25rem'
            }}>
                  <span style={{
                fontSize: '0.8125rem',
                fontWeight: 600,
                color: '#374151'
              }}>
                    v{ss.version}
                  </span>
                  <div style={{
                display: 'flex',
                gap: '0.5rem'
              }}>
                    {ss.created_by_agent && <span style={{
                  fontSize: '0.75rem',
                  background: '#f3e8ff',
                  color: '#7c3aed',
                  padding: '1px 6px',
                  borderRadius: '999px'
                }}>
                        AI
                      </span>}
                    {ss.is_active && <span style={{
                  fontSize: '0.75rem',
                  background: '#dcfce7',
                  color: '#16a34a',
                  padding: '1px 6px',
                  borderRadius: '999px'
                }}>
                        Active
                      </span>}
                  </div>
                </div>
                <code style={{
              display: 'block',
              fontSize: '0.75rem',
              color: '#1e293b',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              maxHeight: '4rem',
              overflow: 'hidden'
            }}>
                  {ss.string_text}
                </code>
                {ss.iterations.length > 0 && <div style={{
              marginTop: '0.375rem',
              fontSize: '0.75rem',
              color: '#64748b'
            }}>
                    {ss.iterations.length} test iteration{ss.iterations.length !== 1 ? 's' : ''} •{' '}
                    Last recall: {(ss.iterations[ss.iterations.length - 1].test_set_recall * 100).toFixed(0)}%
                  </div>}
              </div>)}
          </div>
        </div> : stryMutAct_9fa48("879") ? false : stryMutAct_9fa48("878") ? true : (stryCov_9fa48("878", "879", "880"), (stryMutAct_9fa48("883") ? strings.length <= 0 : stryMutAct_9fa48("882") ? strings.length >= 0 : stryMutAct_9fa48("881") ? true : (stryCov_9fa48("881", "882", "883"), strings.length > 0)) && <div>
          <h4 style={{
          margin: '0 0 0.5rem',
          fontSize: '0.875rem',
          color: '#374151'
        }}>
            Version History ({strings.length})
          </h4>
          <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '0.5rem'
        }}>
            {strings.map(stryMutAct_9fa48("892") ? () => undefined : (stryCov_9fa48("892"), ss => <div key={ss.id} onClick={stryMutAct_9fa48("893") ? () => undefined : (stryCov_9fa48("893"), () => setSelectedId(ss.id))} style={{
            border: `1px solid ${(stryMutAct_9fa48("898") ? selected?.id !== ss.id : stryMutAct_9fa48("897") ? false : stryMutAct_9fa48("896") ? true : (stryCov_9fa48("896", "897", "898"), (stryMutAct_9fa48("899") ? selected.id : (stryCov_9fa48("899"), selected?.id)) === ss.id)) ? '#2563eb' : '#e2e8f0'}`,
            borderRadius: '0.375rem',
            padding: '0.625rem 0.75rem',
            cursor: 'pointer',
            background: (stryMutAct_9fa48("907") ? selected?.id !== ss.id : stryMutAct_9fa48("906") ? false : stryMutAct_9fa48("905") ? true : (stryCov_9fa48("905", "906", "907"), (stryMutAct_9fa48("908") ? selected.id : (stryCov_9fa48("908"), selected?.id)) === ss.id)) ? '#eff6ff' : '#fff'
          }}>
                <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginBottom: '0.25rem'
            }}>
                  <span style={{
                fontSize: '0.8125rem',
                fontWeight: 600,
                color: '#374151'
              }}>
                    v{ss.version}
                  </span>
                  <div style={{
                display: 'flex',
                gap: '0.5rem'
              }}>
                    {stryMutAct_9fa48("923") ? ss.created_by_agent || <span style={{
                  fontSize: '0.75rem',
                  background: '#f3e8ff',
                  color: '#7c3aed',
                  padding: '1px 6px',
                  borderRadius: '999px'
                }}>
                        AI
                      </span> : stryMutAct_9fa48("922") ? false : stryMutAct_9fa48("921") ? true : (stryCov_9fa48("921", "922", "923"), ss.created_by_agent && <span style={{
                  fontSize: '0.75rem',
                  background: '#f3e8ff',
                  color: '#7c3aed',
                  padding: '1px 6px',
                  borderRadius: '999px'
                }}>
                        AI
                      </span>)}
                    {stryMutAct_9fa48("932") ? ss.is_active || <span style={{
                  fontSize: '0.75rem',
                  background: '#dcfce7',
                  color: '#16a34a',
                  padding: '1px 6px',
                  borderRadius: '999px'
                }}>
                        Active
                      </span> : stryMutAct_9fa48("931") ? false : stryMutAct_9fa48("930") ? true : (stryCov_9fa48("930", "931", "932"), ss.is_active && <span style={{
                  fontSize: '0.75rem',
                  background: '#dcfce7',
                  color: '#16a34a',
                  padding: '1px 6px',
                  borderRadius: '999px'
                }}>
                        Active
                      </span>)}
                  </div>
                </div>
                <code style={{
              display: 'block',
              fontSize: '0.75rem',
              color: '#1e293b',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              maxHeight: '4rem',
              overflow: 'hidden'
            }}>
                  {ss.string_text}
                </code>
                {stryMutAct_9fa48("949") ? ss.iterations.length > 0 || <div style={{
              marginTop: '0.375rem',
              fontSize: '0.75rem',
              color: '#64748b'
            }}>
                    {ss.iterations.length} test iteration{ss.iterations.length !== 1 ? 's' : ''} •{' '}
                    Last recall: {(ss.iterations[ss.iterations.length - 1].test_set_recall * 100).toFixed(0)}%
                  </div> : stryMutAct_9fa48("948") ? false : stryMutAct_9fa48("947") ? true : (stryCov_9fa48("947", "948", "949"), (stryMutAct_9fa48("952") ? ss.iterations.length <= 0 : stryMutAct_9fa48("951") ? ss.iterations.length >= 0 : stryMutAct_9fa48("950") ? true : (stryCov_9fa48("950", "951", "952"), ss.iterations.length > 0)) && <div style={{
              marginTop: '0.375rem',
              fontSize: '0.75rem',
              color: '#64748b'
            }}>
                    {ss.iterations.length} test iteration{(stryMutAct_9fa48("959") ? ss.iterations.length === 1 : stryMutAct_9fa48("958") ? false : stryMutAct_9fa48("957") ? true : (stryCov_9fa48("957", "958", "959"), ss.iterations.length !== 1)) ? 's' : ''} •{' '}
                    Last recall: {(stryMutAct_9fa48("963") ? ss.iterations[ss.iterations.length - 1].test_set_recall / 100 : (stryCov_9fa48("963"), ss.iterations[stryMutAct_9fa48("964") ? ss.iterations.length + 1 : (stryCov_9fa48("964"), ss.iterations.length - 1)].test_set_recall * 100)).toFixed(0)}%
                  </div>)}
              </div>))}
          </div>
        </div>)}

      {/* Selected string full view */}
      {stryMutAct_9fa48("967") ? selected || <div style={{
        marginTop: '1rem',
        padding: '0.75rem',
        background: '#f8fafc',
        borderRadius: '0.5rem'
      }}>
          <h4 style={{
          margin: '0 0 0.5rem',
          fontSize: '0.875rem',
          color: '#374151'
        }}>
            v{selected.version} — Full String
          </h4>
          <code style={{
          display: 'block',
          fontSize: '0.8125rem',
          color: '#1e293b',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word'
        }}>
            {selected.string_text}
          </code>
        </div> : stryMutAct_9fa48("966") ? false : stryMutAct_9fa48("965") ? true : (stryCov_9fa48("965", "966", "967"), selected && <div style={{
        marginTop: '1rem',
        padding: '0.75rem',
        background: '#f8fafc',
        borderRadius: '0.5rem'
      }}>
          <h4 style={{
          margin: '0 0 0.5rem',
          fontSize: '0.875rem',
          color: '#374151'
        }}>
            v{selected.version} — Full String
          </h4>
          <code style={{
          display: 'block',
          fontSize: '0.8125rem',
          color: '#1e293b',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word'
        }}>
            {selected.string_text}
          </code>
        </div>)}
    </div>;
  }
}