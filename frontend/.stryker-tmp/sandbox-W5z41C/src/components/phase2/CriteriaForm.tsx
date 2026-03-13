/**
 * CriteriaForm: add/remove inclusion and exclusion criteria with reorder support.
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
  study_id: number;
  description: string;
  order_index: number;
}
interface CriteriaFormProps {
  studyId: number;
}
function CriterionList({
  title,
  items,
  onAdd,
  onDelete,
  onMoveUp,
  onMoveDown,
  isAdding
}: {
  title: string;
  items: Criterion[];
  onAdd: (description: string) => void;
  onDelete: (id: number) => void;
  onMoveUp: (index: number) => void;
  onMoveDown: (index: number) => void;
  isAdding: boolean;
}) {
  if (stryMutAct_9fa48("0")) {
    {}
  } else {
    stryCov_9fa48("0");
    const [newText, setNewText] = useState('');
    const handleAdd = () => {
      if (stryMutAct_9fa48("2")) {
        {}
      } else {
        stryCov_9fa48("2");
        const trimmed = stryMutAct_9fa48("3") ? newText : (stryCov_9fa48("3"), newText.trim());
        if (stryMutAct_9fa48("6") ? false : stryMutAct_9fa48("5") ? true : stryMutAct_9fa48("4") ? trimmed : (stryCov_9fa48("4", "5", "6"), !trimmed)) return;
        onAdd(trimmed);
        setNewText('');
      }
    };
    return <div style={{
      marginBottom: '1.5rem'
    }}>
      <h4 style={{
        margin: '0 0 0.75rem',
        fontSize: '0.9375rem',
        color: '#374151'
      }}>{title}</h4>

      <ol style={{
        margin: '0 0 0.75rem',
        paddingLeft: '1.5rem'
      }}>
        {items.map(stryMutAct_9fa48("17") ? () => undefined : (stryCov_9fa48("17"), (item, idx) => <li key={item.id} style={{
          marginBottom: '0.5rem',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '0.5rem'
        }}>
            <span style={{
            flex: 1,
            fontSize: '0.875rem',
            color: '#374151',
            paddingTop: '2px'
          }}>
              {item.description}
            </span>
            <div style={{
            display: 'flex',
            gap: '0.25rem',
            flexShrink: 0
          }}>
              <button onClick={stryMutAct_9fa48("30") ? () => undefined : (stryCov_9fa48("30"), () => onMoveUp(idx))} disabled={stryMutAct_9fa48("33") ? idx !== 0 : stryMutAct_9fa48("32") ? false : stryMutAct_9fa48("31") ? true : (stryCov_9fa48("31", "32", "33"), idx === 0)} title="Move up" style={reorderBtnStyle(stryMutAct_9fa48("36") ? idx !== 0 : stryMutAct_9fa48("35") ? false : stryMutAct_9fa48("34") ? true : (stryCov_9fa48("34", "35", "36"), idx === 0))}>
                ↑
              </button>
              <button onClick={stryMutAct_9fa48("37") ? () => undefined : (stryCov_9fa48("37"), () => onMoveDown(idx))} disabled={stryMutAct_9fa48("40") ? idx !== items.length - 1 : stryMutAct_9fa48("39") ? false : stryMutAct_9fa48("38") ? true : (stryCov_9fa48("38", "39", "40"), idx === (stryMutAct_9fa48("41") ? items.length + 1 : (stryCov_9fa48("41"), items.length - 1)))} title="Move down" style={reorderBtnStyle(stryMutAct_9fa48("44") ? idx !== items.length - 1 : stryMutAct_9fa48("43") ? false : stryMutAct_9fa48("42") ? true : (stryCov_9fa48("42", "43", "44"), idx === (stryMutAct_9fa48("45") ? items.length + 1 : (stryCov_9fa48("45"), items.length - 1))))}>
                ↓
              </button>
              <button onClick={stryMutAct_9fa48("46") ? () => undefined : (stryCov_9fa48("46"), () => onDelete(item.id))} title="Remove" style={{
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              color: '#ef4444',
              fontSize: '0.875rem',
              padding: '0 4px'
            }}>
                ✕
              </button>
            </div>
          </li>))}
        {stryMutAct_9fa48("56") ? items.length === 0 || <li style={{
          fontSize: '0.875rem',
          color: '#9ca3af',
          listStyle: 'none',
          marginLeft: '-1.5rem'
        }}>
            No criteria added yet.
          </li> : stryMutAct_9fa48("55") ? false : stryMutAct_9fa48("54") ? true : (stryCov_9fa48("54", "55", "56"), (stryMutAct_9fa48("58") ? items.length !== 0 : stryMutAct_9fa48("57") ? true : (stryCov_9fa48("57", "58"), items.length === 0)) && <li style={{
          fontSize: '0.875rem',
          color: '#9ca3af',
          listStyle: 'none',
          marginLeft: '-1.5rem'
        }}>
            No criteria added yet.
          </li>)}
      </ol>

      <div style={{
        display: 'flex',
        gap: '0.5rem'
      }}>
        <input value={newText} onChange={stryMutAct_9fa48("67") ? () => undefined : (stryCov_9fa48("67"), e => setNewText(e.target.value))} onKeyDown={stryMutAct_9fa48("68") ? () => undefined : (stryCov_9fa48("68"), e => stryMutAct_9fa48("71") ? e.key === 'Enter' || handleAdd() : stryMutAct_9fa48("70") ? false : stryMutAct_9fa48("69") ? true : (stryCov_9fa48("69", "70", "71"), (stryMutAct_9fa48("73") ? e.key !== 'Enter' : stryMutAct_9fa48("72") ? true : (stryCov_9fa48("72", "73"), e.key === 'Enter')) && handleAdd()))} placeholder="Add criterion…" style={{
          flex: 1,
          padding: '0.375rem 0.625rem',
          border: '1px solid #d1d5db',
          borderRadius: '0.375rem',
          fontSize: '0.875rem'
        }} />
        <button onClick={handleAdd} disabled={stryMutAct_9fa48("82") ? isAdding && !newText.trim() : stryMutAct_9fa48("81") ? false : stryMutAct_9fa48("80") ? true : (stryCov_9fa48("80", "81", "82"), isAdding || (stryMutAct_9fa48("83") ? newText.trim() : (stryCov_9fa48("83"), !(stryMutAct_9fa48("84") ? newText : (stryCov_9fa48("84"), newText.trim())))))} style={{
          padding: '0.375rem 0.75rem',
          background: '#2563eb',
          color: '#fff',
          border: 'none',
          borderRadius: '0.375rem',
          cursor: (stryMutAct_9fa48("93") ? isAdding && !newText.trim() : stryMutAct_9fa48("92") ? false : stryMutAct_9fa48("91") ? true : (stryCov_9fa48("91", "92", "93"), isAdding || (stryMutAct_9fa48("94") ? newText.trim() : (stryCov_9fa48("94"), !(stryMutAct_9fa48("95") ? newText : (stryCov_9fa48("95"), newText.trim())))))) ? 'not-allowed' : 'pointer',
          fontSize: '0.875rem',
          opacity: (stryMutAct_9fa48("101") ? isAdding && !newText.trim() : stryMutAct_9fa48("100") ? false : stryMutAct_9fa48("99") ? true : (stryCov_9fa48("99", "100", "101"), isAdding || (stryMutAct_9fa48("102") ? newText.trim() : (stryCov_9fa48("102"), !(stryMutAct_9fa48("103") ? newText : (stryCov_9fa48("103"), newText.trim())))))) ? 0.6 : 1
        }}>
          Add
        </button>
      </div>
    </div>;
  }
}
function reorderBtnStyle(disabled: boolean) {
  if (stryMutAct_9fa48("104")) {
    {}
  } else {
    stryCov_9fa48("104");
    return {
      background: 'transparent',
      border: '1px solid #d1d5db',
      borderRadius: '0.25rem',
      cursor: disabled ? 'not-allowed' : 'pointer',
      color: disabled ? '#9ca3af' : '#374151',
      fontSize: '0.75rem',
      padding: '0 4px',
      opacity: disabled ? 0.5 : 1
    } as const;
  }
}
export default function CriteriaForm({
  studyId
}: CriteriaFormProps) {
  if (stryMutAct_9fa48("105")) {
    {}
  } else {
    stryCov_9fa48("105");
    const qc = useQueryClient();
    const {
      data: inclusion = stryMutAct_9fa48("106") ? ["Stryker was here"] : (stryCov_9fa48("106"), [])
    } = useQuery<Criterion[]>({
      queryKey: stryMutAct_9fa48("108") ? [] : (stryCov_9fa48("108"), ['criteria', studyId, 'inclusion']),
      queryFn: stryMutAct_9fa48("111") ? () => undefined : (stryCov_9fa48("111"), () => api.get<Criterion[]>(`/api/v1/studies/${studyId}/criteria/inclusion`))
    });
    const {
      data: exclusion = stryMutAct_9fa48("113") ? ["Stryker was here"] : (stryCov_9fa48("113"), [])
    } = useQuery<Criterion[]>({
      queryKey: stryMutAct_9fa48("115") ? [] : (stryCov_9fa48("115"), ['criteria', studyId, 'exclusion']),
      queryFn: stryMutAct_9fa48("118") ? () => undefined : (stryCov_9fa48("118"), () => api.get<Criterion[]>(`/api/v1/studies/${studyId}/criteria/exclusion`))
    });
    const addInclusion = useMutation({
      mutationFn: stryMutAct_9fa48("121") ? () => undefined : (stryCov_9fa48("121"), (description: string) => api.post<Criterion>(`/api/v1/studies/${studyId}/criteria/inclusion`, {
        description,
        order_index: inclusion.length
      })),
      onSuccess: stryMutAct_9fa48("124") ? () => undefined : (stryCov_9fa48("124"), () => qc.invalidateQueries({
        queryKey: stryMutAct_9fa48("126") ? [] : (stryCov_9fa48("126"), ['criteria', studyId, 'inclusion'])
      }))
    });
    const addExclusion = useMutation({
      mutationFn: stryMutAct_9fa48("130") ? () => undefined : (stryCov_9fa48("130"), (description: string) => api.post<Criterion>(`/api/v1/studies/${studyId}/criteria/exclusion`, {
        description,
        order_index: exclusion.length
      })),
      onSuccess: stryMutAct_9fa48("133") ? () => undefined : (stryCov_9fa48("133"), () => qc.invalidateQueries({
        queryKey: stryMutAct_9fa48("135") ? [] : (stryCov_9fa48("135"), ['criteria', studyId, 'exclusion'])
      }))
    });
    const deleteInclusion = useMutation({
      mutationFn: stryMutAct_9fa48("139") ? () => undefined : (stryCov_9fa48("139"), (id: number) => api.delete<void>(`/api/v1/studies/${studyId}/criteria/inclusion/${id}`)),
      onSuccess: stryMutAct_9fa48("141") ? () => undefined : (stryCov_9fa48("141"), () => qc.invalidateQueries({
        queryKey: stryMutAct_9fa48("143") ? [] : (stryCov_9fa48("143"), ['criteria', studyId, 'inclusion'])
      }))
    });
    const deleteExclusion = useMutation({
      mutationFn: stryMutAct_9fa48("147") ? () => undefined : (stryCov_9fa48("147"), (id: number) => api.delete<void>(`/api/v1/studies/${studyId}/criteria/exclusion/${id}`)),
      onSuccess: stryMutAct_9fa48("149") ? () => undefined : (stryCov_9fa48("149"), () => qc.invalidateQueries({
        queryKey: stryMutAct_9fa48("151") ? [] : (stryCov_9fa48("151"), ['criteria', studyId, 'exclusion'])
      }))
    });

    // Reorder helpers — optimistic local reorder (no server-side order endpoint needed)
    const [incOrder, setIncOrder] = useState<number[] | null>(null);
    const [excOrder, setExcOrder] = useState<number[] | null>(null);
    const sortedInclusion = incOrder ? stryMutAct_9fa48("154") ? [...inclusion] : (stryCov_9fa48("154"), (stryMutAct_9fa48("155") ? [] : (stryCov_9fa48("155"), [...inclusion])).sort(stryMutAct_9fa48("156") ? () => undefined : (stryCov_9fa48("156"), (a, b) => stryMutAct_9fa48("157") ? incOrder.indexOf(a.id) + incOrder.indexOf(b.id) : (stryCov_9fa48("157"), incOrder.indexOf(a.id) - incOrder.indexOf(b.id))))) : stryMutAct_9fa48("158") ? [...inclusion] : (stryCov_9fa48("158"), (stryMutAct_9fa48("159") ? [] : (stryCov_9fa48("159"), [...inclusion])).sort(stryMutAct_9fa48("160") ? () => undefined : (stryCov_9fa48("160"), (a, b) => stryMutAct_9fa48("161") ? a.order_index + b.order_index : (stryCov_9fa48("161"), a.order_index - b.order_index))));
    const sortedExclusion = excOrder ? stryMutAct_9fa48("162") ? [...exclusion] : (stryCov_9fa48("162"), (stryMutAct_9fa48("163") ? [] : (stryCov_9fa48("163"), [...exclusion])).sort(stryMutAct_9fa48("164") ? () => undefined : (stryCov_9fa48("164"), (a, b) => stryMutAct_9fa48("165") ? excOrder.indexOf(a.id) + excOrder.indexOf(b.id) : (stryCov_9fa48("165"), excOrder.indexOf(a.id) - excOrder.indexOf(b.id))))) : stryMutAct_9fa48("166") ? [...exclusion] : (stryCov_9fa48("166"), (stryMutAct_9fa48("167") ? [] : (stryCov_9fa48("167"), [...exclusion])).sort(stryMutAct_9fa48("168") ? () => undefined : (stryCov_9fa48("168"), (a, b) => stryMutAct_9fa48("169") ? a.order_index + b.order_index : (stryCov_9fa48("169"), a.order_index - b.order_index))));
    const moveInc = (idx: number, dir: -1 | 1) => {
      if (stryMutAct_9fa48("170")) {
        {}
      } else {
        stryCov_9fa48("170");
        const ordered = sortedInclusion.map(stryMutAct_9fa48("171") ? () => undefined : (stryCov_9fa48("171"), c => c.id));
        const swapIdx = stryMutAct_9fa48("172") ? idx - dir : (stryCov_9fa48("172"), idx + dir);
        [ordered[idx], ordered[swapIdx]] = stryMutAct_9fa48("173") ? [] : (stryCov_9fa48("173"), [ordered[swapIdx], ordered[idx]]);
        setIncOrder(ordered);
      }
    };
    const moveExc = (idx: number, dir: -1 | 1) => {
      if (stryMutAct_9fa48("174")) {
        {}
      } else {
        stryCov_9fa48("174");
        const ordered = sortedExclusion.map(stryMutAct_9fa48("175") ? () => undefined : (stryCov_9fa48("175"), c => c.id));
        const swapIdx = stryMutAct_9fa48("176") ? idx - dir : (stryCov_9fa48("176"), idx + dir);
        [ordered[idx], ordered[swapIdx]] = stryMutAct_9fa48("177") ? [] : (stryCov_9fa48("177"), [ordered[swapIdx], ordered[idx]]);
        setExcOrder(ordered);
      }
    };
    return <div>
      <h3 style={{
        margin: '0 0 1rem',
        fontSize: '1rem',
        color: '#111827'
      }}>
        Inclusion / Exclusion Criteria
      </h3>

      <CriterionList title="Inclusion Criteria" items={sortedInclusion} onAdd={stryMutAct_9fa48("182") ? () => undefined : (stryCov_9fa48("182"), desc => addInclusion.mutate(desc))} onDelete={stryMutAct_9fa48("183") ? () => undefined : (stryCov_9fa48("183"), id => deleteInclusion.mutate(id))} onMoveUp={stryMutAct_9fa48("184") ? () => undefined : (stryCov_9fa48("184"), idx => moveInc(idx, stryMutAct_9fa48("185") ? +1 : (stryCov_9fa48("185"), -1)))} onMoveDown={stryMutAct_9fa48("186") ? () => undefined : (stryCov_9fa48("186"), idx => moveInc(idx, 1))} isAdding={addInclusion.isPending} />

      <CriterionList title="Exclusion Criteria" items={sortedExclusion} onAdd={stryMutAct_9fa48("187") ? () => undefined : (stryCov_9fa48("187"), desc => addExclusion.mutate(desc))} onDelete={stryMutAct_9fa48("188") ? () => undefined : (stryCov_9fa48("188"), id => deleteExclusion.mutate(id))} onMoveUp={stryMutAct_9fa48("189") ? () => undefined : (stryCov_9fa48("189"), idx => moveExc(idx, stryMutAct_9fa48("190") ? +1 : (stryCov_9fa48("190"), -1)))} onMoveDown={stryMutAct_9fa48("191") ? () => undefined : (stryCov_9fa48("191"), idx => moveExc(idx, 1))} isAdding={addExclusion.isPending} />
    </div>;
  }
}