import React, { useState } from 'react';
import type { LearningPathItem } from '../data/mockData';
import { MOCK_LEARNING_PATH, CONCEPTS } from '../data/mockData';
import { CheckCircle, ArrowRight, ExternalLink } from 'lucide-react';

interface LearningPathViewProps {
  onUnlockRetest: () => void;
}

export const LearningPathView: React.FC<LearningPathViewProps> = ({ onUnlockRetest }) => {
  const [items, setItems] = useState<LearningPathItem[]>(MOCK_LEARNING_PATH);
  const [activeItemId, setActiveItemId] = useState<string>(items[0]?.id || '');
  const [showSolution, setShowSolution] = useState(false);

  const activeItem = items.find(i => i.id === activeItemId) || items[0];
  const activeConcept = CONCEPTS.find(c => c.id === activeItem.concept_id);

  const handleToggleComplete = (itemId: string) => {
    const updated = items.map(item => {
      if (item.id === itemId) return { ...item, completed: !item.completed };
      return item;
    });
    setItems(updated);

    if (updated.every(i => i.completed)) {
      onUnlockRetest();
    }
  };

  const allCompleted = items.every(i => i.completed);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '960px', margin: '0 auto' }}>
      {/* Header */}
      <div className="card-clean" style={{ padding: '20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span className="badge badge-mastered">Topological Learning Path</span>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Skips Mastered Concepts (&gt;70%)</span>
          </div>
          <h2 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text-main)' }}>Targeted Remediation Plan</h2>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Remediate Root Gap (<strong>D12 Functional Dependencies</strong>) first, then proceed to <strong>D13 Normalization</strong>.
          </p>
        </div>

        <button
          onClick={onUnlockRetest}
          className="btn-primary"
        >
          <span>Retest &amp; Evaluation</span>
          <ArrowRight size={14} />
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
        {/* Step Navigation Sidebar */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <div style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.04em' }}>
            Remediation Steps ({items.filter(i => i.completed).length}/{items.length} Done)
          </div>

          {items.map(item => {
            const isCurrent = item.id === activeItemId;
            return (
              <div
                key={item.id}
                onClick={() => { setActiveItemId(item.id); setShowSolution(false); }}
                style={{
                  padding: '14px',
                  borderRadius: '10px',
                  border: isCurrent ? '1px solid var(--primary)' : '1px solid var(--border-card)',
                  background: isCurrent ? 'var(--primary-subtle)' : '#ffffff',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '12px',
                  transition: 'all 0.1s ease'
                }}
              >
                <div
                  onClick={(e) => { e.stopPropagation(); handleToggleComplete(item.id); }}
                  style={{
                    width: '22px',
                    height: '22px',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginTop: '2px',
                    border: '1px solid',
                    cursor: 'pointer',
                    background: item.completed ? 'var(--success)' : 'transparent',
                    borderColor: item.completed ? 'var(--success)' : 'var(--border-card)',
                    color: item.completed ? '#ffffff' : 'var(--text-muted)'
                  }}
                >
                  {item.completed ? <CheckCircle size={14} /> : <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)' }}>{item.position}</span>}
                </div>

                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', fontWeight: 700, color: 'var(--primary)' }}>{item.concept_id}</span>
                    <span style={{ fontSize: '11px', color: 'var(--text-dim)' }}>{item.estimated_mins} mins</span>
                  </div>
                  <h4 style={{ fontSize: '13.5px', fontWeight: 600, color: 'var(--text-main)', marginTop: '2px' }}>{item.concept_name}</h4>
                  <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px', lineHeight: 1.4 }}>{item.rationale}</p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Study Content Module */}
        <div className="card-clean" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '18px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', paddingBottom: '14px', flexWrap: 'wrap', gap: '10px' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '13px', fontWeight: 800, color: 'var(--primary)' }}>{activeItem.concept_id}</span>
                <h3 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-main)' }}>{activeItem.concept_name}</h3>
              </div>
              <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>{activeItem.rationale}</p>
            </div>

            <button
              onClick={() => handleToggleComplete(activeItem.id)}
              className="btn-secondary"
              style={{ fontSize: '12px', color: activeItem.completed ? 'var(--success-text)' : 'var(--text-main)' }}
            >
              <CheckCircle size={13} />
              <span>{activeItem.completed ? 'Completed' : 'Mark Done'}</span>
            </button>
          </div>

          {/* Key Takeaways */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <h4 style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.04em' }}>
              Foundational Rules:
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {activeItem.key_takeaways.map((point, idx) => (
                <div key={idx} style={{ padding: '10px 12px', borderRadius: '6px', background: '#f8fafc', border: '1px solid var(--border-card)', fontSize: '12.5px', color: 'var(--text-secondary)', display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                  <span style={{ color: 'var(--primary)', fontWeight: 700 }}>•</span>
                  <span style={{ lineHeight: 1.45 }}>{point}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Micro-Practice */}
          <div style={{ padding: '14px', borderRadius: '8px', background: '#f8fafc', border: '1px solid var(--border-card)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '11.5px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--text-main)' }}>
                Micro-Practice Exercise
              </span>
              <button
                onClick={() => setShowSolution(!showSolution)}
                style={{ fontSize: '11.5px', color: 'var(--primary)', fontWeight: 600, cursor: 'pointer' }}
              >
                {showSolution ? 'Hide Solution' : 'Reveal Solution'}
              </button>
            </div>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)', background: '#ffffff', padding: '10px', borderRadius: '6px', border: '1px solid var(--border-card)' }}>
              {activeItem.practice_prompt}
            </p>
            {showSolution && (
              <div style={{ padding: '10px', borderRadius: '6px', background: 'var(--success-subtle)', border: '1px solid var(--success-border)', fontSize: '12px', color: 'var(--success-text)', lineHeight: 1.45 }}>
                <strong>Solution:</strong> {activeItem.practice_solution}
              </div>
            )}
          </div>

          {/* Reference Material */}
          {activeConcept?.resources && activeConcept.resources.length > 0 && (
            <div style={{ borderTop: '1px solid #f1f5f9', paddingTop: '10px' }}>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '6px' }}>Reference:</div>
              {activeConcept.resources.map((res, i) => (
                <a
                  key={i}
                  href={res.url}
                  target="_blank"
                  rel="noreferrer"
                  style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px', borderRadius: '6px', background: '#f8fafc', border: '1px solid var(--border-card)', fontSize: '12px', color: 'var(--primary-text)', textDecoration: 'none' }}
                >
                  <span style={{ fontWeight: 600 }}>{res.title}</span>
                  <ExternalLink size={13} />
                </a>
              ))}
            </div>
          )}

          <div style={{ display: 'flex', justifyContent: 'flex-end', paddingTop: '6px' }}>
            <button
              onClick={onUnlockRetest}
              className="btn-primary"
            >
              <span>{allCompleted ? 'Begin Retest Assessment' : 'Proceed to Retest'}</span>
              <ArrowRight size={14} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
