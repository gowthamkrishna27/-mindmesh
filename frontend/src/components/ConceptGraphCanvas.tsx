import React, { useState } from 'react';
import type { Concept, StudentMastery } from '../data/mockData';
import { CONCEPTS } from '../data/mockData';
import { ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';

interface ConceptGraphCanvasProps {
  masteryMap: Record<string, StudentMastery>;
  selectedConceptId: string | null;
  onSelectConcept: (concept: Concept) => void;
  rootGapId?: string;
}

export const ConceptGraphCanvas: React.FC<ConceptGraphCanvasProps> = ({
  masteryMap,
  selectedConceptId,
  onSelectConcept,
  rootGapId = 'D12'
}) => {
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  const handleMouseDown = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).tagName === 'svg' || (e.target as HTMLElement).id === 'graph-bg') {
      setIsDragging(true);
      setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setPan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    }
  };

  const handleMouseUp = () => setIsDragging(false);

  // Status colors
  const getNodeColor = (status?: string, isRootGap?: boolean) => {
    if (isRootGap) {
      return { bg: '#fff1f2', border: '#e11d48', text: '#9f1239', scoreColor: '#e11d48' };
    }
    switch (status) {
      case 'mastered':
        return { bg: '#ffffff', border: '#10b981', text: '#0f172a', scoreColor: '#059669' };
      case 'confirmed':
        return { bg: '#fff1f2', border: '#e11d48', text: '#9f1239', scoreColor: '#e11d48' };
      case 'suspected':
        return { bg: '#ffffff', border: '#f43f5e', text: '#0f172a', scoreColor: '#e11d48' };
      case 'uncertain':
        return { bg: '#ffffff', border: '#f59e0b', text: '#0f172a', scoreColor: '#d97706' };
      default:
        return { bg: '#ffffff', border: '#e2e8f0', text: '#334155', scoreColor: '#94a3b8' };
    }
  };

  const edges: { from: Concept; to: Concept; id: string }[] = [];
  CONCEPTS.forEach(concept => {
    concept.prerequisites.forEach(prereqId => {
      const prereqConcept = CONCEPTS.find(c => c.id === prereqId);
      if (prereqConcept) {
        edges.push({
          from: prereqConcept,
          to: concept,
          id: `${prereqId}->${concept.id}`
        });
      }
    });
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      {/* Canvas */}
      <div 
        className="card-clean"
        style={{
          position: 'relative',
          width: '100%',
          height: '520px',
          background: '#ffffff',
          overflow: 'hidden',
          userSelect: 'none'
        }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <svg id="graph-bg" style={{ width: '100%', height: '100%', cursor: isDragging ? 'grabbing' : 'grab' }}>
          <defs>
            <pattern id="light-grid" width="24" height="24" patternUnits="userSpaceOnUse">
              <path d="M 24 0 L 0 0 0 24" fill="none" stroke="#f8fafc" strokeWidth="1" />
            </pattern>
            <marker
              id="arrowhead"
              markerWidth="6"
              markerHeight="5"
              refX="5"
              refY="2.5"
              orient="auto"
            >
              <polygon points="0 0, 6 2.5, 0 5" fill="#94a3b8" />
            </marker>
            <marker
              id="arrowhead-gap"
              markerWidth="6"
              markerHeight="5"
              refX="5"
              refY="2.5"
              orient="auto"
            >
              <polygon points="0 0, 6 2.5, 0 5" fill="#e11d48" />
            </marker>
          </defs>

          <rect width="100%" height="100%" fill="url(#light-grid)" />

          <g transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}>
            {/* Edges */}
            {edges.map(edge => {
              const isRootGapEdge = edge.from.id === rootGapId || edge.to.id === rootGapId;
              const fromX = edge.from.x + 60;
              const fromY = edge.from.y + 21;
              const toX = edge.to.x + 60;
              const toY = edge.to.y + 21;

              const dx = toX - fromX;
              const cx1 = fromX + dx * 0.45;
              const cy1 = fromY;
              const cx2 = toX - dx * 0.45;
              const cy2 = toY;

              return (
                <path
                  key={edge.id}
                  d={`M ${fromX} ${fromY} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${toX} ${toY}`}
                  fill="none"
                  stroke={isRootGapEdge ? '#e11d48' : '#cbd5e1'}
                  strokeWidth={isRootGapEdge ? 1.8 : 1.1}
                  strokeDasharray={isRootGapEdge ? '4 3' : 'none'}
                  markerEnd={isRootGapEdge ? 'url(#arrowhead-gap)' : 'url(#arrowhead)'}
                  opacity={isRootGapEdge ? 0.95 : 0.6}
                />
              );
            })}

            {/* Nodes */}
            {CONCEPTS.map(concept => {
              const mastery = masteryMap[concept.id];
              const status = mastery?.status || 'insufficient';
              const isRootGap = concept.id === rootGapId;
              const colors = getNodeColor(status, isRootGap);
              const isSelected = selectedConceptId === concept.id;

              return (
                <g
                  key={concept.id}
                  transform={`translate(${concept.x}, ${concept.y})`}
                  onClick={() => onSelectConcept(concept)}
                  style={{ cursor: 'pointer' }}
                >
                  {/* Selection Ring */}
                  {isSelected && (
                    <rect
                      x="-3"
                      y="-3"
                      width="126"
                      height="48"
                      rx="7"
                      fill="none"
                      stroke="var(--primary)"
                      strokeWidth="1.5"
                    />
                  )}

                  {/* Node Box */}
                  <rect
                    x="0"
                    y="0"
                    width="120"
                    height="42"
                    rx="6"
                    fill={colors.bg}
                    stroke={colors.border}
                    strokeWidth={status === 'suspected' ? '1.2' : isRootGap ? '1.5' : '1.2'}
                    strokeDasharray={status === 'suspected' ? '3 3' : 'none'}
                  />

                  {/* Top Row: Concept ID and Percentage */}
                  <text
                    x="8"
                    y="16"
                    fill="#0f172a"
                    fontSize="10"
                    fontWeight="700"
                    fontFamily="'JetBrains Mono', monospace"
                  >
                    {concept.id}
                  </text>

                  <text
                    x="112"
                    y="16"
                    textAnchor="end"
                    fill={colors.scoreColor}
                    fontSize="10"
                    fontWeight="600"
                    fontFamily="'JetBrains Mono', monospace"
                  >
                    {mastery?.p !== undefined ? `${(mastery.p * 100).toFixed(0)}%` : '—'}
                  </text>

                  {/* Bottom Row: Name */}
                  <text
                    x="8"
                    y="31"
                    fill={colors.text}
                    fontSize="10"
                    fontWeight="500"
                    fontFamily="'Plus Jakarta Sans', sans-serif"
                  >
                    {concept.name.length > 15 ? concept.name.substring(0, 14) + '…' : concept.name}
                  </text>
                </g>
              );
            })}
          </g>
        </svg>

        {/* Minimal Zoom Controls */}
        <div style={{ position: 'absolute', top: '10px', right: '10px', display: 'flex', gap: '2px', background: '#ffffff', padding: '3px', borderRadius: '6px', border: '1px solid var(--border-card)' }}>
          <button
            onClick={() => setZoom(z => Math.min(z + 0.15, 1.8))}
            style={{ padding: '4px', borderRadius: '4px', color: 'var(--text-muted)' }}
            title="Zoom In"
          >
            <ZoomIn size={13} />
          </button>
          <button
            onClick={() => setZoom(z => Math.max(z - 0.15, 0.7))}
            style={{ padding: '4px', borderRadius: '4px', color: 'var(--text-muted)' }}
            title="Zoom Out"
          >
            <ZoomOut size={13} />
          </button>
          <button
            onClick={() => { setZoom(1); setPan({ x: 0, y: 0 }); }}
            style={{ padding: '4px', borderRadius: '4px', color: 'var(--text-muted)' }}
            title="Reset"
          >
            <RotateCcw size={13} />
          </button>
        </div>
      </div>

      {/* External Legend Row (below canvas, never overlapping nodes) */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '6px 12px', fontSize: '11.5px', color: 'var(--text-muted)', flexWrap: 'wrap', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '2px', background: 'var(--success)' }} />
            <span>Mastered (&gt;70%)</span>
          </span>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '2px', background: 'var(--warning)' }} />
            <span>Uncertain</span>
          </span>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '2px', border: '1px dashed var(--danger)' }} />
            <span>Suspected</span>
          </span>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '2px', background: 'var(--danger)' }} />
            <span style={{ fontWeight: 600, color: 'var(--danger)' }}>Confirmed Root Gap (&lt;30%)</span>
          </span>
        </div>
        <div>
          <span>Directed Prerequisite: A → B</span>
        </div>
      </div>
    </div>
  );
};
