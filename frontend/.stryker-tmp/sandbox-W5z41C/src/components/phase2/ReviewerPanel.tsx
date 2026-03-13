/**
 * ReviewerPanel: submit accept/reject/duplicate decisions with reason selector
 * from the study's criteria list and override annotation.
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
import { api } from '../../services/api';
interface Criterion {
  id: number;
  description: string;
  order_index: number;
}
interface Reviewer {
  id: number;
  reviewer_type: string;
  user_id: number | null;
  agent_name: string | null;
}
interface ReviewerPanelProps {
  studyId: number;
  candidateId: number;
  onDecisionSubmitted?: () => void;
}
type DecisionType = 'accepted' | 'rejected' | 'duplicate';
const DECISION_STYLES: Record<DecisionType, {
  bg: string;
  text: string;
  border: string;
}> = {
  accepted: {
    bg: '#dcfce7',
    text: '#16a34a',
    border: '#16a34a'
  },
  rejected: {
    bg: '#fee2e2',
    text: '#dc2626',
    border: '#dc2626'
  },
  duplicate: {
    bg: '#f3f4f6',
    text: '#6b7280',
    border: '#6b7280'
  }
};
export default function ReviewerPanel({
  studyId,
  candidateId,
  onDecisionSubmitted
}: ReviewerPanelProps) {
  if (stryMutAct_9fa48("558")) {
    {}
  } else {
    stryCov_9fa48("558");
    const qc = useQueryClient();
    const [selectedDecision, setSelectedDecision] = useState<DecisionType | null>(null);
    const [selectedReasons, setSelectedReasons] = useState<number[]>(stryMutAct_9fa48("559") ? ["Stryker was here"] : (stryCov_9fa48("559"), []));
    const [annotationText, setAnnotationText] = useState('');
    const [reviewerId, setReviewerId] = useState<number | null>(null);
    const {
      data: inclusion = stryMutAct_9fa48("561") ? ["Stryker was here"] : (stryCov_9fa48("561"), [])
    } = useQuery<Criterion[]>({
      queryKey: stryMutAct_9fa48("563") ? [] : (stryCov_9fa48("563"), ['criteria', studyId, 'inclusion']),
      queryFn: stryMutAct_9fa48("566") ? () => undefined : (stryCov_9fa48("566"), () => api.get<Criterion[]>(`/api/v1/studies/${studyId}/criteria/inclusion`))
    });
    const {
      data: exclusion = stryMutAct_9fa48("568") ? ["Stryker was here"] : (stryCov_9fa48("568"), [])
    } = useQuery<Criterion[]>({
      queryKey: stryMutAct_9fa48("570") ? [] : (stryCov_9fa48("570"), ['criteria', studyId, 'exclusion']),
      queryFn: stryMutAct_9fa48("573") ? () => undefined : (stryCov_9fa48("573"), () => api.get<Criterion[]>(`/api/v1/studies/${studyId}/criteria/exclusion`))
    });
    const submitDecision = useMutation({
      mutationFn: stryMutAct_9fa48("576") ? () => undefined : (stryCov_9fa48("576"), (body: {
        reviewer_id: number;
        decision: string;
        reasons: object[];
      }) => api.post(`/api/v1/studies/${studyId}/papers/${candidateId}/decisions`, body)),
      onSuccess: () => {
        if (stryMutAct_9fa48("578")) {
          {}
        } else {
          stryCov_9fa48("578");
          qc.invalidateQueries({
            queryKey: stryMutAct_9fa48("580") ? [] : (stryCov_9fa48("580"), ['decisions', studyId, candidateId])
          });
          qc.invalidateQueries({
            queryKey: stryMutAct_9fa48("583") ? [] : (stryCov_9fa48("583"), ['papers', studyId])
          });
          setSelectedDecision(null);
          setSelectedReasons(stryMutAct_9fa48("585") ? ["Stryker was here"] : (stryCov_9fa48("585"), []));
          setAnnotationText('');
          stryMutAct_9fa48("587") ? onDecisionSubmitted() : (stryCov_9fa48("587"), onDecisionSubmitted?.());
        }
      }
    });
    const handleSubmit = () => {
      if (stryMutAct_9fa48("588")) {
        {}
      } else {
        stryCov_9fa48("588");
        if (stryMutAct_9fa48("591") ? !selectedDecision && reviewerId === null : stryMutAct_9fa48("590") ? false : stryMutAct_9fa48("589") ? true : (stryCov_9fa48("589", "590", "591"), (stryMutAct_9fa48("592") ? selectedDecision : (stryCov_9fa48("592"), !selectedDecision)) || (stryMutAct_9fa48("594") ? reviewerId !== null : stryMutAct_9fa48("593") ? false : (stryCov_9fa48("593", "594"), reviewerId === null)))) return;
        const reasons: object[] = stryMutAct_9fa48("595") ? [] : (stryCov_9fa48("595"), [...selectedReasons.map(id => {
          if (stryMutAct_9fa48("596")) {
            {}
          } else {
            stryCov_9fa48("596");
            const inc = inclusion.find(stryMutAct_9fa48("597") ? () => undefined : (stryCov_9fa48("597"), c => stryMutAct_9fa48("600") ? c.id !== id : stryMutAct_9fa48("599") ? false : stryMutAct_9fa48("598") ? true : (stryCov_9fa48("598", "599", "600"), c.id === id)));
            const exc = exclusion.find(stryMutAct_9fa48("601") ? () => undefined : (stryCov_9fa48("601"), c => stryMutAct_9fa48("604") ? c.id !== id : stryMutAct_9fa48("603") ? false : stryMutAct_9fa48("602") ? true : (stryCov_9fa48("602", "603", "604"), c.id === id)));
            return {
              criterion_id: id,
              criterion_type: inc ? 'inclusion' : 'exclusion',
              text: stryMutAct_9fa48("608") ? (inc ?? exc)?.description && '' : (stryCov_9fa48("608"), (stryMutAct_9fa48("609") ? (inc ?? exc).description : (stryCov_9fa48("609"), (stryMutAct_9fa48("610") ? inc && exc : (stryCov_9fa48("610"), inc ?? exc))?.description)) ?? '')
            };
          }
        }), ...((stryMutAct_9fa48("612") ? annotationText : (stryCov_9fa48("612"), annotationText.trim())) ? stryMutAct_9fa48("613") ? [] : (stryCov_9fa48("613"), [{
          criterion_type: 'annotation',
          text: stryMutAct_9fa48("616") ? annotationText : (stryCov_9fa48("616"), annotationText.trim())
        }]) : stryMutAct_9fa48("617") ? ["Stryker was here"] : (stryCov_9fa48("617"), []))]);
        submitDecision.mutate({
          reviewer_id: reviewerId,
          decision: selectedDecision,
          reasons
        });
      }
    };
    const toggleReason = (id: number) => {
      if (stryMutAct_9fa48("619")) {
        {}
      } else {
        stryCov_9fa48("619");
        setSelectedReasons(stryMutAct_9fa48("620") ? () => undefined : (stryCov_9fa48("620"), prev => prev.includes(id) ? stryMutAct_9fa48("621") ? prev : (stryCov_9fa48("621"), prev.filter(stryMutAct_9fa48("622") ? () => undefined : (stryCov_9fa48("622"), x => stryMutAct_9fa48("625") ? x === id : stryMutAct_9fa48("624") ? false : stryMutAct_9fa48("623") ? true : (stryCov_9fa48("623", "624", "625"), x !== id)))) : stryMutAct_9fa48("626") ? [] : (stryCov_9fa48("626"), [...prev, id])));
      }
    };
    const canSubmit = stryMutAct_9fa48("629") ? selectedDecision !== null && reviewerId !== null || !submitDecision.isPending : stryMutAct_9fa48("628") ? false : stryMutAct_9fa48("627") ? true : (stryCov_9fa48("627", "628", "629"), (stryMutAct_9fa48("631") ? selectedDecision !== null || reviewerId !== null : stryMutAct_9fa48("630") ? true : (stryCov_9fa48("630", "631"), (stryMutAct_9fa48("633") ? selectedDecision === null : stryMutAct_9fa48("632") ? true : (stryCov_9fa48("632", "633"), selectedDecision !== null)) && (stryMutAct_9fa48("635") ? reviewerId === null : stryMutAct_9fa48("634") ? true : (stryCov_9fa48("634", "635"), reviewerId !== null)))) && (stryMutAct_9fa48("636") ? submitDecision.isPending : (stryCov_9fa48("636"), !submitDecision.isPending)));
    return <div style={{
      border: '1px solid #e2e8f0',
      borderRadius: '0.5rem',
      padding: '1rem',
      background: '#f8fafc'
    }}>
      <h4 style={{
        margin: '0 0 0.875rem',
        fontSize: '0.9375rem',
        color: '#111827'
      }}>
        Submit Decision
      </h4>

      {/* Reviewer ID input (simplified — in real use would be populated from auth context) */}
      <div style={{
        marginBottom: '0.875rem'
      }}>
        <label style={labelStyle}>Reviewer ID</label>
        <input type="number" value={stryMutAct_9fa48("648") ? reviewerId && '' : (stryCov_9fa48("648"), reviewerId ?? '')} onChange={stryMutAct_9fa48("650") ? () => undefined : (stryCov_9fa48("650"), e => setReviewerId(e.target.value ? Number(e.target.value) : null))} placeholder="Enter reviewer ID…" style={inputStyle} />
      </div>

      {/* Decision buttons */}
      <div style={{
        marginBottom: '0.875rem'
      }}>
        <label style={labelStyle}>Decision</label>
        <div style={{
          display: 'flex',
          gap: '0.5rem'
        }}>
          {(['accepted', 'rejected', 'duplicate'] as DecisionType[]).map(d => {
            if (stryMutAct_9fa48("656")) {
              {}
            } else {
              stryCov_9fa48("656");
              const style = DECISION_STYLES[d];
              const isSelected = stryMutAct_9fa48("659") ? selectedDecision !== d : stryMutAct_9fa48("658") ? false : stryMutAct_9fa48("657") ? true : (stryCov_9fa48("657", "658", "659"), selectedDecision === d);
              return <button key={d} onClick={stryMutAct_9fa48("660") ? () => undefined : (stryCov_9fa48("660"), () => setSelectedDecision(isSelected ? null : d))} style={{
                padding: '0.5rem 1rem',
                background: isSelected ? style.text : '#fff',
                color: isSelected ? '#fff' : style.text,
                border: `2px solid ${style.border}`,
                borderRadius: '0.375rem',
                cursor: 'pointer',
                fontSize: '0.875rem',
                fontWeight: 600,
                textTransform: 'capitalize',
                transition: 'all 0.1s'
              }}>
                {d}
              </button>;
            }
          })}
        </div>
      </div>

      {/* Criteria reason selector */}
      {stryMutAct_9fa48("673") ? selectedDecision && (inclusion.length > 0 || exclusion.length > 0) || <div style={{
        marginBottom: '0.875rem'
      }}>
          <label style={labelStyle}>Reasons (select criteria)</label>
          <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '0.375rem',
          maxHeight: '160px',
          overflowY: 'auto'
        }}>
            {inclusion.length > 0 && <div>
                <div style={groupLabelStyle}>Inclusion Criteria</div>
                {inclusion.map(c => <CriterionCheckbox key={c.id} criterion={c} checked={selectedReasons.includes(c.id)} onChange={() => toggleReason(c.id)} />)}
              </div>}
            {exclusion.length > 0 && <div>
                <div style={groupLabelStyle}>Exclusion Criteria</div>
                {exclusion.map(c => <CriterionCheckbox key={c.id} criterion={c} checked={selectedReasons.includes(c.id)} onChange={() => toggleReason(c.id)} />)}
              </div>}
          </div>
        </div> : stryMutAct_9fa48("672") ? false : stryMutAct_9fa48("671") ? true : (stryCov_9fa48("671", "672", "673"), (stryMutAct_9fa48("675") ? selectedDecision || inclusion.length > 0 || exclusion.length > 0 : stryMutAct_9fa48("674") ? true : (stryCov_9fa48("674", "675"), selectedDecision && (stryMutAct_9fa48("677") ? inclusion.length > 0 && exclusion.length > 0 : stryMutAct_9fa48("676") ? true : (stryCov_9fa48("676", "677"), (stryMutAct_9fa48("680") ? inclusion.length <= 0 : stryMutAct_9fa48("679") ? inclusion.length >= 0 : stryMutAct_9fa48("678") ? false : (stryCov_9fa48("678", "679", "680"), inclusion.length > 0)) || (stryMutAct_9fa48("683") ? exclusion.length <= 0 : stryMutAct_9fa48("682") ? exclusion.length >= 0 : stryMutAct_9fa48("681") ? false : (stryCov_9fa48("681", "682", "683"), exclusion.length > 0)))))) && <div style={{
        marginBottom: '0.875rem'
      }}>
          <label style={labelStyle}>Reasons (select criteria)</label>
          <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '0.375rem',
          maxHeight: '160px',
          overflowY: 'auto'
        }}>
            {stryMutAct_9fa48("694") ? inclusion.length > 0 || <div>
                <div style={groupLabelStyle}>Inclusion Criteria</div>
                {inclusion.map(c => <CriterionCheckbox key={c.id} criterion={c} checked={selectedReasons.includes(c.id)} onChange={() => toggleReason(c.id)} />)}
              </div> : stryMutAct_9fa48("693") ? false : stryMutAct_9fa48("692") ? true : (stryCov_9fa48("692", "693", "694"), (stryMutAct_9fa48("697") ? inclusion.length <= 0 : stryMutAct_9fa48("696") ? inclusion.length >= 0 : stryMutAct_9fa48("695") ? true : (stryCov_9fa48("695", "696", "697"), inclusion.length > 0)) && <div>
                <div style={groupLabelStyle}>Inclusion Criteria</div>
                {inclusion.map(stryMutAct_9fa48("698") ? () => undefined : (stryCov_9fa48("698"), c => <CriterionCheckbox key={c.id} criterion={c} checked={selectedReasons.includes(c.id)} onChange={stryMutAct_9fa48("699") ? () => undefined : (stryCov_9fa48("699"), () => toggleReason(c.id))} />))}
              </div>)}
            {stryMutAct_9fa48("702") ? exclusion.length > 0 || <div>
                <div style={groupLabelStyle}>Exclusion Criteria</div>
                {exclusion.map(c => <CriterionCheckbox key={c.id} criterion={c} checked={selectedReasons.includes(c.id)} onChange={() => toggleReason(c.id)} />)}
              </div> : stryMutAct_9fa48("701") ? false : stryMutAct_9fa48("700") ? true : (stryCov_9fa48("700", "701", "702"), (stryMutAct_9fa48("705") ? exclusion.length <= 0 : stryMutAct_9fa48("704") ? exclusion.length >= 0 : stryMutAct_9fa48("703") ? true : (stryCov_9fa48("703", "704", "705"), exclusion.length > 0)) && <div>
                <div style={groupLabelStyle}>Exclusion Criteria</div>
                {exclusion.map(stryMutAct_9fa48("706") ? () => undefined : (stryCov_9fa48("706"), c => <CriterionCheckbox key={c.id} criterion={c} checked={selectedReasons.includes(c.id)} onChange={stryMutAct_9fa48("707") ? () => undefined : (stryCov_9fa48("707"), () => toggleReason(c.id))} />))}
              </div>)}
          </div>
        </div>)}

      {/* Override annotation */}
      <div style={{
        marginBottom: '0.875rem'
      }}>
        <label style={labelStyle}>Additional notes / override annotation</label>
        <textarea value={annotationText} onChange={stryMutAct_9fa48("710") ? () => undefined : (stryCov_9fa48("710"), e => setAnnotationText(e.target.value))} placeholder="Optional annotation…" rows={2} style={{
          ...inputStyle,
          resize: 'vertical',
          fontFamily: 'inherit'
        }} />
      </div>

      {/* Submit */}
      <button onClick={handleSubmit} disabled={stryMutAct_9fa48("714") ? canSubmit : (stryCov_9fa48("714"), !canSubmit)} style={{
        padding: '0.5rem 1.25rem',
        background: canSubmit ? '#2563eb' : '#93c5fd',
        color: '#fff',
        border: 'none',
        borderRadius: '0.375rem',
        cursor: canSubmit ? 'pointer' : 'not-allowed',
        fontSize: '0.875rem',
        fontWeight: 600
      }}>
        {submitDecision.isPending ? 'Submitting…' : 'Submit Decision'}
      </button>

      {stryMutAct_9fa48("729") ? submitDecision.isError || <p style={{
        margin: '0.5rem 0 0',
        color: '#ef4444',
        fontSize: '0.8125rem'
      }}>
          Failed to submit decision. Please try again.
        </p> : stryMutAct_9fa48("728") ? false : stryMutAct_9fa48("727") ? true : (stryCov_9fa48("727", "728", "729"), submitDecision.isError && <p style={{
        margin: '0.5rem 0 0',
        color: '#ef4444',
        fontSize: '0.8125rem'
      }}>
          Failed to submit decision. Please try again.
        </p>)}

      {stryMutAct_9fa48("736") ? submitDecision.isSuccess || <p style={{
        margin: '0.5rem 0 0',
        color: '#16a34a',
        fontSize: '0.8125rem'
      }}>
          Decision submitted.
        </p> : stryMutAct_9fa48("735") ? false : stryMutAct_9fa48("734") ? true : (stryCov_9fa48("734", "735", "736"), submitDecision.isSuccess && <p style={{
        margin: '0.5rem 0 0',
        color: '#16a34a',
        fontSize: '0.8125rem'
      }}>
          Decision submitted.
        </p>)}
    </div>;
  }
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function CriterionCheckbox({
  criterion,
  checked,
  onChange
}: {
  criterion: Criterion;
  checked: boolean;
  onChange: () => void;
}) {
  if (stryMutAct_9fa48("741")) {
    {}
  } else {
    stryCov_9fa48("741");
    return <label style={{
      display: 'flex',
      alignItems: 'flex-start',
      gap: '0.375rem',
      cursor: 'pointer',
      padding: '0.1875rem 0'
    }}>
      <input type="checkbox" checked={checked} onChange={onChange} style={{
        flexShrink: 0,
        marginTop: '2px'
      }} />
      <span style={{
        fontSize: '0.8125rem',
        color: '#374151'
      }}>
        {criterion.description}
      </span>
    </label>;
  }
}

// ---------------------------------------------------------------------------
// Shared styles
// ---------------------------------------------------------------------------

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: '0.8125rem',
  fontWeight: 600,
  color: '#374151',
  marginBottom: '0.375rem'
};
const groupLabelStyle: React.CSSProperties = {
  fontSize: '0.6875rem',
  fontWeight: 700,
  color: '#9ca3af',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  padding: '0.25rem 0'
};
const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '0.375rem 0.625rem',
  border: '1px solid #d1d5db',
  borderRadius: '0.375rem',
  fontSize: '0.875rem',
  background: '#fff',
  boxSizing: 'border-box'
};