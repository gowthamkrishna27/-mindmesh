import React, { useState } from 'react';
import { TEACHER_COHORT_HEATMAP } from '../data/mockData';

export const TeacherHeatmapView: React.FC = () => {
  const [selectedConceptId, setSelectedConceptId] = useState<string>('D12');
  const [sortBy, setSortBy] = useState<'gap_rate' | 'id'>('gap_rate');

  const sortedList = [...TEACHER_COHORT_HEATMAP].sort((a, b) => {
    if (sortBy === 'gap_rate') return b.gap_rate - a.gap_rate;
    return a.concept_id.localeCompare(b.concept_id);
  });

  const selectedItem = TEACHER_COHORT_HEATMAP.find(t => t.concept_id === selectedConceptId) || TEACHER_COHORT_HEATMAP[11];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '960px', margin: '0 auto' }}>
      {/* Header */}
      <div className="card-clean" style={{ padding: '20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span className="badge badge-uncertain">Teacher Cohort View</span>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Class CS 301 • 28 Students</span>
          </div>
          <h2 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text-main)' }}>Class Concept Gap Heatmap</h2>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Aggregate visualization of foundational prerequisites blocking cohort progress.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <button
            onClick={() => setSortBy('gap_rate')}
            className={sortBy === 'gap_rate' ? 'btn-primary' : 'btn-secondary'}
            style={{ fontSize: '12px', padding: '6px 12px' }}
          >
            Highest Gap
          </button>
          <button
            onClick={() => setSortBy('id')}
            className={sortBy === 'id' ? 'btn-primary' : 'btn-secondary'}
            style={{ fontSize: '12px', padding: '6px 12px' }}
          >
            Syllabus Order
          </button>
        </div>
      </div>

      {/* Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '12px' }}>
        {sortedList.map(item => {
          const isSelected = item.concept_id === selectedConceptId;

          return (
            <div
              key={item.concept_id}
              onClick={() => setSelectedConceptId(item.concept_id)}
              style={{
                padding: '14px',
                borderRadius: '8px',
                border: isSelected ? '1px solid var(--primary)' : '1px solid var(--border-card)',
                background: isSelected ? 'var(--primary-subtle)' : '#ffffff',
                cursor: 'pointer',
                display: 'flex',
                flexDirection: 'column',
                gap: '6px',
                transition: 'all 0.1s ease'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', fontWeight: 700, color: 'var(--primary)' }}>{item.concept_id}</span>
                <span style={{
                  fontSize: '11.5px',
                  fontFamily: 'var(--font-mono)',
                  fontWeight: 700,
                  color: item.gap_rate >= 50 ? 'var(--danger)' : item.gap_rate >= 25 ? 'var(--warning)' : 'var(--success)'
                }}>
                  {item.gap_rate}% Need Help
                </span>
              </div>

              <h4 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-main)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{item.name}</h4>

              <div style={{ width: '100%', height: '6px', borderRadius: '3px', background: '#f1f5f9', overflow: 'hidden', display: 'flex', marginTop: '2px' }}>
                <div style={{ width: `${(item.confirmed_gaps / 28) * 100}%`, background: 'var(--danger)' }} />
                <div style={{ width: `${(item.suspected_gaps / 28) * 100}%`, background: 'var(--warning)' }} />
                <div style={{ width: `${(item.mastered / 28) * 100}%`, background: 'var(--success)' }} />
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-muted)' }}>
                <span>{item.confirmed_gaps} Confirmed</span>
                <span>{item.suspected_gaps} Suspected</span>
                <span>{item.mastered} Mastered</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Selected Drilldown */}
      <div className="card-clean" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', paddingBottom: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '15px', fontWeight: 700, color: 'var(--primary)' }}>{selectedItem.concept_id}</span>
            <h3 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-main)' }}>{selectedItem.name} — Cohort Analysis</h3>
          </div>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>28 Student Cohort</span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '12px' }}>
          <div style={{ padding: '12px', borderRadius: '8px', background: '#f8fafc', border: '1px solid var(--border-card)' }}>
            <span style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>Struggling Learners:</span>
            <div style={{ fontSize: '18px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--danger)' }}>
              {selectedItem.confirmed_gaps + selectedItem.suspected_gaps} / 28 Students
            </div>
          </div>

          <div style={{ padding: '12px', borderRadius: '8px', background: '#f8fafc', border: '1px solid var(--border-card)' }}>
            <span style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>Primary Misconception:</span>
            <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--warning-text)' }}>
              Transitive Dependency Inversion
            </div>
            <p style={{ fontSize: '11.5px', color: 'var(--text-muted)', marginTop: '2px' }}>
              64% confused X → Y and Y → Z transitivity.
            </p>
          </div>

          <div style={{ padding: '12px', borderRadius: '8px', background: '#f8fafc', border: '1px solid var(--border-card)' }}>
            <span style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>Intervention Recommendation:</span>
            <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--success-text)' }}>
              15-Min Live Demonstration
            </div>
            <p style={{ fontSize: '11.5px', color: 'var(--text-muted)', marginTop: '2px' }}>
              Review Armstrong Axioms before 3NF lecture.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
