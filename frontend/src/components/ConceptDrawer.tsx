import React from 'react';
import type { Concept, StudentMastery } from '../data/mockData';
import { QUESTIONS } from '../data/mockData';
import { X, Target } from 'lucide-react';

interface ConceptDrawerProps {
  concept: Concept | null;
  mastery?: StudentMastery;
  onClose: () => void;
  onTestConcept: (conceptId: string) => void;
}

export const ConceptDrawer: React.FC<ConceptDrawerProps> = ({
  concept,
  mastery,
  onClose,
  onTestConcept
}) => {
  if (!concept) return null;
  const conceptQuestions = QUESTIONS.filter(q => q.concept === concept.id);
  const status = mastery?.status || 'insufficient';

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      bottom: 0,
      right: 0,
      width: '100%',
      maxWidth: '420px',
      background: '#ffffff',
      borderLeft: '1px solid var(--border-card)',
      zIndex: 60,
      boxShadow: 'var(--shadow-lg)',
      padding: '24px',
      overflowY: 'auto',
      display: 'flex',
      flexDirection: 'column',
      gap: '20px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', paddingBottom: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '13px', fontWeight: 700, padding: '2px 8px', borderRadius: '4px', background: 'var(--primary-subtle)', color: 'var(--primary-text)' }}>
            {concept.id}
          </span>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Difficulty {concept.difficulty}/5</span>
        </div>
        <button
          onClick={onClose}
          style={{ padding: '4px', borderRadius: '4px', color: 'var(--text-muted)' }}
        >
          <X size={16} />
        </button>
      </div>

      <div>
        <h3 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-main)', marginBottom: '6px' }}>{concept.name}</h3>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>{concept.description}</p>
      </div>

      {/* Mastery Stat */}
      <div className="card-clean" style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Estimated Mastery:</span>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '16px', fontWeight: 700, color: 'var(--text-main)' }}>
            {mastery?.p !== undefined ? `${(mastery.p * 100).toFixed(0)}%` : '50%'}
          </span>
        </div>

        <div style={{ width: '100%', height: '6px', borderRadius: '9999px', background: '#f1f5f9', overflow: 'hidden' }}>
          <div
            style={{
              height: '100%',
              borderRadius: '9999px',
              width: `${(mastery?.p || 0.5) * 100}%`,
              background: status === 'mastered' ? 'var(--success)' : status === 'confirmed' ? 'var(--danger)' : status === 'suspected' ? 'var(--danger)' : 'var(--warning)'
            }}
          />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '12px', borderTop: '1px solid #f1f5f9', paddingTop: '8px' }}>
          <div>
            <span style={{ color: 'var(--text-muted)', display: 'block' }}>Direct Evidence:</span>
            <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{mastery?.n_direct || 0} answers</span>
          </div>
          <div>
            <span style={{ color: 'var(--text-muted)', display: 'block' }}>Propagated:</span>
            <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{mastery?.n_indirect || 0} events</span>
          </div>
        </div>
      </div>

      {/* Prerequisites */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
        <h4 style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
          Prerequisites:
        </h4>
        {concept.prerequisites.length === 0 ? (
          <div style={{ fontSize: '12px', color: 'var(--success-text)', background: 'var(--success-subtle)', padding: '6px 10px', borderRadius: '4px' }}>
            Root Foundation Concept
          </div>
        ) : (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
            {concept.prerequisites.map(p => (
              <span key={p} className="badge badge-insufficient">
                {p}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Objectives */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
        <h4 style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
          Learning Objectives:
        </h4>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {concept.learning_objectives.map((obj, i) => (
            <div key={i} style={{ fontSize: '12.5px', color: 'var(--text-secondary)', display: 'flex', alignItems: 'flex-start', gap: '6px' }}>
              <span style={{ color: 'var(--primary)', fontWeight: 700 }}>•</span>
              <span>{obj}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Action */}
      <div style={{ paddingTop: '8px', borderTop: '1px solid #f1f5f9' }}>
        <button
          onClick={() => { onTestConcept(concept.id); onClose(); }}
          className="btn-primary"
          style={{ width: '100%' }}
        >
          <Target size={14} />
          <span>Test Question for {concept.id} ({conceptQuestions.length} available)</span>
        </button>
      </div>
    </div>
  );
};
