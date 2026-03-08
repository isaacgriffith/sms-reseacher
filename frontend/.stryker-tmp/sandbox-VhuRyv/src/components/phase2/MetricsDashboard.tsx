/**
 * MetricsDashboard: displays per-phase and total search metrics funnel
 * (identified → accepted → rejected → duplicates) for a study.
 *
 * Consumes GET /studies/{study_id}/metrics
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
import { useQuery } from '@tanstack/react-query';
import { api } from '../../services/api';
interface PhaseMetrics {
  phase_tag: string;
  search_execution_id: number;
  total_identified: number;
  accepted: number;
  rejected: number;
  duplicates: number;
}
interface StudyMetricsResponse {
  study_id: number;
  phases: PhaseMetrics[];
  totals: PhaseMetrics;
}
interface MetricsDashboardProps {
  studyId: number;
}
const BAR_COLORS: Record<string, string> = {
  total_identified: '#3b82f6',
  accepted: '#16a34a',
  rejected: '#dc2626',
  duplicates: '#6b7280'
};
const BAR_LABELS: Record<string, string> = {
  total_identified: 'Identified',
  accepted: 'Accepted',
  rejected: 'Rejected',
  duplicates: 'Duplicates'
};
function FunnelBar({
  label,
  value,
  max,
  color
}: {
  label: string;
  value: number;
  max: number;
  color: string;
}) {
  if (stryMutAct_9fa48("202")) {
    {}
  } else {
    stryCov_9fa48("202");
    const pct = (stryMutAct_9fa48("206") ? max <= 0 : stryMutAct_9fa48("205") ? max >= 0 : stryMutAct_9fa48("204") ? false : stryMutAct_9fa48("203") ? true : (stryCov_9fa48("203", "204", "205", "206"), max > 0)) ? Math.round(stryMutAct_9fa48("207") ? value / max / 100 : (stryCov_9fa48("207"), (stryMutAct_9fa48("208") ? value * max : (stryCov_9fa48("208"), value / max)) * 100)) : 0;
    return <div style={{
      marginBottom: '0.5rem'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        fontSize: '0.8125rem',
        color: '#374151',
        marginBottom: '0.2rem'
      }}>
        <span>{label}</span>
        <span style={{
          fontWeight: 600,
          color
        }}>
          {value.toLocaleString()}
          {stryMutAct_9fa48("220") ? max > 0 || <span style={{
            fontWeight: 400,
            color: '#9ca3af',
            marginLeft: '0.25rem'
          }}>
              ({pct}%)
            </span> : stryMutAct_9fa48("219") ? false : stryMutAct_9fa48("218") ? true : (stryCov_9fa48("218", "219", "220"), (stryMutAct_9fa48("223") ? max <= 0 : stryMutAct_9fa48("222") ? max >= 0 : stryMutAct_9fa48("221") ? true : (stryCov_9fa48("221", "222", "223"), max > 0)) && <span style={{
            fontWeight: 400,
            color: '#9ca3af',
            marginLeft: '0.25rem'
          }}>
              ({pct}%)
            </span>)}
        </span>
      </div>
      <div style={{
        height: '0.5rem',
        background: '#f1f5f9',
        borderRadius: '9999px',
        overflow: 'hidden'
      }}>
        <div style={{
          width: `${pct}%`,
          height: '100%',
          background: color,
          borderRadius: '9999px',
          transition: 'width 0.3s ease'
        }} />
      </div>
    </div>;
  }
}
function PhaseCard({
  phase
}: {
  phase: PhaseMetrics;
}) {
  if (stryMutAct_9fa48("237")) {
    {}
  } else {
    stryCov_9fa48("237");
    const max = phase.total_identified;
    return <div style={{
      border: '1px solid #e2e8f0',
      borderRadius: '0.5rem',
      padding: '1rem',
      background: '#fff'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '0.875rem'
      }}>
        <h4 style={{
          margin: 0,
          fontSize: '0.9375rem',
          color: '#111827'
        }}>
          {(stryMutAct_9fa48("253") ? phase.phase_tag !== 'all' : stryMutAct_9fa48("252") ? false : stryMutAct_9fa48("251") ? true : (stryCov_9fa48("251", "252", "253"), phase.phase_tag === 'all')) ? 'All Phases (Totals)' : phase.phase_tag}
        </h4>
        {stryMutAct_9fa48("258") ? phase.phase_tag !== 'all' || <span style={{
          fontSize: '0.6875rem',
          color: '#6b7280',
          background: '#f1f5f9',
          padding: '0.125rem 0.375rem',
          borderRadius: '0.25rem'
        }}>
            exec #{phase.search_execution_id}
          </span> : stryMutAct_9fa48("257") ? false : stryMutAct_9fa48("256") ? true : (stryCov_9fa48("256", "257", "258"), (stryMutAct_9fa48("260") ? phase.phase_tag === 'all' : stryMutAct_9fa48("259") ? true : (stryCov_9fa48("259", "260"), phase.phase_tag !== 'all')) && <span style={{
          fontSize: '0.6875rem',
          color: '#6b7280',
          background: '#f1f5f9',
          padding: '0.125rem 0.375rem',
          borderRadius: '0.25rem'
        }}>
            exec #{phase.search_execution_id}
          </span>)}
      </div>

      {(['total_identified', 'accepted', 'rejected', 'duplicates'] as const).map(stryMutAct_9fa48("268") ? () => undefined : (stryCov_9fa48("268"), key => <FunnelBar key={key} label={BAR_LABELS[key]} value={phase[key]} max={max} color={BAR_COLORS[key]} />))}
    </div>;
  }
}
export default function MetricsDashboard({
  studyId
}: MetricsDashboardProps) {
  if (stryMutAct_9fa48("269")) {
    {}
  } else {
    stryCov_9fa48("269");
    const {
      data,
      isLoading,
      isError,
      error
    } = useQuery<StudyMetricsResponse>({
      queryKey: stryMutAct_9fa48("271") ? [] : (stryCov_9fa48("271"), ['metrics', studyId]),
      queryFn: stryMutAct_9fa48("273") ? () => undefined : (stryCov_9fa48("273"), () => api.get<StudyMetricsResponse>(`/api/v1/studies/${studyId}/metrics`)),
      staleTime: 30_000
    });
    if (stryMutAct_9fa48("276") ? false : stryMutAct_9fa48("275") ? true : (stryCov_9fa48("275", "276"), isLoading)) {
      if (stryMutAct_9fa48("277")) {
        {}
      } else {
        stryCov_9fa48("277");
        return <div style={{
          padding: '1.5rem',
          color: '#6b7280',
          fontSize: '0.875rem'
        }}>
        Loading metrics…
      </div>;
      }
    }
    if (stryMutAct_9fa48("283") ? false : stryMutAct_9fa48("282") ? true : (stryCov_9fa48("282", "283"), isError)) {
      if (stryMutAct_9fa48("284")) {
        {}
      } else {
        stryCov_9fa48("284");
        return <div style={{
          padding: '1rem',
          border: '1px solid #fecaca',
          borderRadius: '0.5rem',
          background: '#fef2f2',
          color: '#dc2626',
          fontSize: '0.875rem'
        }}>
        Failed to load metrics: {stryMutAct_9fa48("292") ? (error as Error)?.message && 'Unknown error' : (stryCov_9fa48("292"), (stryMutAct_9fa48("293") ? (error as Error).message : (stryCov_9fa48("293"), (error as Error)?.message)) ?? 'Unknown error')}
      </div>;
      }
    }
    if (stryMutAct_9fa48("297") ? !data && data.phases.length === 0 : stryMutAct_9fa48("296") ? false : stryMutAct_9fa48("295") ? true : (stryCov_9fa48("295", "296", "297"), (stryMutAct_9fa48("298") ? data : (stryCov_9fa48("298"), !data)) || (stryMutAct_9fa48("300") ? data.phases.length !== 0 : stryMutAct_9fa48("299") ? false : (stryCov_9fa48("299", "300"), data.phases.length === 0)))) {
      if (stryMutAct_9fa48("301")) {
        {}
      } else {
        stryCov_9fa48("301");
        return <div style={{
          padding: '2rem',
          textAlign: 'center',
          color: '#6b7280',
          fontSize: '0.875rem',
          background: '#f8fafc',
          borderRadius: '0.5rem',
          border: '1px solid #e2e8f0'
        }}>
        No search metrics yet. Run a search to see the funnel.
      </div>;
      }
    }
    return <section>
      <h3 style={{
        margin: '0 0 1rem',
        fontSize: '1rem',
        color: '#111827',
        fontWeight: 700
      }}>
        Search Metrics
      </h3>

      {/* Per-phase cards */}
      {stryMutAct_9fa48("316") ? data.phases.length > 0 || <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
        gap: '0.75rem',
        marginBottom: '0.75rem'
      }}>
          {data.phases.map(phase => <PhaseCard key={phase.phase_tag} phase={phase} />)}
        </div> : stryMutAct_9fa48("315") ? false : stryMutAct_9fa48("314") ? true : (stryCov_9fa48("314", "315", "316"), (stryMutAct_9fa48("319") ? data.phases.length <= 0 : stryMutAct_9fa48("318") ? data.phases.length >= 0 : stryMutAct_9fa48("317") ? true : (stryCov_9fa48("317", "318", "319"), data.phases.length > 0)) && <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
        gap: '0.75rem',
        marginBottom: '0.75rem'
      }}>
          {data.phases.map(stryMutAct_9fa48("325") ? () => undefined : (stryCov_9fa48("325"), phase => <PhaseCard key={phase.phase_tag} phase={phase} />))}
        </div>)}

      {/* Totals card (only shown when >1 phase) */}
      {stryMutAct_9fa48("328") ? data.phases.length > 1 || <PhaseCard phase={data.totals} /> : stryMutAct_9fa48("327") ? false : stryMutAct_9fa48("326") ? true : (stryCov_9fa48("326", "327", "328"), (stryMutAct_9fa48("331") ? data.phases.length <= 1 : stryMutAct_9fa48("330") ? data.phases.length >= 1 : stryMutAct_9fa48("329") ? true : (stryCov_9fa48("329", "330", "331"), data.phases.length > 1)) && <PhaseCard phase={data.totals} />)}
    </section>;
  }
}