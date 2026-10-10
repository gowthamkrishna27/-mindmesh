'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import { ZoomIn, ZoomOut, RotateCcw, Maximize2, Minimize2, Expand, CheckCircle, AlertTriangle, Info } from 'lucide-react';
import { Concept, StudentMastery } from '@/lib/types';
import { fetchConcepts } from '@/lib/apiClient';

interface ConceptGraphProps {
  masteryMap: Record<string, StudentMastery>;
  selectedConceptId: string | null;
  onSelectConcept: (concept: Concept) => void;
  rootGapId?: string;
  isDark?: boolean;
  concepts?: Concept[];
}

export function ConceptGraph({
  masteryMap,
  selectedConceptId,
  onSelectConcept,
  rootGapId,
  isDark = false,
  concepts
}: ConceptGraphProps) {
  const [loadedConcepts, setLoadedConcepts] = useState<Concept[]>(concepts || []);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!concepts || concepts.length === 0) {
      fetchConcepts().then(c => {
        if (c && c.length > 0) setLoadedConcepts(c);
      });
    }
  }, [concepts]);

  const activeConcepts = concepts && concepts.length > 0 ? concepts : loadedConcepts;
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 20, y: 10 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Compute full bounding box and fit all 18 nodes nicely into container
  const fitToView = useCallback(() => {
    const container = containerRef.current;
    if (!container || activeConcepts.length === 0) return;

    const { clientWidth: width, clientHeight: height } = container;
    if (width <= 0 || height <= 0) return;

    let minX = Infinity;
    let minY = Infinity;
    let maxX = -Infinity;
    let maxY = -Infinity;

    activeConcepts.forEach(c => {
      const x = c.x ?? 0;
      const y = c.y ?? 0;
      if (x < minX) minX = x;
      if (y < minY) minY = y;
      if (x + 136 > maxX) maxX = x + 136;
      if (y + 48 > maxY) maxY = y + 48;
    });

    if (!isFinite(minX) || !isFinite(maxX) || !isFinite(minY) || !isFinite(maxY)) return;

    const graphWidth = maxX - minX;
    const graphHeight = maxY - minY;
    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;

    // Generous edge padding
    const paddingX = Math.min(52, width * 0.08);
    const paddingY = Math.min(48, height * 0.08);

    const availableWidth = Math.max(width - paddingX * 2, 80);
    const availableHeight = Math.max(height - paddingY * 2, 80);

    const scaleX = availableWidth / graphWidth;
    const scaleY = availableHeight / graphHeight;

    // Calculate fit zoom
    const fitZoom = Math.min(Math.max(Math.min(scaleX, scaleY), 0.35), 1.25);

    const panX = width / 2 - centerX * fitZoom;
    const panY = height / 2 - centerY * fitZoom;

    setZoom(Number(fitZoom.toFixed(3)));
    setPan({ x: Math.round(panX), y: Math.round(panY) });
  }, [activeConcepts]);

  // Auto-fit on initial render and whenever concepts change
  useEffect(() => {
    if (activeConcepts.length > 0) {
      const timer = setTimeout(() => {
        fitToView();
      }, 50);
      return () => clearTimeout(timer);
    }
  }, [activeConcepts.length, fitToView]);

  // Auto-fit on container resize (window resizing or fullscreen toggling)
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const observer = new ResizeObserver(() => {
      fitToView();
    });
    observer.observe(container);

    return () => observer.disconnect();
  }, [fitToView]);

  // Smooth wheel zoom
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleWheel = (e: WheelEvent) => {
      e.preventDefault();
      const rect = container.getBoundingClientRect();
      const cursorX = e.clientX - rect.left;
      const cursorY = e.clientY - rect.top;

      const delta = -e.deltaY;
      const factor = delta > 0 ? 1.08 : 0.92;

      setZoom(prevZoom => {
        const nextZoom = Math.min(Math.max(prevZoom * factor, 0.35), 2.2);
        setPan(prevPan => ({
          x: cursorX - (cursorX - prevPan.x) * (nextZoom / prevZoom),
          y: cursorY - (cursorY - prevPan.y) * (nextZoom / prevZoom)
        }));
        return Number(nextZoom.toFixed(3));
      });
    };

    container.addEventListener('wheel', handleWheel, { passive: false });
    return () => {
      container.removeEventListener('wheel', handleWheel);
    };
  }, []);

  // Handle Escape key to exit fullscreen
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isFullscreen) {
        setIsFullscreen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isFullscreen]);

  const handleMouseDown = (e: React.MouseEvent) => {
    const target = e.target as HTMLElement;
    const isNode = target.closest('[data-node="true"]');
    if (!isNode) {
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

  // Status colors compatible with theme
  const getNodeColor = (status?: string, isRootGap?: boolean, isAssessed?: boolean) => {
    if (isRootGap && rootGapId) {
      return {
        bg: isDark ? '#3b0d19' : '#fff1f2',
        border: '#e11d48',
        text: isDark ? '#fda4af' : '#9f1239',
        scoreColor: '#e11d48',
        label: 'ROOT GAP'
      };
    }
    if (!isAssessed) {
      return {
        bg: isDark ? '#1e293b' : '#ffffff',
        border: isDark ? '#334155' : '#cbd5e1',
        text: isDark ? '#94a3b8' : '#64748b',
        scoreColor: isDark ? '#64748b' : '#94a3b8',
        label: 'UNASSESSED'
      };
    }
    switch (status) {
      case 'mastered':
        return {
          bg: isDark ? '#062d1d' : '#f0fdf4',
          border: '#10b981',
          text: isDark ? '#6ee7b7' : '#065f46',
          scoreColor: '#10b981',
          label: 'MASTERED'
        };
      case 'confirmed':
        return {
          bg: isDark ? '#3b0d19' : '#fff1f2',
          border: '#e11d48',
          text: isDark ? '#fda4af' : '#9f1239',
          scoreColor: '#e11d48',
          label: 'GAP (CONFIRMED)'
        };
      case 'suspected':
        return {
          bg: isDark ? '#331219' : '#fff1f2',
          border: '#f43f5e',
          text: isDark ? '#fda4af' : '#be123c',
          scoreColor: '#f43f5e',
          label: 'SUSPECTED GAP'
        };
      case 'uncertain':
        return {
          bg: isDark ? '#2e1c07' : '#fffbeb',
          border: '#f59e0b',
          text: isDark ? '#fcd34d' : '#92400e',
          scoreColor: '#d97706',
          label: 'UNCERTAIN'
        };
      default:
        return {
          bg: isDark ? '#1e293b' : '#ffffff',
          border: isDark ? '#334155' : '#cbd5e1',
          text: isDark ? '#94a3b8' : '#475569',
          scoreColor: '#94a3b8',
          label: 'UNASSESSED'
        };
    }
  };

  // Build DAG edges
  const edges: { from: Concept; to: Concept; id: string }[] = [];
  activeConcepts.forEach(concept => {
    concept.prerequisites.forEach(prereqId => {
      const prereqConcept = activeConcepts.find(c => c.id === prereqId);
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
    <div className={isFullscreen ? "fixed inset-0 z-50 flex flex-col gap-3 bg-background/95 p-4 sm:p-6 backdrop-blur-md shadow-2xl" : "flex flex-col gap-3"}>
      {/* Graph Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex flex-wrap items-center gap-3">
          <span className="flex items-center gap-1.5 font-medium">
            <span className="size-2.5 rounded-full bg-emerald-500" />
            Mastered (p &gt; 0.70)
          </span>
          <span className="flex items-center gap-1.5 font-medium">
            <span className="size-2.5 rounded-full bg-amber-500" />
            Uncertain (p 0.35-0.65)
          </span>
          <span className="flex items-center gap-1.5 font-medium">
            <span className="size-2.5 rounded-full bg-rose-500" />
            Gap / Weakness
          </span>
          <span className="flex items-center gap-1.5 font-medium text-rose-600 dark:text-rose-400">
            <span className="size-2.5 animate-pulse rounded-full bg-rose-600 ring-2 ring-rose-400" />
            Root Gap (Target Blocker)
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="hidden sm:inline-block px-2 py-0.5 rounded text-[11px] font-mono text-muted-foreground bg-muted/60">
            {Math.round(zoom * 100)}%
          </span>
          <button
            onClick={() => setZoom(z => Number(Math.min(z + 0.15, 2.2).toFixed(3)))}
            className="flex size-7 items-center justify-center rounded border bg-card text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
            title="Zoom In"
          >
            <ZoomIn className="size-3.5" />
          </button>
          <button
            onClick={() => setZoom(z => Number(Math.max(z - 0.15, 0.35).toFixed(3)))}
            className="flex size-7 items-center justify-center rounded border bg-card text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
            title="Zoom Out"
          >
            <ZoomOut className="size-3.5" />
          </button>
          <button
            onClick={fitToView}
            className="flex h-7 items-center gap-1.5 px-2.5 rounded border bg-card text-xs font-medium text-foreground hover:bg-muted hover:border-primary/40 transition-colors shadow-xs"
            title="Full Fit View (Auto-scale & center entire curriculum)"
          >
            <Maximize2 className="size-3.5 text-primary" />
            <span>Fit View</span>
          </button>
          <button
            onClick={() => setIsFullscreen(f => !f)}
            className="flex size-7 items-center justify-center rounded border bg-card text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
            title={isFullscreen ? "Exit Fullscreen (Esc)" : "Expand Fullscreen"}
          >
            {isFullscreen ? <Minimize2 className="size-3.5" /> : <Expand className="size-3.5" />}
          </button>
          <button
            onClick={fitToView}
            className="flex size-7 items-center justify-center rounded border bg-card text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
            title="Reset to Fit View"
          >
            <RotateCcw className="size-3.5" />
          </button>
        </div>
      </div>

      {/* SVG Canvas */}
      <div
        ref={containerRef}
        className={isFullscreen ? "relative flex-1 w-full min-h-0 overflow-hidden rounded-xl border bg-card shadow-inner" : "relative h-[560px] sm:h-[600px] lg:h-[640px] w-full overflow-hidden rounded-lg border bg-card"}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <svg
          id="graph-bg"
          className="size-full"
          style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
        >
          <defs>
            <pattern id="grid-pattern" width="28" height="28" patternUnits="userSpaceOnUse">
              <path
                d="M 28 0 L 0 0 0 28"
                fill="none"
                stroke={isDark ? '#334155' : '#f1f5f9'}
                strokeWidth="1"
              />
            </pattern>
            <marker id="arrowhead" markerWidth="6" markerHeight="5" refX="5" refY="2.5" orient="auto">
              <polygon points="0 0, 6 2.5, 0 5" fill={isDark ? '#64748b' : '#94a3b8'} />
            </marker>
            <marker id="arrowhead-gap" markerWidth="6" markerHeight="5" refX="5" refY="2.5" orient="auto">
              <polygon points="0 0, 6 2.5, 0 5" fill="#e11d48" />
            </marker>
          </defs>

          <rect width="100%" height="100%" fill="url(#grid-pattern)" />

          <g transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}>
            {/* Edges */}
            {edges.map(edge => {
              const isRootEdge = !!rootGapId && (edge.from.id === rootGapId || edge.to.id === rootGapId);
              const fromX = edge.from.x + 68;
              const fromY = edge.from.y + 24;
              const toX = edge.to.x + 68;
              const toY = edge.to.y + 24;

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
                  stroke={isRootEdge ? '#e11d48' : isDark ? '#475569' : '#cbd5e1'}
                  strokeWidth={isRootEdge ? '2.5' : '1.5'}
                  strokeDasharray={isRootEdge ? 'none' : 'none'}
                  markerEnd={isRootEdge ? 'url(#arrowhead-gap)' : 'url(#arrowhead)'}
                  opacity={isRootEdge ? 0.9 : 0.65}
                />
              );
            })}

            {/* Nodes */}
            {activeConcepts.map(concept => {
              const mastery = masteryMap[concept.id];
              const isRootGap = !!rootGapId && concept.id === rootGapId;
              const isSelected = concept.id === selectedConceptId;
              const isAssessed = !!mastery && (mastery.n_direct > 0 || mastery.status === 'mastered' || mastery.status === 'confirmed');
              const style = getNodeColor(mastery?.status, isRootGap, isAssessed);
              const pLabel = isAssessed ? `${Math.round(mastery.p * 100)}%` : '—';

              return (
                <g
                  key={concept.id}
                  data-node="true"
                  transform={`translate(${concept.x}, ${concept.y})`}
                  onClick={() => onSelectConcept(concept)}
                  className="cursor-pointer transition-transform"
                >
                  {/* Selection glow */}
                  {isSelected && (
                    <rect
                      x="-4"
                      y="-4"
                      width="144"
                      height="56"
                      rx="10"
                      fill="none"
                      stroke="#3b82f6"
                      strokeWidth="2.5"
                      strokeDasharray="4 2"
                    />
                  )}

                  {/* Node container */}
                  <rect
                    width="136"
                    height="48"
                    rx="8"
                    fill={style.bg}
                    stroke={isSelected ? '#3b82f6' : style.border}
                    strokeWidth={isRootGap ? '2.5' : '1.5'}
                    className="shadow-sm transition-colors"
                  />

                  {/* Root gap pulse ring */}
                  {isRootGap && (
                    <rect
                      x="-2"
                      y="-2"
                      width="140"
                      height="52"
                      rx="9"
                      fill="none"
                      stroke="#e11d48"
                      strokeWidth="1.5"
                      opacity="0.6"
                      className="animate-pulse"
                    />
                  )}

                  {/* Concept ID */}
                  <text
                    x="8"
                    y="18"
                    fontSize="10"
                    fontWeight="700"
                    fill={style.text}
                    fontFamily="inherit"
                  >
                    {concept.id}
                  </text>

                  {/* Status label / badge */}
                  <text
                    x="126"
                    y="18"
                    textAnchor="end"
                    fontSize="8.5"
                    fontWeight="600"
                    fill={style.scoreColor}
                    fontFamily="inherit"
                  >
                    {pLabel}
                  </text>

                  {/* Concept Title */}
                  <text
                    x="8"
                    y="34"
                    fontSize="10"
                    fontWeight="600"
                    fill={isDark ? '#e2e8f0' : '#1e293b'}
                    fontFamily="inherit"
                  >
                    {concept.name.length > 17 ? concept.name.slice(0, 16) + '…' : concept.name}
                  </text>
                </g>
              );
            })}
          </g>
        </svg>

        {/* Floating helper legend */}
        <div className="pointer-events-none absolute bottom-3 left-3 rounded border bg-card/90 px-3 py-1.5 text-[11px] text-muted-foreground backdrop-blur flex items-center gap-2">
          <span>Click any concept to inspect</span>
          <span className="text-muted-foreground/60">•</span>
          <span>Scroll to zoom</span>
          <span className="text-muted-foreground/60">•</span>
          <span>Drag to pan</span>
        </div>
      </div>
    </div>
  );
}
