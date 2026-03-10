/**
 * Study page: phase router rendering phase 1–5 tabs based on unlocked_phases.
 */

import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import PICOForm from '../components/phase1/PICOForm';
import SeedPapers from '../components/phase1/SeedPapers';

interface StudyDetail {
  id: number;
  name: string;
  topic: string | null;
  study_type: string;
  status: string;
  current_phase: number;
  motivation: string | null;
  research_objectives: string[];
  research_questions: string[];
  snowball_threshold: number;
  unlocked_phases: number[];
  created_at: string;
  updated_at: string;
}

const PHASE_META = [
  { phase: 1, label: 'Scoping', icon: '🎯' },
  { phase: 2, label: 'Search', icon: '🔍' },
  { phase: 3, label: 'Screening', icon: '📋' },
  { phase: 4, label: 'Extraction', icon: '📊' },
  { phase: 5, label: 'Reporting', icon: '📄' },
];

export default function StudyPage() {
  const { studyId } = useParams<{ studyId: string }>();
  const [activePhase, setActivePhase] = useState(1);

  const { data: study, isLoading, error } = useQuery<StudyDetail>({
    queryKey: ['study', studyId],
    queryFn: () => api.get<StudyDetail>(`/api/v1/studies/${studyId}`),
    enabled: !!studyId,
  });

  if (isLoading) return <p>Loading study…</p>;
  if (error || !study) return <p style={{ color: 'red' }}>Failed to load study.</p>;

  const unlocked = new Set(study.unlocked_phases);

  return (
    <div>
      {/* Study header */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ margin: '0 0 0.25rem' }}>{study.name}</h2>
        {study.topic && (
          <p style={{ margin: '0 0 0.5rem', color: '#64748b' }}>{study.topic}</p>
        )}
        <div style={{ display: 'flex', gap: '1rem', fontSize: '0.875rem', color: '#64748b' }}>
          <span>{study.study_type}</span>
          <span>·</span>
          <span style={{ textTransform: 'capitalize' }}>{study.status}</span>
          <span>·</span>
          <span>Snowball threshold: {study.snowball_threshold}</span>
        </div>
      </div>

      {/* Phase tabs */}
      <div
        style={{
          display: 'flex',
          gap: '0',
          marginBottom: '2rem',
          borderBottom: '2px solid #e2e8f0',
        }}
      >
        {PHASE_META.map(({ phase, label, icon }) => {
          const isUnlocked = unlocked.has(phase);
          const isActive = activePhase === phase;
          return (
            <button
              key={phase}
              onClick={() => isUnlocked && setActivePhase(phase)}
              style={{
                padding: '0.625rem 1rem',
                background: 'transparent',
                border: 'none',
                borderBottom: isActive ? '2px solid #2563eb' : '2px solid transparent',
                marginBottom: '-2px',
                cursor: isUnlocked ? 'pointer' : 'not-allowed',
                color: isActive ? '#2563eb' : isUnlocked ? '#374151' : '#9ca3af',
                fontWeight: isActive ? 600 : 400,
                fontSize: '0.875rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.375rem',
              }}
            >
              <span>{icon}</span>
              <span>
                Phase {phase}: {label}
              </span>
              {!isUnlocked && <span style={{ fontSize: '0.75rem' }}>🔒</span>}
            </button>
          );
        })}
      </div>

      {/* Phase content */}
      {activePhase === 1 && study.id && (
        <div>
          {/* Research context summary */}
          {(study.research_questions.length > 0 || study.research_objectives.length > 0) && (
            <div style={{ marginBottom: '2rem', padding: '1rem', background: '#f8fafc', borderRadius: '0.5rem' }}>
              {study.research_objectives.length > 0 && (
                <div style={{ marginBottom: '0.75rem' }}>
                  <h4 style={{ margin: '0 0 0.5rem', fontSize: '0.875rem', color: '#374151' }}>Research Objectives</h4>
                  <ul style={{ margin: 0, paddingLeft: '1.25rem' }}>
                    {study.research_objectives.map((o, i) => (
                      <li key={i} style={{ fontSize: '0.875rem', color: '#4b5563' }}>{o}</li>
                    ))}
                  </ul>
                </div>
              )}
              {study.research_questions.length > 0 && (
                <div>
                  <h4 style={{ margin: '0 0 0.5rem', fontSize: '0.875rem', color: '#374151' }}>Research Questions</h4>
                  <ul style={{ margin: 0, paddingLeft: '1.25rem' }}>
                    {study.research_questions.map((q, i) => (
                      <li key={i} style={{ fontSize: '0.875rem', color: '#4b5563' }}>{q}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
            <PICOForm studyId={study.id} />
            <SeedPapers studyId={study.id} />
          </div>
        </div>
      )}

      {activePhase === 2 && (
        <div style={{ color: '#64748b' }}>
          <p>Phase 2: Search String Builder — coming in the next sprint.</p>
        </div>
      )}

      {activePhase > 2 && (
        <div style={{ color: '#64748b' }}>
          <p>Phase {activePhase} content will be available in a future sprint.</p>
        </div>
      )}
    </div>
  );
}
