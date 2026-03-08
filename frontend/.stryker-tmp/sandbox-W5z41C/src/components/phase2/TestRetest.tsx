/**
 * TestRetest: trigger test search, show iteration results, approve/reject.
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
  version: number;
  string_text: string;
  is_active: boolean;
  created_by_agent: string | null;
  iterations: Iteration[];
}
interface TestRetestProps {
  studyId: number;
}
export default function TestRetest({
  studyId
}: TestRetestProps) {
  if (stryMutAct_9fa48("983")) {
    {}
  } else {
    stryCov_9fa48("983");
    const qc = useQueryClient();
    const [testError, setTestError] = useState<string | null>(null);
    const [selectedStringId, setSelectedStringId] = useState<number | null>(null);
    const [databases, setDatabases] = useState('');
    const {
      data: strings = stryMutAct_9fa48("985") ? ["Stryker was here"] : (stryCov_9fa48("985"), []),
      isLoading
    } = useQuery<SearchString[]>({
      queryKey: stryMutAct_9fa48("987") ? [] : (stryCov_9fa48("987"), ['search-strings', studyId]),
      queryFn: stryMutAct_9fa48("989") ? () => undefined : (stryCov_9fa48("989"), () => api.get<SearchString[]>(`/api/v1/studies/${studyId}/search-strings`))
    });
    const activeOrFirst = selectedStringId ? strings.find(stryMutAct_9fa48("991") ? () => undefined : (stryCov_9fa48("991"), s => stryMutAct_9fa48("994") ? s.id !== selectedStringId : stryMutAct_9fa48("993") ? false : stryMutAct_9fa48("992") ? true : (stryCov_9fa48("992", "993", "994"), s.id === selectedStringId))) : stryMutAct_9fa48("995") ? strings.find(s => s.is_active) && strings[0] : (stryCov_9fa48("995"), strings.find(stryMutAct_9fa48("996") ? () => undefined : (stryCov_9fa48("996"), s => s.is_active)) ?? strings[0]);
    const runTest = useMutation({
      mutationFn: stryMutAct_9fa48("998") ? () => undefined : (stryCov_9fa48("998"), (ssId: number) => api.post<{
        job_id: string | null;
        search_string_id: number;
      }>(`/api/v1/studies/${studyId}/search-strings/${ssId}/test`, {
        databases: stryMutAct_9fa48("1001") ? databases.split(',').map(d => d.trim()) : (stryCov_9fa48("1001"), databases.split(',').map(stryMutAct_9fa48("1003") ? () => undefined : (stryCov_9fa48("1003"), d => stryMutAct_9fa48("1004") ? d : (stryCov_9fa48("1004"), d.trim()))).filter(Boolean))
      })),
      onSuccess: () => {
        if (stryMutAct_9fa48("1005")) {
          {}
        } else {
          stryCov_9fa48("1005");
          setTestError(null);
          // After job completes, user can refresh to see new iteration
          qc.invalidateQueries({
            queryKey: stryMutAct_9fa48("1007") ? [] : (stryCov_9fa48("1007"), ['search-strings', studyId])
          });
        }
      },
      onError: err => {
        if (stryMutAct_9fa48("1009")) {
          {}
        } else {
          stryCov_9fa48("1009");
          setTestError(err instanceof ApiError ? err.detail : 'Test search failed');
        }
      }
    });
    const approveIteration = useMutation({
      mutationFn: stryMutAct_9fa48("1012") ? () => undefined : (stryCov_9fa48("1012"), ({
        ssId,
        iterId,
        approved
      }: {
        ssId: number;
        iterId: number;
        approved: boolean;
      }) => api.patch<Iteration>(`/api/v1/studies/${studyId}/search-strings/${ssId}/iterations/${iterId}`, {
        human_approved: approved
      })),
      onSuccess: stryMutAct_9fa48("1015") ? () => undefined : (stryCov_9fa48("1015"), () => qc.invalidateQueries({
        queryKey: stryMutAct_9fa48("1017") ? [] : (stryCov_9fa48("1017"), ['search-strings', studyId])
      }))
    });
    if (stryMutAct_9fa48("1020") ? false : stryMutAct_9fa48("1019") ? true : (stryCov_9fa48("1019", "1020"), isLoading)) return <p style={{
      color: '#64748b',
      fontSize: '0.875rem'
    }}>Loading…</p>;
    if (stryMutAct_9fa48("1026") ? strings.length !== 0 : stryMutAct_9fa48("1025") ? false : stryMutAct_9fa48("1024") ? true : (stryCov_9fa48("1024", "1025", "1026"), strings.length === 0)) {
      if (stryMutAct_9fa48("1027")) {
        {}
      } else {
        stryCov_9fa48("1027");
        return <div style={{
          color: '#64748b',
          fontSize: '0.875rem'
        }}>
        No search strings yet. Create one in the Search String Editor above.
      </div>;
      }
    }
    return <div>
      <h3 style={{
        margin: '0 0 1rem',
        fontSize: '1rem',
        color: '#111827'
      }}>Test &amp; Evaluate</h3>

      {/* String selector */}
      <div style={{
        marginBottom: '1rem'
      }}>
        <label style={{
          fontSize: '0.875rem',
          color: '#374151',
          marginRight: '0.5rem'
        }}>
          Search string:
        </label>
        <select value={stryMutAct_9fa48("1041") ? activeOrFirst?.id && '' : (stryCov_9fa48("1041"), (stryMutAct_9fa48("1042") ? activeOrFirst.id : (stryCov_9fa48("1042"), activeOrFirst?.id)) ?? '')} onChange={stryMutAct_9fa48("1044") ? () => undefined : (stryCov_9fa48("1044"), e => setSelectedStringId(Number(e.target.value)))} style={{
          padding: '0.375rem 0.5rem',
          border: '1px solid #d1d5db',
          borderRadius: '0.375rem',
          fontSize: '0.875rem'
        }}>
          {strings.map(stryMutAct_9fa48("1050") ? () => undefined : (stryCov_9fa48("1050"), ss => <option key={ss.id} value={ss.id}>
              v{ss.version}{ss.is_active ? ' (active)' : ''}{ss.created_by_agent ? ' [AI]' : ''}
            </option>))}
        </select>
      </div>

      {/* Databases input */}
      <div style={{
        marginBottom: '1rem'
      }}>
        <label style={{
          fontSize: '0.875rem',
          color: '#374151',
          display: 'block',
          marginBottom: '0.25rem'
        }}>
          Databases (comma-separated, e.g. acm,ieee,scopus):
        </label>
        <input value={databases} onChange={stryMutAct_9fa48("1062") ? () => undefined : (stryCov_9fa48("1062"), e => setDatabases(e.target.value))} placeholder="acm,ieee,scopus" style={{
          width: '100%',
          padding: '0.375rem 0.625rem',
          border: '1px solid #d1d5db',
          borderRadius: '0.375rem',
          fontSize: '0.875rem',
          boxSizing: 'border-box'
        }} />
      </div>

      {/* Run test button */}
      <button onClick={stryMutAct_9fa48("1070") ? () => undefined : (stryCov_9fa48("1070"), () => stryMutAct_9fa48("1073") ? activeOrFirst || runTest.mutate(activeOrFirst.id) : stryMutAct_9fa48("1072") ? false : stryMutAct_9fa48("1071") ? true : (stryCov_9fa48("1071", "1072", "1073"), activeOrFirst && runTest.mutate(activeOrFirst.id)))} disabled={stryMutAct_9fa48("1076") ? runTest.isPending && !activeOrFirst : stryMutAct_9fa48("1075") ? false : stryMutAct_9fa48("1074") ? true : (stryCov_9fa48("1074", "1075", "1076"), runTest.isPending || (stryMutAct_9fa48("1077") ? activeOrFirst : (stryCov_9fa48("1077"), !activeOrFirst)))} style={{
        padding: '0.5rem 1rem',
        background: '#0891b2',
        color: '#fff',
        border: 'none',
        borderRadius: '0.375rem',
        cursor: (stryMutAct_9fa48("1086") ? runTest.isPending && !activeOrFirst : stryMutAct_9fa48("1085") ? false : stryMutAct_9fa48("1084") ? true : (stryCov_9fa48("1084", "1085", "1086"), runTest.isPending || (stryMutAct_9fa48("1087") ? activeOrFirst : (stryCov_9fa48("1087"), !activeOrFirst)))) ? 'not-allowed' : 'pointer',
        fontSize: '0.875rem',
        marginBottom: '1rem',
        opacity: (stryMutAct_9fa48("1094") ? runTest.isPending && !activeOrFirst : stryMutAct_9fa48("1093") ? false : stryMutAct_9fa48("1092") ? true : (stryCov_9fa48("1092", "1093", "1094"), runTest.isPending || (stryMutAct_9fa48("1095") ? activeOrFirst : (stryCov_9fa48("1095"), !activeOrFirst)))) ? 0.6 : 1
      }}>
        {runTest.isPending ? 'Queuing…' : '▶ Run Test Search'}
      </button>

      {stryMutAct_9fa48("1100") ? runTest.isSuccess || <p style={{
        fontSize: '0.875rem',
        color: '#16a34a',
        marginBottom: '0.75rem'
      }}>
          Test search queued. Refresh to see new iteration results.
        </p> : stryMutAct_9fa48("1099") ? false : stryMutAct_9fa48("1098") ? true : (stryCov_9fa48("1098", "1099", "1100"), runTest.isSuccess && <p style={{
        fontSize: '0.875rem',
        color: '#16a34a',
        marginBottom: '0.75rem'
      }}>
          Test search queued. Refresh to see new iteration results.
        </p>)}

      {stryMutAct_9fa48("1107") ? testError || <p style={{
        color: '#ef4444',
        fontSize: '0.875rem',
        margin: '0 0 0.75rem'
      }}>{testError}</p> : stryMutAct_9fa48("1106") ? false : stryMutAct_9fa48("1105") ? true : (stryCov_9fa48("1105", "1106", "1107"), testError && <p style={{
        color: '#ef4444',
        fontSize: '0.875rem',
        margin: '0 0 0.75rem'
      }}>{testError}</p>)}

      {/* Iterations table */}
      {stryMutAct_9fa48("1114") ? activeOrFirst && activeOrFirst.iterations.length > 0 || <div>
          <h4 style={{
          margin: '0 0 0.5rem',
          fontSize: '0.875rem',
          color: '#374151'
        }}>
            Iterations for v{activeOrFirst.version}
          </h4>
          <table style={{
          width: '100%',
          borderCollapse: 'collapse',
          fontSize: '0.875rem'
        }}>
            <thead>
              <tr style={{
              background: '#f1f5f9'
            }}>
                <th style={thStyle}>#</th>
                <th style={thStyle}>Results</th>
                <th style={thStyle}>Recall</th>
                <th style={thStyle}>AI Judgment</th>
                <th style={thStyle}>Status</th>
                <th style={thStyle}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {activeOrFirst.iterations.map(it => <tr key={it.id} style={{
              borderBottom: '1px solid #e2e8f0'
            }}>
                  <td style={tdStyle}>{it.iteration_number}</td>
                  <td style={tdStyle}>{it.result_set_count.toLocaleString()}</td>
                  <td style={tdStyle}>
                    <span style={{
                  color: it.test_set_recall >= 0.8 ? '#16a34a' : it.test_set_recall >= 0.5 ? '#d97706' : '#dc2626',
                  fontWeight: 600
                }}>
                      {(it.test_set_recall * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td style={{
                ...tdStyle,
                maxWidth: '200px',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap'
              }}>
                    {it.ai_adequacy_judgment ?? '—'}
                  </td>
                  <td style={tdStyle}>
                    {it.human_approved === true && <span style={{
                  color: '#16a34a',
                  fontWeight: 600
                }}>Approved</span>}
                    {it.human_approved === false && <span style={{
                  color: '#dc2626',
                  fontWeight: 600
                }}>Rejected</span>}
                    {it.human_approved === null && <span style={{
                  color: '#64748b'
                }}>Pending</span>}
                  </td>
                  <td style={tdStyle}>
                    {it.human_approved !== true && <button onClick={() => approveIteration.mutate({
                  ssId: activeOrFirst.id,
                  iterId: it.id,
                  approved: true
                })} style={actionBtnStyle('#16a34a')}>
                        Approve
                      </button>}
                    {it.human_approved !== false && <button onClick={() => approveIteration.mutate({
                  ssId: activeOrFirst.id,
                  iterId: it.id,
                  approved: false
                })} style={{
                  ...actionBtnStyle('#dc2626'),
                  marginLeft: '0.25rem'
                }}>
                        Reject
                      </button>}
                  </td>
                </tr>)}
            </tbody>
          </table>
        </div> : stryMutAct_9fa48("1113") ? false : stryMutAct_9fa48("1112") ? true : (stryCov_9fa48("1112", "1113", "1114"), (stryMutAct_9fa48("1116") ? activeOrFirst || activeOrFirst.iterations.length > 0 : stryMutAct_9fa48("1115") ? true : (stryCov_9fa48("1115", "1116"), activeOrFirst && (stryMutAct_9fa48("1119") ? activeOrFirst.iterations.length <= 0 : stryMutAct_9fa48("1118") ? activeOrFirst.iterations.length >= 0 : stryMutAct_9fa48("1117") ? true : (stryCov_9fa48("1117", "1118", "1119"), activeOrFirst.iterations.length > 0)))) && <div>
          <h4 style={{
          margin: '0 0 0.5rem',
          fontSize: '0.875rem',
          color: '#374151'
        }}>
            Iterations for v{activeOrFirst.version}
          </h4>
          <table style={{
          width: '100%',
          borderCollapse: 'collapse',
          fontSize: '0.875rem'
        }}>
            <thead>
              <tr style={{
              background: '#f1f5f9'
            }}>
                <th style={thStyle}>#</th>
                <th style={thStyle}>Results</th>
                <th style={thStyle}>Recall</th>
                <th style={thStyle}>AI Judgment</th>
                <th style={thStyle}>Status</th>
                <th style={thStyle}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {activeOrFirst.iterations.map(stryMutAct_9fa48("1130") ? () => undefined : (stryCov_9fa48("1130"), it => <tr key={it.id} style={{
              borderBottom: '1px solid #e2e8f0'
            }}>
                  <td style={tdStyle}>{it.iteration_number}</td>
                  <td style={tdStyle}>{it.result_set_count.toLocaleString()}</td>
                  <td style={tdStyle}>
                    <span style={{
                  color: (stryMutAct_9fa48("1137") ? it.test_set_recall < 0.8 : stryMutAct_9fa48("1136") ? it.test_set_recall > 0.8 : stryMutAct_9fa48("1135") ? false : stryMutAct_9fa48("1134") ? true : (stryCov_9fa48("1134", "1135", "1136", "1137"), it.test_set_recall >= 0.8)) ? '#16a34a' : (stryMutAct_9fa48("1142") ? it.test_set_recall < 0.5 : stryMutAct_9fa48("1141") ? it.test_set_recall > 0.5 : stryMutAct_9fa48("1140") ? false : stryMutAct_9fa48("1139") ? true : (stryCov_9fa48("1139", "1140", "1141", "1142"), it.test_set_recall >= 0.5)) ? '#d97706' : '#dc2626',
                  fontWeight: 600
                }}>
                      {(stryMutAct_9fa48("1145") ? it.test_set_recall / 100 : (stryCov_9fa48("1145"), it.test_set_recall * 100)).toFixed(1)}%
                    </span>
                  </td>
                  <td style={{
                ...tdStyle,
                maxWidth: '200px',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap'
              }}>
                    {stryMutAct_9fa48("1151") ? it.ai_adequacy_judgment && '—' : (stryCov_9fa48("1151"), it.ai_adequacy_judgment ?? '—')}
                  </td>
                  <td style={tdStyle}>
                    {stryMutAct_9fa48("1155") ? it.human_approved === true || <span style={{
                  color: '#16a34a',
                  fontWeight: 600
                }}>Approved</span> : stryMutAct_9fa48("1154") ? false : stryMutAct_9fa48("1153") ? true : (stryCov_9fa48("1153", "1154", "1155"), (stryMutAct_9fa48("1157") ? it.human_approved !== true : stryMutAct_9fa48("1156") ? true : (stryCov_9fa48("1156", "1157"), it.human_approved === (stryMutAct_9fa48("1158") ? false : (stryCov_9fa48("1158"), true)))) && <span style={{
                  color: '#16a34a',
                  fontWeight: 600
                }}>Approved</span>)}
                    {stryMutAct_9fa48("1163") ? it.human_approved === false || <span style={{
                  color: '#dc2626',
                  fontWeight: 600
                }}>Rejected</span> : stryMutAct_9fa48("1162") ? false : stryMutAct_9fa48("1161") ? true : (stryCov_9fa48("1161", "1162", "1163"), (stryMutAct_9fa48("1165") ? it.human_approved !== false : stryMutAct_9fa48("1164") ? true : (stryCov_9fa48("1164", "1165"), it.human_approved === (stryMutAct_9fa48("1166") ? true : (stryCov_9fa48("1166"), false)))) && <span style={{
                  color: '#dc2626',
                  fontWeight: 600
                }}>Rejected</span>)}
                    {stryMutAct_9fa48("1171") ? it.human_approved === null || <span style={{
                  color: '#64748b'
                }}>Pending</span> : stryMutAct_9fa48("1170") ? false : stryMutAct_9fa48("1169") ? true : (stryCov_9fa48("1169", "1170", "1171"), (stryMutAct_9fa48("1173") ? it.human_approved !== null : stryMutAct_9fa48("1172") ? true : (stryCov_9fa48("1172", "1173"), it.human_approved === null)) && <span style={{
                  color: '#64748b'
                }}>Pending</span>)}
                  </td>
                  <td style={tdStyle}>
                    {stryMutAct_9fa48("1178") ? it.human_approved !== true || <button onClick={() => approveIteration.mutate({
                  ssId: activeOrFirst.id,
                  iterId: it.id,
                  approved: true
                })} style={actionBtnStyle('#16a34a')}>
                        Approve
                      </button> : stryMutAct_9fa48("1177") ? false : stryMutAct_9fa48("1176") ? true : (stryCov_9fa48("1176", "1177", "1178"), (stryMutAct_9fa48("1180") ? it.human_approved === true : stryMutAct_9fa48("1179") ? true : (stryCov_9fa48("1179", "1180"), it.human_approved !== (stryMutAct_9fa48("1181") ? false : (stryCov_9fa48("1181"), true)))) && <button onClick={stryMutAct_9fa48("1182") ? () => undefined : (stryCov_9fa48("1182"), () => approveIteration.mutate({
                  ssId: activeOrFirst.id,
                  iterId: it.id,
                  approved: stryMutAct_9fa48("1184") ? false : (stryCov_9fa48("1184"), true)
                }))} style={actionBtnStyle('#16a34a')}>
                        Approve
                      </button>)}
                    {stryMutAct_9fa48("1188") ? it.human_approved !== false || <button onClick={() => approveIteration.mutate({
                  ssId: activeOrFirst.id,
                  iterId: it.id,
                  approved: false
                })} style={{
                  ...actionBtnStyle('#dc2626'),
                  marginLeft: '0.25rem'
                }}>
                        Reject
                      </button> : stryMutAct_9fa48("1187") ? false : stryMutAct_9fa48("1186") ? true : (stryCov_9fa48("1186", "1187", "1188"), (stryMutAct_9fa48("1190") ? it.human_approved === false : stryMutAct_9fa48("1189") ? true : (stryCov_9fa48("1189", "1190"), it.human_approved !== (stryMutAct_9fa48("1191") ? true : (stryCov_9fa48("1191"), false)))) && <button onClick={stryMutAct_9fa48("1192") ? () => undefined : (stryCov_9fa48("1192"), () => approveIteration.mutate({
                  ssId: activeOrFirst.id,
                  iterId: it.id,
                  approved: stryMutAct_9fa48("1194") ? true : (stryCov_9fa48("1194"), false)
                }))} style={{
                  ...actionBtnStyle('#dc2626'),
                  marginLeft: '0.25rem'
                }}>
                        Reject
                      </button>)}
                  </td>
                </tr>))}
            </tbody>
          </table>
        </div>)}

      {stryMutAct_9fa48("1200") ? activeOrFirst && activeOrFirst.iterations.length === 0 || <p style={{
        color: '#64748b',
        fontSize: '0.875rem'
      }}>
          No test iterations yet. Run a test search to evaluate recall.
        </p> : stryMutAct_9fa48("1199") ? false : stryMutAct_9fa48("1198") ? true : (stryCov_9fa48("1198", "1199", "1200"), (stryMutAct_9fa48("1202") ? activeOrFirst || activeOrFirst.iterations.length === 0 : stryMutAct_9fa48("1201") ? true : (stryCov_9fa48("1201", "1202"), activeOrFirst && (stryMutAct_9fa48("1204") ? activeOrFirst.iterations.length !== 0 : stryMutAct_9fa48("1203") ? true : (stryCov_9fa48("1203", "1204"), activeOrFirst.iterations.length === 0)))) && <p style={{
        color: '#64748b',
        fontSize: '0.875rem'
      }}>
          No test iterations yet. Run a test search to evaluate recall.
        </p>)}
    </div>;
  }
}
const thStyle: React.CSSProperties = {
  padding: '0.5rem 0.75rem',
  textAlign: 'left',
  fontWeight: 600,
  color: '#374151',
  fontSize: '0.8125rem',
  borderBottom: '2px solid #e2e8f0'
};
const tdStyle: React.CSSProperties = {
  padding: '0.5rem 0.75rem',
  color: '#374151'
};
function actionBtnStyle(color: string): React.CSSProperties {
  if (stryMutAct_9fa48("1217")) {
    {}
  } else {
    stryCov_9fa48("1217");
    return {
      padding: '0.25rem 0.5rem',
      background: 'transparent',
      border: `1px solid ${color}`,
      borderRadius: '0.25rem',
      color,
      cursor: 'pointer',
      fontSize: '0.75rem'
    };
  }
}