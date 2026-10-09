import React, { useState } from 'react';
import type { ResponseRecord, StudentMastery } from '../data/mockData';
import { CONCEPTS } from '../data/mockData';
import { ShieldCheck, CheckCircle2, XCircle } from 'lucide-react';

interface EvidencePanelProps {
  masteryMap: Record<string, StudentMastery>;
  responses: ResponseRecord[];
  rootGapId: string;
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({
  masteryMap,
  responses,
  rootGapId = 'D12'
}) => {
  const [llmFallbackSimulated, setLlmFallbackSimulated] = useState(false);

  const rootConcept = CONCEPTS.find(c => c.id === rootGapId) || CONCEPTS[11];
  const rootMastery = masteryMap[rootGapId];

  const weakConcepts = Object.values(masteryMap)
    .filter(m => m.status === 'confirmed' || m.status === 'suspected')
    .sort((a, b) => (b.blocker_score || 0) - (a.blocker_score || 0));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '960px', margin: '0 auto' }}>
      {/* Root Gap Diagnosis Card */}
      <div className="card-clean" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px', borderLeft: '4px solid var(--danger)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px', borderBottom: '1px solid #f1f5f9', paddingBottom: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className="badge badge-confirmed">Confirmed Root Gap</span>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              Formula: (1 − p) × importance
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <button
              onClick={() => setLlmFallbackSimulated(!llmFallbackSimulated)}
              className="btn-secondary"
              style={{ fontSize: '11px', padding: '4px 10px' }}
            >
              <span>{llmFallbackSimulated ? 'Fallback Active (Deterministic)' : 'LLM Assistant Active'}</span>
            </button>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', alignItems: 'center' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
              <span style={{ fontSize: '24px', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--danger)' }}>{rootConcept.id}</span>
              <h2 style={{ fontSize: '22px', fontWeight: 700, color: 'var(--text-main)' }}>{rootConcept.name}</h2>
            </div>
            <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: 1.55 }}>
              Target concept <strong>D13 (Normalization)</strong> failed because the learner cannot compute attribute closures. Rather than assigning redundant Normalization practice, the engine isolates <strong>{rootConcept.name}</strong> as the foundational root blocker.
            </p>

            <div style={{ padding: '12px', borderRadius: '8px', background: '#f8fafc', border: '1px solid var(--border-card)', fontSize: '12px', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '4px', fontFamily: 'var(--font-mono)' }}>
              <div>• Blocker Score: (1 − {rootMastery?.p.toFixed(2)}) × 0.83 = <strong style={{ color: 'var(--danger)' }}>{rootMastery?.blocker_score?.toFixed(2)}</strong></div>
              <div>• Status Rule: p &lt; 0.30 and 2 direct evidence events (Q12A, Q12B).</div>
            </div>
          </div>

          <div style={{ background: '#f8fafc', border: '1px solid var(--border-card)', borderRadius: '10px', padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Mastery Estimate (p):</span>
              <span style={{ fontSize: '22px', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--danger)' }}>
                {((rootMastery?.p || 0.18) * 100).toFixed(0)}%
              </span>
            </div>
            <div style={{ width: '100%', height: '6px', borderRadius: '9999px', background: '#e2e8f0', overflow: 'hidden' }}>
              <div style={{ height: '100%', borderRadius: '9999px', background: 'var(--danger)', width: `${(rootMastery?.p || 0.18) * 100}%` }} />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', borderTop: '1px solid #e2e8f0', paddingTop: '8px', fontSize: '11.5px' }}>
              <div>
                <span style={{ color: 'var(--text-muted)', display: 'block' }}>Direct Evidence:</span>
                <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{rootMastery?.n_direct || 2} answers</span>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)', display: 'block' }}>Propagated:</span>
                <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{rootMastery?.n_indirect || 1} event</span>
              </div>
            </div>
          </div>
        </div>

        {/* Explainer */}
        <div style={{ padding: '12px 16px', borderRadius: '8px', background: 'var(--primary-subtle)', border: '1px solid #c7d2fe', fontSize: '12.5px', color: 'var(--primary-text)', display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
          <ShieldCheck size={18} style={{ color: 'var(--primary)', flexShrink: 0, marginTop: '2px' }} />
          <div>
            <div style={{ fontWeight: 600, marginBottom: '2px' }}>
              {llmFallbackSimulated ? 'Deterministic Rule Engine Explainer' : 'AI Explainer (Validated Assistant Output)'}
            </div>
            <p style={{ lineHeight: 1.5, color: 'var(--text-secondary)' }}>
              Learner correctly solved SQL and relational algebra, but failed Normalization Q13A choosing distractor &apos;1NF only&apos; (misconception: cannot compute transitive FDs). Targeted questions Q12A and Q12B confirmed Armstrong axiom difficulty. Functional dependencies must be remediated first.
            </p>
          </div>
        </div>
      </div>

      {/* Candidate Root Gaps Comparison Table */}
      <div className="card-clean" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
        <h3 style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text-main)' }}>
          Candidate Blocker Ranking
        </h3>

        <div style={{ overflowX: 'auto' }}>
          <table>
            <thead>
              <tr>
                <th>Concept</th>
                <th>Role</th>
                <th>Mastery (p)</th>
                <th>Direct Ev.</th>
                <th>Blocker Score</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {weakConcepts.map(c => {
                const conceptDef = CONCEPTS.find(x => x.id === c.concept_id);
                const isWinner = c.concept_id === rootGapId;
                return (
                  <tr key={c.concept_id} style={{ background: isWinner ? 'var(--danger-subtle)' : 'transparent' }}>
                    <td style={{ fontWeight: 600, color: 'var(--text-main)' }}>
                      <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--primary)', marginRight: '6px' }}>{c.concept_id}</span>
                      <span>{conceptDef?.name}</span>
                    </td>
                    <td>{conceptDef?.prerequisites.length === 0 ? 'Foundation' : 'Prerequisite'}</td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>{(c.p * 100).toFixed(0)}%</td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>{c.n_direct}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--warning-text)' }}>{c.blocker_score?.toFixed(2) || '—'}</td>
                    <td>
                      <span className={`badge ${c.status === 'confirmed' ? 'badge-confirmed' : 'badge-suspected'}`}>
                        {c.status}
                      </span>
                    </td>
                    <td style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                      {isWinner ? 'Priority 1 in Path' : 'Deferred review'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Audit Trail: Response Chain with Distractor Misconceptions */}
      <div className="card-clean" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
        <h3 style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text-main)' }}>
          Session Audit Trail (Responses &amp; Misconceptions)
        </h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {responses.map((resp, i) => (
            <div key={resp.id || i} style={{ padding: '12px 14px', borderRadius: '8px', background: '#f8fafc', border: '1px solid var(--border-card)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px', fontSize: '12.5px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                {resp.correct ? (
                  <CheckCircle2 size={16} style={{ color: 'var(--success)', flexShrink: 0 }} />
                ) : (
                  <XCircle size={16} style={{ color: 'var(--danger)', flexShrink: 0 }} />
                )}
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--text-main)' }}>{resp.question_id}</span>
                    <span style={{ color: 'var(--text-muted)' }}>Concept: {resp.concept_id}</span>
                    <span style={{ color: 'var(--text-muted)' }}>Option: {resp.option_id.toUpperCase()}</span>
                    <span className="badge badge-insufficient">{resp.confidence} conf</span>
                  </div>
                  {resp.misconception && (
                    <div style={{ fontSize: '11.5px', color: 'var(--danger-text)', marginTop: '2px' }}>
                      Distractor Misconception: {resp.misconception}
                    </div>
                  )}
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontSize: '11.5px' }}>
                <span>{(resp.response_ms / 1000).toFixed(1)}s</span>
                <span>Weight: {resp.evidence_weight}</span>
                <span>{resp.timestamp}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
