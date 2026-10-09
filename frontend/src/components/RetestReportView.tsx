import React from 'react';
import { POST_RETEST_MASTERY, INITIAL_DIAGNOSTIC_MASTERY, CONCEPTS } from '../data/mockData';
import { ArrowUpRight, RotateCcw } from 'lucide-react';

interface RetestReportViewProps {
  onResetDemo: () => void;
}

export const RetestReportView: React.FC<RetestReportViewProps> = ({ onResetDemo }) => {
  const beforeD12 = INITIAL_DIAGNOSTIC_MASTERY['D12'];
  const afterD12 = POST_RETEST_MASTERY['D12'];

  const beforeD13 = INITIAL_DIAGNOSTIC_MASTERY['D13'];
  const afterD13 = POST_RETEST_MASTERY['D13'];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '960px', margin: '0 auto' }}>
      {/* Retest Status Header */}
      <div className="card-clean" style={{ padding: '20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span className="badge badge-mastered">Retest Complete (Family B Items)</span>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>SRS FR-P4 &amp; FR-P5</span>
          </div>
          <h2 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text-main)' }}>Before vs. After Mastery Report</h2>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Retested on alternate family questions (<strong>Q12B</strong> and <strong>Q13B</strong>) following Functional Dependencies remediation.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={onResetDemo}
            className="btn-secondary"
          >
            <RotateCcw size={14} />
            <span>Reset Demo</span>
          </button>
        </div>
      </div>

      {/* Comparison Highlights */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
        {/* D12 Functional Dependencies */}
        <div className="card-clean" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '12px', borderTop: '3px solid var(--success)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '14px', fontWeight: 800, color: 'var(--primary)' }}>D12</span>
              <h3 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-main)' }}>Functional Dependencies</h3>
            </div>
            <span className="badge badge-mastered">Resolved</span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', padding: '12px', borderRadius: '8px', background: '#f8fafc', border: '1px solid var(--border-card)' }}>
            <div>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block' }}>Before:</span>
              <div style={{ fontSize: '22px', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--danger)' }}>
                {(beforeD12.p * 100).toFixed(0)}%
              </div>
              <span className="badge badge-confirmed" style={{ marginTop: '2px' }}>Confirmed Gap</span>
            </div>

            <div>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block' }}>After:</span>
              <div style={{ fontSize: '22px', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--success)', display: 'flex', alignItems: 'center', gap: '2px' }}>
                <span>{(afterD12.p * 100).toFixed(0)}%</span>
                <ArrowUpRight size={18} />
              </div>
              <span className="badge badge-mastered" style={{ marginTop: '2px' }}>Mastered</span>
            </div>
          </div>

          <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            Student passed Q12B (Augmentation Rule). Prerequisite mastery increased by <strong>+70%</strong>.
          </p>
        </div>

        {/* D13 Normalization */}
        <div className="card-clean" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '12px', borderTop: '3px solid var(--success)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '14px', fontWeight: 800, color: 'var(--primary)' }}>D13</span>
              <h3 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-main)' }}>Normalization (1NF-3NF)</h3>
            </div>
            <span className="badge badge-mastered">Mastered</span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', padding: '12px', borderRadius: '8px', background: '#f8fafc', border: '1px solid var(--border-card)' }}>
            <div>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block' }}>Before:</span>
              <div style={{ fontSize: '22px', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--danger)' }}>
                {(beforeD13.p * 100).toFixed(0)}%
              </div>
              <span className="badge badge-suspected" style={{ marginTop: '2px' }}>Suspected Gap</span>
            </div>

            <div>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block' }}>After:</span>
              <div style={{ fontSize: '22px', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--success)', display: 'flex', alignItems: 'center', gap: '2px' }}>
                <span>{(afterD13.p * 100).toFixed(0)}%</span>
                <ArrowUpRight size={18} />
              </div>
              <span className="badge badge-mastered" style={{ marginTop: '2px' }}>Mastered</span>
            </div>
          </div>

          <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            Student successfully analyzed Q13B (2NF Partial Dependency). Target concept achieved mastery.
          </p>
        </div>
      </div>

      {/* Comprehensive 18-Concept Delta Table */}
      <div className="card-clean" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
        <h3 style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text-main)' }}>
          18-Concept Mastery State Comparison
        </h3>

        <div style={{ overflowX: 'auto' }}>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Concept</th>
                <th>Prerequisites</th>
                <th>Pre-Test</th>
                <th>Post-Retest</th>
                <th>Delta</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {CONCEPTS.map(c => {
                const pre = INITIAL_DIAGNOSTIC_MASTERY[c.id];
                const post = POST_RETEST_MASTERY[c.id];
                const delta = post.p - pre.p;
                const isIntervened = c.id === 'D12' || c.id === 'D13';

                return (
                  <tr key={c.id} style={{ background: isIntervened ? 'var(--primary-subtle)' : 'transparent' }}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--primary)' }}>{c.id}</td>
                    <td style={{ fontWeight: 600, color: 'var(--text-main)' }}>{c.name}</td>
                    <td style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontSize: '12px' }}>
                      {c.prerequisites.length > 0 ? c.prerequisites.join(', ') : 'None'}
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>{(pre.p * 100).toFixed(0)}%</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--text-main)' }}>{(post.p * 100).toFixed(0)}%</td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>
                      {delta > 0 ? (
                        <span style={{ color: 'var(--success)', fontWeight: 700 }}>+{ (delta * 100).toFixed(0) }%</span>
                      ) : (
                        <span style={{ color: 'var(--text-dim)' }}>0%</span>
                      )}
                    </td>
                    <td>
                      <span className={`badge ${post.status === 'mastered' ? 'badge-mastered' : post.status === 'confirmed' ? 'badge-confirmed' : post.status === 'suspected' ? 'badge-suspected' : 'badge-insufficient'}`}>
                        {post.status}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
