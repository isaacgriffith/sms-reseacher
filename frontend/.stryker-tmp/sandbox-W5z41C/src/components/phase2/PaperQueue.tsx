/**
 * PaperQueue: paginated list of candidate papers with status badges,
 * phase tags, and AI decision summaries. Filters by status and phase.
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
import { useQuery } from '@tanstack/react-query';
import { api } from '../../services/api';
interface Paper {
  id: number;
  title: string;
  abstract: string | null;
  doi: string | null;
  authors: Array<{
    name: string;
  }> | null;
  year: number | null;
  venue: string | null;
}
interface CandidatePaper {
  id: number;
  study_id: number;
  paper_id: number;
  phase_tag: string;
  current_status: 'pending' | 'accepted' | 'rejected' | 'duplicate';
  duplicate_of_id: number | null;
  paper: Paper;
}
interface PaperQueueProps {
  studyId: number;
}
const STATUS_COLORS: Record<string, string> = {
  pending: '#d97706',
  accepted: '#16a34a',
  rejected: '#dc2626',
  duplicate: '#6b7280'
};
const PAGE_SIZE = 20;
export default function PaperQueue({
  studyId
}: PaperQueueProps) {
  if (stryMutAct_9fa48("337")) {
    {}
  } else {
    stryCov_9fa48("337");
    const [statusFilter, setStatusFilter] = useState<string>('');
    const [phaseFilter, setPhaseFilter] = useState<string>('');
    const [page, setPage] = useState(0);
    const offset = stryMutAct_9fa48("340") ? page / PAGE_SIZE : (stryCov_9fa48("340"), page * PAGE_SIZE);
    const params = new URLSearchParams();
    if (stryMutAct_9fa48("342") ? false : stryMutAct_9fa48("341") ? true : (stryCov_9fa48("341", "342"), statusFilter)) params.set('status', statusFilter);
    if (stryMutAct_9fa48("345") ? false : stryMutAct_9fa48("344") ? true : (stryCov_9fa48("344", "345"), phaseFilter)) params.set('phase_tag', phaseFilter);
    params.set('offset', String(offset));
    params.set('limit', String(PAGE_SIZE));
    const {
      data: papers = stryMutAct_9fa48("349") ? ["Stryker was here"] : (stryCov_9fa48("349"), []),
      isLoading,
      error,
      refetch
    } = useQuery<CandidatePaper[]>({
      queryKey: stryMutAct_9fa48("351") ? [] : (stryCov_9fa48("351"), ['papers', studyId, statusFilter, phaseFilter, page]),
      queryFn: stryMutAct_9fa48("353") ? () => undefined : (stryCov_9fa48("353"), () => api.get<CandidatePaper[]>(`/api/v1/studies/${studyId}/papers?${params.toString()}`))
    });
    const handleResetFilters = () => {
      if (stryMutAct_9fa48("355")) {
        {}
      } else {
        stryCov_9fa48("355");
        setStatusFilter('');
        setPhaseFilter('');
        setPage(0);
      }
    };
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
        }}>Paper Queue</h3>
        <button onClick={stryMutAct_9fa48("366") ? () => undefined : (stryCov_9fa48("366"), () => refetch())} style={{
          padding: '0.25rem 0.75rem',
          background: 'transparent',
          border: '1px solid #d1d5db',
          borderRadius: '0.375rem',
          cursor: 'pointer',
          fontSize: '0.8125rem',
          color: '#374151'
        }}>
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div style={{
        display: 'flex',
        gap: '0.75rem',
        marginBottom: '1rem',
        flexWrap: 'wrap'
      }}>
        <select value={statusFilter} onChange={e => {
          if (stryMutAct_9fa48("380")) {
            {}
          } else {
            stryCov_9fa48("380");
            setStatusFilter(e.target.value);
            setPage(0);
          }
        }} style={selectStyle}>
          <option value="">All statuses</option>
          <option value="pending">Pending</option>
          <option value="accepted">Accepted</option>
          <option value="rejected">Rejected</option>
          <option value="duplicate">Duplicate</option>
        </select>

        <input value={phaseFilter} onChange={e => {
          if (stryMutAct_9fa48("381")) {
            {}
          } else {
            stryCov_9fa48("381");
            setPhaseFilter(e.target.value);
            setPage(0);
          }
        }} placeholder="Filter by phase tag…" style={{
          padding: '0.375rem 0.625rem',
          border: '1px solid #d1d5db',
          borderRadius: '0.375rem',
          fontSize: '0.875rem',
          minWidth: '180px'
        }} />

        {stryMutAct_9fa48("390") ? statusFilter || phaseFilter || <button onClick={handleResetFilters} style={clearBtnStyle}>
            Clear filters
          </button> : stryMutAct_9fa48("389") ? false : stryMutAct_9fa48("388") ? true : (stryCov_9fa48("388", "389", "390"), (stryMutAct_9fa48("392") ? statusFilter && phaseFilter : stryMutAct_9fa48("391") ? true : (stryCov_9fa48("391", "392"), statusFilter || phaseFilter)) && <button onClick={handleResetFilters} style={clearBtnStyle}>
            Clear filters
          </button>)}
      </div>

      {/* Paper list */}
      {stryMutAct_9fa48("395") ? isLoading || <p style={{
        color: '#6b7280',
        fontSize: '0.875rem'
      }}>Loading papers…</p> : stryMutAct_9fa48("394") ? false : stryMutAct_9fa48("393") ? true : (stryCov_9fa48("393", "394", "395"), isLoading && <p style={{
        color: '#6b7280',
        fontSize: '0.875rem'
      }}>Loading papers…</p>)}
      {stryMutAct_9fa48("401") ? error || <p style={{
        color: '#ef4444',
        fontSize: '0.875rem'
      }}>Failed to load papers.</p> : stryMutAct_9fa48("400") ? false : stryMutAct_9fa48("399") ? true : (stryCov_9fa48("399", "400", "401"), error && <p style={{
        color: '#ef4444',
        fontSize: '0.875rem'
      }}>Failed to load papers.</p>)}

      {stryMutAct_9fa48("407") ? !isLoading && papers.length === 0 || <p style={{
        color: '#9ca3af',
        fontSize: '0.875rem'
      }}>
          No candidate papers found.{' '}
          {statusFilter || phaseFilter ? 'Try adjusting your filters.' : 'Run a full search to populate the paper queue.'}
        </p> : stryMutAct_9fa48("406") ? false : stryMutAct_9fa48("405") ? true : (stryCov_9fa48("405", "406", "407"), (stryMutAct_9fa48("409") ? !isLoading || papers.length === 0 : stryMutAct_9fa48("408") ? true : (stryCov_9fa48("408", "409"), (stryMutAct_9fa48("410") ? isLoading : (stryCov_9fa48("410"), !isLoading)) && (stryMutAct_9fa48("412") ? papers.length !== 0 : stryMutAct_9fa48("411") ? true : (stryCov_9fa48("411", "412"), papers.length === 0)))) && <p style={{
        color: '#9ca3af',
        fontSize: '0.875rem'
      }}>
          No candidate papers found.{' '}
          {(stryMutAct_9fa48("419") ? statusFilter && phaseFilter : stryMutAct_9fa48("418") ? false : stryMutAct_9fa48("417") ? true : (stryCov_9fa48("417", "418", "419"), statusFilter || phaseFilter)) ? 'Try adjusting your filters.' : 'Run a full search to populate the paper queue.'}
        </p>)}

      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '0.75rem'
      }}>
        {papers.map(stryMutAct_9fa48("426") ? () => undefined : (stryCov_9fa48("426"), cp => <div key={cp.id} style={{
          border: '1px solid #e2e8f0',
          borderRadius: '0.5rem',
          padding: '0.875rem',
          background: '#fff'
        }}>
            <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            gap: '0.75rem',
            marginBottom: '0.375rem'
          }}>
              <span style={{
              fontWeight: 600,
              fontSize: '0.875rem',
              color: '#111827',
              flex: 1
            }}>
                {cp.paper.title}
              </span>
              <span style={{
              flexShrink: 0,
              padding: '0.125rem 0.5rem',
              borderRadius: '9999px',
              fontSize: '0.75rem',
              fontWeight: 600,
              background: `${STATUS_COLORS[cp.current_status]}20`,
              color: STATUS_COLORS[cp.current_status],
              textTransform: 'capitalize'
            }}>
                {cp.current_status}
              </span>
            </div>

            <div style={{
            display: 'flex',
            gap: '1rem',
            fontSize: '0.75rem',
            color: '#6b7280',
            flexWrap: 'wrap'
          }}>
              {stryMutAct_9fa48("455") ? cp.paper.year || <span>{cp.paper.year}</span> : stryMutAct_9fa48("454") ? false : stryMutAct_9fa48("453") ? true : (stryCov_9fa48("453", "454", "455"), cp.paper.year && <span>{cp.paper.year}</span>)}
              {stryMutAct_9fa48("458") ? cp.paper.venue || <span>{cp.paper.venue}</span> : stryMutAct_9fa48("457") ? false : stryMutAct_9fa48("456") ? true : (stryCov_9fa48("456", "457", "458"), cp.paper.venue && <span>{cp.paper.venue}</span>)}
              {stryMutAct_9fa48("461") ? cp.paper.doi || <span>DOI: {cp.paper.doi}</span> : stryMutAct_9fa48("460") ? false : stryMutAct_9fa48("459") ? true : (stryCov_9fa48("459", "460", "461"), cp.paper.doi && <span>DOI: {cp.paper.doi}</span>)}
              <span style={{
              padding: '0.0625rem 0.375rem',
              background: '#f1f5f9',
              borderRadius: '0.25rem',
              fontSize: '0.6875rem'
            }}>
                {cp.phase_tag}
              </span>
            </div>

            {stryMutAct_9fa48("469") ? cp.paper.abstract || <p style={{
            margin: '0.5rem 0 0',
            fontSize: '0.8125rem',
            color: '#4b5563',
            lineHeight: 1.5,
            display: '-webkit-box',
            WebkitLineClamp: 3,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden'
          }}>
                {cp.paper.abstract}
              </p> : stryMutAct_9fa48("468") ? false : stryMutAct_9fa48("467") ? true : (stryCov_9fa48("467", "468", "469"), cp.paper.abstract && <p style={{
            margin: '0.5rem 0 0',
            fontSize: '0.8125rem',
            color: '#4b5563',
            lineHeight: 1.5,
            display: '-webkit-box',
            WebkitLineClamp: 3,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden'
          }}>
                {cp.paper.abstract}
              </p>)}
          </div>))}
      </div>

      {/* Pagination */}
      {stryMutAct_9fa48("479") ? papers.length === PAGE_SIZE || page > 0 || <div style={{
        display: 'flex',
        gap: '0.5rem',
        justifyContent: 'center',
        marginTop: '1rem'
      }}>
          <button onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0} style={paginationBtnStyle(page === 0)}>
            ← Previous
          </button>
          <span style={{
          padding: '0.375rem 0.625rem',
          fontSize: '0.875rem',
          color: '#374151'
        }}>
            Page {page + 1}
          </span>
          <button onClick={() => setPage(p => p + 1)} disabled={papers.length < PAGE_SIZE} style={paginationBtnStyle(papers.length < PAGE_SIZE)}>
            Next →
          </button>
        </div> : stryMutAct_9fa48("478") ? false : stryMutAct_9fa48("477") ? true : (stryCov_9fa48("477", "478", "479"), (stryMutAct_9fa48("481") ? papers.length === PAGE_SIZE && page > 0 : stryMutAct_9fa48("480") ? true : (stryCov_9fa48("480", "481"), (stryMutAct_9fa48("483") ? papers.length !== PAGE_SIZE : stryMutAct_9fa48("482") ? false : (stryCov_9fa48("482", "483"), papers.length === PAGE_SIZE)) || (stryMutAct_9fa48("486") ? page <= 0 : stryMutAct_9fa48("485") ? page >= 0 : stryMutAct_9fa48("484") ? false : (stryCov_9fa48("484", "485", "486"), page > 0)))) && <div style={{
        display: 'flex',
        gap: '0.5rem',
        justifyContent: 'center',
        marginTop: '1rem'
      }}>
          <button onClick={stryMutAct_9fa48("492") ? () => undefined : (stryCov_9fa48("492"), () => setPage(stryMutAct_9fa48("493") ? () => undefined : (stryCov_9fa48("493"), p => stryMutAct_9fa48("494") ? Math.min(0, p - 1) : (stryCov_9fa48("494"), Math.max(0, stryMutAct_9fa48("495") ? p + 1 : (stryCov_9fa48("495"), p - 1))))))} disabled={stryMutAct_9fa48("498") ? page !== 0 : stryMutAct_9fa48("497") ? false : stryMutAct_9fa48("496") ? true : (stryCov_9fa48("496", "497", "498"), page === 0)} style={paginationBtnStyle(stryMutAct_9fa48("501") ? page !== 0 : stryMutAct_9fa48("500") ? false : stryMutAct_9fa48("499") ? true : (stryCov_9fa48("499", "500", "501"), page === 0))}>
            ← Previous
          </button>
          <span style={{
          padding: '0.375rem 0.625rem',
          fontSize: '0.875rem',
          color: '#374151'
        }}>
            Page {stryMutAct_9fa48("506") ? page - 1 : (stryCov_9fa48("506"), page + 1)}
          </span>
          <button onClick={stryMutAct_9fa48("507") ? () => undefined : (stryCov_9fa48("507"), () => setPage(stryMutAct_9fa48("508") ? () => undefined : (stryCov_9fa48("508"), p => stryMutAct_9fa48("509") ? p - 1 : (stryCov_9fa48("509"), p + 1))))} disabled={stryMutAct_9fa48("513") ? papers.length >= PAGE_SIZE : stryMutAct_9fa48("512") ? papers.length <= PAGE_SIZE : stryMutAct_9fa48("511") ? false : stryMutAct_9fa48("510") ? true : (stryCov_9fa48("510", "511", "512", "513"), papers.length < PAGE_SIZE)} style={paginationBtnStyle(stryMutAct_9fa48("517") ? papers.length >= PAGE_SIZE : stryMutAct_9fa48("516") ? papers.length <= PAGE_SIZE : stryMutAct_9fa48("515") ? false : stryMutAct_9fa48("514") ? true : (stryCov_9fa48("514", "515", "516", "517"), papers.length < PAGE_SIZE))}>
            Next →
          </button>
        </div>)}
    </div>;
  }
}
const selectStyle: React.CSSProperties = {
  padding: '0.375rem 0.625rem',
  border: '1px solid #d1d5db',
  borderRadius: '0.375rem',
  fontSize: '0.875rem',
  background: '#fff',
  cursor: 'pointer'
};
const clearBtnStyle: React.CSSProperties = {
  padding: '0.375rem 0.625rem',
  background: 'transparent',
  border: '1px solid #d1d5db',
  borderRadius: '0.375rem',
  cursor: 'pointer',
  fontSize: '0.8125rem',
  color: '#374151'
};
function paginationBtnStyle(disabled: boolean): React.CSSProperties {
  if (stryMutAct_9fa48("533")) {
    {}
  } else {
    stryCov_9fa48("533");
    return {
      padding: '0.375rem 0.75rem',
      background: disabled ? '#f9fafb' : '#fff',
      border: '1px solid #d1d5db',
      borderRadius: '0.375rem',
      cursor: disabled ? 'not-allowed' : 'pointer',
      fontSize: '0.875rem',
      color: disabled ? '#9ca3af' : '#374151',
      opacity: disabled ? 0.6 : 1
    };
  }
}