import React from 'react';
import { ShieldCheck, ArrowRight } from 'lucide-react';

interface ConsentIntroViewProps {
  onStartQuiz: () => void;
  consentGiven: boolean;
  setConsentGiven: (val: boolean) => void;
}

export const ConsentIntroView: React.FC<ConsentIntroViewProps> = ({
  onStartQuiz,
  consentGiven,
  setConsentGiven
}) => {
  return (
    <div style={{ maxWidth: '880px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '24px', padding: '12px 0' }}>
      {/* Clean Minimal Hero */}
      <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>
        <span className="badge badge-insufficient" style={{ fontSize: '11px' }}>
          AI-VERSE Problem 30 • DBMS Dependency Graph
        </span>

        <h1 style={{ fontSize: '32px', fontWeight: 700, color: 'var(--text-main)', letterSpacing: '-0.02em', maxWidth: '720px' }}>
          Trace Learning Gaps to Foundational Prerequisites
        </h1>

        <p style={{ fontSize: '14.5px', color: 'var(--text-secondary)', maxWidth: '640px', lineHeight: 1.6 }}>
          When a student fails a concept like <em>Normalization</em>, traditional platforms prescribe more normalization drills. MindMesh uses a 18-concept prerequisite graph to diagnose whether the root blocker is actually an earlier prerequisite like <em>Functional Dependencies</em>.
        </p>
      </div>

      {/* 3 Minimal Pillars */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px' }}>
        <div className="card-clean" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <h3 style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text-main)' }}>1. Prerequisite Graph</h3>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: 1.5 }}>
            18 core DBMS concepts with validated directed prerequisite edges (<code style={{ color: 'var(--primary)' }}>A → B</code>). A must be mastered before B.
          </p>
        </div>

        <div className="card-clean" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <h3 style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text-main)' }}>2. Deterministic Bayesian</h3>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: 1.5 }}>
            Mastery estimates update based on correctness, confidence weighting, and distractor misconception mappings. No LLM controls mastery.
          </p>
        </div>

        <div className="card-clean" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <h3 style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text-main)' }}>3. Root Gap Remediation</h3>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: 1.5 }}>
            Calculates the highest blocker score, reorders the study path topologically, retests with alternate family questions, and outputs before/after reports.
          </p>
        </div>
      </div>

      {/* Seed Demo Profile Card */}
      <div className="card-clean" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '10px', borderLeft: '3px solid var(--primary)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', paddingBottom: '8px' }}>
          <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-main)' }}>
            Benchmark Persona: Alex Chen (STU-9402)
          </span>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
            Seed Diagnosis Scenario
          </span>
        </div>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.55 }}>
          Alex scores 90% on SQL Basics and Relational Algebra, but fails Normalization (D13). Rather than assigning redundant Normalization drills, MindMesh identifies that Alex lacks Functional Dependencies (D12), confirms it in 2 targeted questions, and retests.
        </p>
      </div>

      {/* Privacy Consent Box */}
      <div className="card-clean" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px', background: '#ffffff' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
          <ShieldCheck size={20} style={{ color: 'var(--primary)', flexShrink: 0, marginTop: '2px' }} />
          <div>
            <h4 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-main)', marginBottom: '2px' }}>
              Data Ethics &amp; Consent
            </h4>
            <p style={{ fontSize: '12.5px', color: 'var(--text-muted)', lineHeight: 1.5 }}>
              All interactions are logged under pseudonymous IDs. No personal identifying information (PII) is transmitted. Diagnostic decisions are fully deterministic and reproducible.
            </p>
          </div>
        </div>

        <label style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '10px 14px', borderRadius: '8px', background: '#f8fafc', border: '1px solid var(--border-card)', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={consentGiven}
            onChange={(e) => setConsentGiven(e.target.checked)}
            style={{ width: '15px', height: '15px', accentColor: 'var(--primary)', cursor: 'pointer' }}
          />
          <span style={{ fontSize: '13px', color: 'var(--text-main)', fontWeight: 500 }}>
            I consent to participate in this adaptive diagnostic session.
          </span>
        </label>

        <div style={{ display: 'flex', justifyContent: 'flex-end', paddingTop: '2px' }}>
          <button
            onClick={onStartQuiz}
            disabled={!consentGiven}
            className="btn-primary"
          >
            <span>Start Diagnostic Assessment</span>
            <ArrowRight size={15} />
          </button>
        </div>
      </div>
    </div>
  );
};
