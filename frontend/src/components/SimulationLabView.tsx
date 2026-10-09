import React, { useState } from 'react';
import { SIMULATION_BENCHMARK } from '../data/mockData';
import { Play } from 'lucide-react';

export const SimulationLabView: React.FC = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [simStep, setSimStep] = useState(3);

  const runSimulation = () => {
    setIsRunning(true);
    setSimStep(0);
    const interval = setInterval(() => {
      setSimStep(prev => {
        if (prev >= 3) {
          clearInterval(interval);
          setIsRunning(false);
          return 3;
        }
        return prev + 1;
      });
    }, 400);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '960px', margin: '0 auto' }}>
      {/* Header */}
      <div className="card-clean" style={{ padding: '20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span className="badge badge-mastered">Algorithm Benchmark</span>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>SRS Section 11.3 Simulation</span>
          </div>
          <h2 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text-main)' }}>Prerequisite DAG vs. Baselines</h2>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Simulated evaluation across 100 seeded learner agents with hidden prerequisite gaps.
          </p>
        </div>

        <button
          onClick={runSimulation}
          disabled={isRunning}
          className="btn-primary"
        >
          <Play size={14} />
          <span>{isRunning ? 'Running Trial...' : 'Run Simulation'}</span>
        </button>
      </div>

      {/* Benchmark Metric Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
        {SIMULATION_BENCHMARK.map((bench, idx) => {
          const isMindMesh = idx === 2;

          return (
            <div
              key={bench.strategy}
              className={isMindMesh ? 'card-featured' : 'card-clean'}
              style={{
                padding: '20px',
                display: 'flex',
                flexDirection: 'column',
                gap: '14px',
                background: isMindMesh ? 'var(--primary-subtle)' : '#ffffff'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                  {bench.strategy.split(':')[0]}
                </span>
                {isMindMesh && (
                  <span className="badge badge-mastered">
                    Proposed
                  </span>
                )}
              </div>

              <h4 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-main)' }}>
                {bench.strategy.split(':')[1]}
              </h4>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Questions to Diagnose:</span>
                    <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--text-main)' }}>
                      {simStep >= idx ? bench.avg_questions_to_diagnose : '...'} Qs
                    </span>
                  </div>
                  <div style={{ width: '100%', height: '6px', borderRadius: '3px', background: '#e2e8f0', overflow: 'hidden' }}>
                    <div
                      style={{
                        height: '100%',
                        borderRadius: '3px',
                        width: `${((14 - bench.avg_questions_to_diagnose) / 14) * 100}%`,
                        backgroundColor: isMindMesh ? 'var(--primary)' : '#94a3b8'
                      }}
                    />
                  </div>
                </div>

                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Diagnostic Accuracy:</span>
                    <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--text-main)' }}>
                      {simStep >= idx ? `${bench.diagnostic_accuracy_pct}%` : '...'}
                    </span>
                  </div>
                  <div style={{ width: '100%', height: '6px', borderRadius: '3px', background: '#e2e8f0', overflow: 'hidden' }}>
                    <div
                      style={{
                        height: '100%',
                        borderRadius: '3px',
                        width: `${bench.diagnostic_accuracy_pct}%`,
                        backgroundColor: isMindMesh ? 'var(--success)' : '#94a3b8'
                      }}
                    />
                  </div>
                </div>

                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Discovery Rate:</span>
                    <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--text-main)' }}>
                      {simStep >= idx ? `${bench.root_gap_discovery_rate}%` : '...'}
                    </span>
                  </div>
                  <div style={{ width: '100%', height: '6px', borderRadius: '3px', background: '#e2e8f0', overflow: 'hidden' }}>
                    <div
                      style={{
                        height: '100%',
                        borderRadius: '3px',
                        width: `${bench.root_gap_discovery_rate}%`,
                        backgroundColor: isMindMesh ? 'var(--success)' : '#94a3b8'
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Minimal Disclaimer */}
      <div style={{ padding: '12px 16px', borderRadius: '8px', background: '#f8fafc', border: '1px solid var(--border-card)', fontSize: '12px', color: 'var(--text-muted)', lineHeight: 1.5 }}>
        <strong>Evaluation Note:</strong> Simulated results validate algorithmic graph search efficiency (4.8 questions vs 11.4 in linear curricula). They do not establish real-world educational effectiveness.
      </div>
    </div>
  );
};
