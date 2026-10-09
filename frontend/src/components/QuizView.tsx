import React, { useState, useEffect } from 'react';
import type { Question, ResponseRecord, StudentMastery } from '../data/mockData';
import { QUESTIONS } from '../data/mockData';
import { Clock, ArrowRight, Target, BookOpen } from 'lucide-react';

interface QuizViewProps {
  onResponseSubmitted: (record: ResponseRecord) => void;
  currentMastery: Record<string, StudentMastery>;
  responses: ResponseRecord[];
}

export const QuizView: React.FC<QuizViewProps> = ({
  onResponseSubmitted,
  responses
}) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedOptionId, setSelectedOptionId] = useState<string | null>(null);
  const [confidence, setConfidence] = useState<'low' | 'medium' | 'high'>('medium');
  const [timerSeconds, setTimerSeconds] = useState(0);
  const [isSubmitted, setIsSubmitted] = useState(false);

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (!isSubmitted) {
      interval = setInterval(() => {
        setTimerSeconds(s => s + 0.1);
      }, 100);
    }
    return () => clearInterval(interval);
  }, [isSubmitted, currentQuestionIndex]);

  const activeQuestion: Question = QUESTIONS[currentQuestionIndex] || QUESTIONS[0];

  const getSessionPhase = () => {
    const count = responses.length;
    if (count < 4) return { name: "Phase 1: Baseline Probes", badge: "badge-mastered" };
    if (count < 10) return { name: "Phase 2: Targeted Diagnosis", badge: "badge-uncertain" };
    return { name: "Phase 3: Verification", badge: "badge-confirmed" };
  };

  const phase = getSessionPhase();

  const handleSelectOption = (optId: string) => {
    if (!isSubmitted) setSelectedOptionId(optId);
  };

  const handleSubmitAnswer = () => {
    if (!selectedOptionId) return;

    const chosenOption = activeQuestion.options.find(o => o.id === selectedOptionId);
    if (!chosenOption) return;

    const responseMs = Math.round(timerSeconds * 1000);
    let weight = 1.0;
    if (chosenOption.correct && confidence === 'low') weight = 0.6;
    if (!chosenOption.correct && confidence === 'high') weight = 1.2;
    if (responseMs < 3000) weight *= 0.7;

    const record: ResponseRecord = {
      id: `R-${Date.now().toString().slice(-4)}`,
      question_id: activeQuestion.id,
      concept_id: activeQuestion.concept,
      option_id: chosenOption.id,
      correct: chosenOption.correct,
      confidence,
      response_ms: responseMs,
      evidence_weight: Number(weight.toFixed(2)),
      distractor_mapped_to: chosenOption.maps_to,
      misconception: chosenOption.misconception,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    };

    setIsSubmitted(true);
    onResponseSubmitted(record);
  };

  const handleNextQuestion = () => {
    setIsSubmitted(false);
    setSelectedOptionId(null);
    setConfidence('medium');
    setTimerSeconds(0);
    setCurrentQuestionIndex(idx => (idx + 1) % QUESTIONS.length);
  };

  const loadQuestionDirectly = (qId: string) => {
    const idx = QUESTIONS.findIndex(q => q.id === qId);
    if (idx !== -1) {
      setIsSubmitted(false);
      setSelectedOptionId(null);
      setConfidence('medium');
      setTimerSeconds(0);
      setCurrentQuestionIndex(idx);
    }
  };

  const selectedOpt = activeQuestion.options.find(o => o.id === selectedOptionId);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', maxWidth: '880px', margin: '0 auto' }}>
      {/* Session Header */}
      <div className="card-clean" style={{ padding: '14px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontWeight: 700, fontSize: '14px', color: 'var(--text-main)' }}>
            Question {responses.length + 1} of 12
          </span>
          <span className={`badge ${phase.badge}`}>{phase.name}</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
            <Clock size={14} />
            <span>{timerSeconds.toFixed(1)}s</span>
            {timerSeconds < 3 && (
              <span style={{ color: 'var(--warning)', fontFamily: 'var(--font-body)', fontSize: '11px' }}>(&lt;3s dampener)</span>
            )}
          </div>
          <span className="badge badge-mastered" style={{ fontSize: '11px' }}>
            Consent Active
          </span>
        </div>
      </div>

      {/* Benchmark Shortcuts */}
      <div className="card-clean" style={{ padding: '12px 16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
          Benchmark Probes (SRS Scenario):
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
          <button
            onClick={() => loadQuestionDirectly('Q08A')}
            className={activeQuestion.id === 'Q08A' ? 'btn-primary' : 'btn-secondary'}
            style={{ fontSize: '12px', padding: '4px 10px' }}
          >
            1. SQL Basics (D08)
          </button>
          <button
            onClick={() => loadQuestionDirectly('Q07A')}
            className={activeQuestion.id === 'Q07A' ? 'btn-primary' : 'btn-secondary'}
            style={{ fontSize: '12px', padding: '4px 10px' }}
          >
            2. Relational Algebra (D07)
          </button>
          <button
            onClick={() => loadQuestionDirectly('Q13A')}
            className={activeQuestion.id === 'Q13A' ? 'btn-primary' : 'btn-secondary'}
            style={{ fontSize: '12px', padding: '4px 10px', color: activeQuestion.id === 'Q13A' ? '#ffffff' : 'var(--danger)' }}
          >
            3. Normalization (D13 Trigger)
          </button>
          <button
            onClick={() => loadQuestionDirectly('Q12A')}
            className={activeQuestion.id === 'Q12A' ? 'btn-primary' : 'btn-secondary'}
            style={{ fontSize: '12px', padding: '4px 10px', color: activeQuestion.id === 'Q12A' ? '#ffffff' : 'var(--danger)' }}
          >
            4. Functional Dep. (D12 Probe)
          </button>
          <button
            onClick={() => loadQuestionDirectly('Q12B')}
            className={activeQuestion.id === 'Q12B' ? 'btn-primary' : 'btn-secondary'}
            style={{ fontSize: '12px', padding: '4px 10px', color: activeQuestion.id === 'Q12B' ? '#ffffff' : 'var(--danger)' }}
          >
            5. Armstrong Axiom (D12 Confirmed)
          </button>
        </div>
      </div>

      {/* Main Question Card */}
      <div className="card-clean" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '18px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', paddingBottom: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ padding: '2px 8px', borderRadius: '4px', background: 'var(--primary-subtle)', color: 'var(--primary-text)', fontFamily: 'var(--font-mono)', fontSize: '12px', fontWeight: 700 }}>
              {activeQuestion.id}
            </span>
            <span style={{ fontSize: '12.5px', color: 'var(--text-muted)' }}>
              Concept: <strong style={{ color: 'var(--text-main)' }}>{activeQuestion.concept}</strong> (Family {activeQuestion.family})
            </span>
          </div>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            Difficulty {activeQuestion.difficulty}/5
          </span>
        </div>

        {/* Prompt */}
        <h3 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text-main)', lineHeight: 1.5 }}>
          {activeQuestion.prompt}
        </h3>

        {/* Options */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {activeQuestion.options.map(option => {
            const isSelected = selectedOptionId === option.id;
            let bg = '#ffffff';
            let borderColor = 'var(--border-card)';
            let textColor = 'var(--text-main)';

            if (isSubmitted) {
              if (option.correct) {
                bg = 'var(--success-subtle)';
                borderColor = 'var(--success-border)';
                textColor = 'var(--success-text)';
              } else if (isSelected && !option.correct) {
                bg = 'var(--danger-subtle)';
                borderColor = 'var(--danger-border)';
                textColor = 'var(--danger-text)';
              } else {
                textColor = 'var(--text-dim)';
                borderColor = '#f1f5f9';
              }
            } else if (isSelected) {
              bg = 'var(--primary-subtle)';
              borderColor = 'var(--primary)';
            }

            return (
              <div
                key={option.id}
                onClick={() => handleSelectOption(option.id)}
                style={{
                  padding: '12px 16px',
                  borderRadius: '8px',
                  border: `1px solid ${borderColor}`,
                  background: bg,
                  color: textColor,
                  cursor: isSubmitted ? 'default' : 'pointer',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '12px',
                  transition: 'all 0.1s ease'
                }}
              >
                <div style={{
                  width: '22px',
                  height: '22px',
                  borderRadius: '4px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '11px',
                  fontWeight: 700,
                  fontFamily: 'var(--font-mono)',
                  flexShrink: 0,
                  marginTop: '1px',
                  background: isSelected ? 'var(--primary)' : '#f1f5f9',
                  color: isSelected ? '#ffffff' : 'var(--text-secondary)'
                }}>
                  {option.id.toUpperCase()}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '13.5px', fontWeight: 500, lineHeight: 1.45 }}>{option.text}</div>

                  {isSubmitted && !option.correct && option.maps_to && (
                    <div style={{ marginTop: '6px', fontSize: '11.5px', color: 'var(--danger-text)', background: 'var(--danger-subtle)', padding: '6px 10px', borderRadius: '4px' }}>
                      Diagnostic Distractor: Maps to <strong>{option.maps_to}</strong> — {option.misconception}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Confidence Tap */}
        {!isSubmitted && (
          <div style={{ borderTop: '1px solid #f1f5f9', paddingTop: '14px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.04em' }}>
              Confidence Rating:
            </label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
              <button
                type="button"
                onClick={() => setConfidence('low')}
                style={{
                  padding: '10px',
                  borderRadius: '6px',
                  textAlign: 'center',
                  border: confidence === 'low' ? '1px solid var(--warning)' : '1px solid var(--border-card)',
                  background: confidence === 'low' ? 'var(--warning-subtle)' : '#ffffff',
                  color: confidence === 'low' ? 'var(--warning-text)' : 'var(--text-secondary)',
                  cursor: 'pointer'
                }}
              >
                <div style={{ fontSize: '12.5px', fontWeight: 600 }}>Low (0.6x)</div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Guess / Unsure</div>
              </button>

              <button
                type="button"
                onClick={() => setConfidence('medium')}
                style={{
                  padding: '10px',
                  borderRadius: '6px',
                  textAlign: 'center',
                  border: confidence === 'medium' ? '1px solid var(--primary)' : '1px solid var(--border-card)',
                  background: confidence === 'medium' ? 'var(--primary-subtle)' : '#ffffff',
                  color: confidence === 'medium' ? 'var(--primary-text)' : 'var(--text-secondary)',
                  cursor: 'pointer'
                }}
              >
                <div style={{ fontSize: '12.5px', fontWeight: 600 }}>Medium (1.0x)</div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Fairly confident</div>
              </button>

              <button
                type="button"
                onClick={() => setConfidence('high')}
                style={{
                  padding: '10px',
                  borderRadius: '6px',
                  textAlign: 'center',
                  border: confidence === 'high' ? '1px solid var(--success)' : '1px solid var(--border-card)',
                  background: confidence === 'high' ? 'var(--success-subtle)' : '#ffffff',
                  color: confidence === 'high' ? 'var(--success-text)' : 'var(--text-secondary)',
                  cursor: 'pointer'
                }}
              >
                <div style={{ fontSize: '12.5px', fontWeight: 600 }}>High (1.2x)</div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Certain</div>
              </button>
            </div>
          </div>
        )}

        {/* Post-submission Explanation */}
        {isSubmitted && (
          <div style={{ padding: '14px 16px', borderRadius: '8px', background: '#f8fafc', border: '1px solid var(--border-card)', display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', fontWeight: 600, color: 'var(--primary)' }}>
              <BookOpen size={15} />
              <span>Explanation</span>
            </div>
            <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              {activeQuestion.explanation}
            </p>
            {selectedOpt && (
              <div style={{ fontSize: '11.5px', color: 'var(--text-muted)', borderTop: '1px solid #e2e8f0', paddingTop: '6px' }}>
                Recorded in {timerSeconds.toFixed(1)}s ({confidence} confidence). Bayesian engine updated concept {activeQuestion.concept}.
              </div>
            )}
          </div>
        )}

        {/* Action Button */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', paddingTop: '4px' }}>
          {!isSubmitted ? (
            <button
              onClick={handleSubmitAnswer}
              disabled={!selectedOptionId}
              className="btn-primary"
            >
              <span>Submit Answer</span>
              <Target size={14} />
            </button>
          ) : (
            <button
              onClick={handleNextQuestion}
              className="btn-primary"
            >
              <span>Next Question</span>
              <ArrowRight size={14} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
