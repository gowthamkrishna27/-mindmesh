'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { CohortHeatmapRow, Concept, SimulationBenchmarkItem } from '@/lib/types';
import { fetchCohortData, fetchConcepts } from '@/lib/apiClient';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import {
  Users,
  AlertTriangle,
  Flame,
  BarChart2,
  TrendingDown,
  ArrowUpDown,
  Search,
  CheckCircle2,
  HelpCircle,
  ExternalLink,
  ShieldCheck,
  BookOpen,
  Calendar,
  Clock,
  Sparkles,
  Copy,
  Check,
  ChevronDown,
  Layers,
  FileText,
  Lightbulb
} from 'lucide-react';

// Class cohort student mock data for authorized educator inspection
interface StudentCohortRecord {
  id: string;
  name: string;
  email: string;
  conceptMastery: Record<string, {
    status: 'mastered' | 'confirmed' | 'suspected' | 'untested';
    p: number;
    misconception?: string;
    chosenOption?: string;
    responseMs?: number;
    confidence?: 'high' | 'medium' | 'low';
  }>;
}

const CLASS_ROSTER: StudentCohortRecord[] = [
  {
    id: 'usr_alex_chen',
    name: 'Alex Chen',
    email: 'alex.chen@mindmesh.edu',
    conceptMastery: {
      D12: { status: 'confirmed', p: 0.18, misconception: 'Confuses relation-level FD constraint with instance-level row pattern', chosenOption: 'C', responseMs: 14200, confidence: 'high' },
      D13: { status: 'confirmed', p: 0.22, misconception: 'Assumes 2NF eliminates transitive dependencies', chosenOption: 'A', responseMs: 16800, confidence: 'medium' },
      D18: { status: 'suspected', p: 0.35, misconception: 'Neglects index scan overhead when selectivity is low', chosenOption: 'B', responseMs: 19100, confidence: 'low' },
      D01: { status: 'mastered', p: 0.92, responseMs: 6400, confidence: 'high' },
      D02: { status: 'mastered', p: 0.88, responseMs: 7100, confidence: 'high' },
      D03: { status: 'confirmed', p: 0.28, misconception: 'Confuses minimal candidate key with non-minimal superkey', chosenOption: 'C', responseMs: 11200, confidence: 'high' }
    }
  },
  {
    id: 'usr_marcus_v',
    name: 'Marcus Vance',
    email: 'marcus.v@mindmesh.edu',
    conceptMastery: {
      D12: { status: 'confirmed', p: 0.15, misconception: 'Treats functional dependency as an instance-level relationship rather than a schema-level constraint', chosenOption: 'C', responseMs: 18400, confidence: 'high' },
      D13: { status: 'confirmed', p: 0.20, misconception: 'Confuses BCNF violation with 3NF transitive check', chosenOption: 'B', responseMs: 15300, confidence: 'medium' },
      D18: { status: 'confirmed', p: 0.25, misconception: 'Believes sequential scans are always slower than nested loops', chosenOption: 'D', responseMs: 22100, confidence: 'high' },
      D01: { status: 'mastered', p: 0.85, responseMs: 8200, confidence: 'high' },
      D02: { status: 'mastered', p: 0.79, responseMs: 9500, confidence: 'medium' }
    }
  },
  {
    id: 'usr_elena_r',
    name: 'Elena Rostova',
    email: 'elena.r@mindmesh.edu',
    conceptMastery: {
      D12: { status: 'confirmed', p: 0.24, misconception: 'Assumes non-trivial FD can be inferred without closure verification', chosenOption: 'A', responseMs: 13500, confidence: 'medium' },
      D13: { status: 'suspected', p: 0.38, misconception: 'Struggles with decomposing into loss-less join schemas', chosenOption: 'D', responseMs: 17200, confidence: 'low' },
      D18: { status: 'confirmed', p: 0.19, misconception: 'Ignores join ordering dynamic programming cost model', chosenOption: 'B', responseMs: 24500, confidence: 'high' },
      D01: { status: 'mastered', p: 0.94, responseMs: 5800, confidence: 'high' },
      D02: { status: 'mastered', p: 0.91, responseMs: 6300, confidence: 'high' }
    }
  },
  {
    id: 'usr_priya_s',
    name: 'Priya Sharma',
    email: 'priya.s@mindmesh.edu',
    conceptMastery: {
      D12: { status: 'confirmed', p: 0.19, misconception: 'Confuses relation-level FD constraint with instance-level row pattern', chosenOption: 'C', responseMs: 12900, confidence: 'high' },
      D13: { status: 'confirmed', p: 0.21, misconception: 'Fails to check candidate key determinants in 3NF', chosenOption: 'A', responseMs: 14700, confidence: 'medium' },
      D18: { status: 'suspected', p: 0.42, misconception: 'Underestimates disk I/O cost relative to CPU comparisons', chosenOption: 'C', responseMs: 18800, confidence: 'low' },
      D01: { status: 'mastered', p: 0.96, responseMs: 5100, confidence: 'high' },
      D02: { status: 'mastered', p: 0.86, responseMs: 7400, confidence: 'high' }
    }
  },
  {
    id: 'usr_dev_patel',
    name: 'Dev Patel',
    email: 'dev.p@mindmesh.edu',
    conceptMastery: {
      D12: { status: 'confirmed', p: 0.22, misconception: 'Treats functional dependency as an instance-level relationship rather than a schema-level constraint', chosenOption: 'C', responseMs: 16100, confidence: 'high' },
      D13: { status: 'confirmed', p: 0.26, misconception: 'Assumes 2NF eliminates transitive dependencies', chosenOption: 'A', responseMs: 13900, confidence: 'medium' },
      D18: { status: 'confirmed', p: 0.22, misconception: 'Neglects index scan overhead when selectivity is low', chosenOption: 'B', responseMs: 21300, confidence: 'high' },
      D01: { status: 'mastered', p: 0.89, responseMs: 7800, confidence: 'high' },
      D02: { status: 'mastered', p: 0.82, responseMs: 8600, confidence: 'medium' }
    }
  },
  {
    id: 'usr_sarah_j',
    name: 'Sarah Jenkins',
    email: 'sarah.j@mindmesh.edu',
    conceptMastery: {
      D12: { status: 'confirmed', p: 0.16, misconception: 'Confuses relation-level FD constraint with instance-level row pattern', chosenOption: 'C', responseMs: 15300, confidence: 'high' },
      D13: { status: 'confirmed', p: 0.18, misconception: 'Fails to verify dependency preservation during decomposition', chosenOption: 'D', responseMs: 17600, confidence: 'high' },
      D18: { status: 'confirmed', p: 0.28, misconception: 'Believes sequential scans are always slower than nested loops', chosenOption: 'D', responseMs: 19500, confidence: 'medium' },
      D01: { status: 'mastered', p: 0.91, responseMs: 6200, confidence: 'high' },
      D02: { status: 'mastered', p: 0.89, responseMs: 6800, confidence: 'high' }
    }
  },
  {
    id: 'usr_liam_o',
    name: 'Liam O’Connor',
    email: 'liam.o@mindmesh.edu',
    conceptMastery: {
      D12: { status: 'confirmed', p: 0.21, misconception: 'Treats functional dependency as an instance-level relationship rather than a schema-level constraint', chosenOption: 'C', responseMs: 17800, confidence: 'high' },
      D13: { status: 'confirmed', p: 0.24, misconception: 'Assumes 2NF eliminates transitive dependencies', chosenOption: 'A', responseMs: 15100, confidence: 'medium' },
      D18: { status: 'confirmed', p: 0.24, misconception: 'Ignores join ordering dynamic programming cost model', chosenOption: 'B', responseMs: 23200, confidence: 'high' },
      D01: { status: 'mastered', p: 0.88, responseMs: 7900, confidence: 'high' },
      D02: { status: 'mastered', p: 0.84, responseMs: 8100, confidence: 'high' }
    }
  },
  {
    id: 'usr_aisha_k',
    name: 'Aisha Khan',
    email: 'aisha.k@mindmesh.edu',
    conceptMastery: {
      D12: { status: 'confirmed', p: 0.17, misconception: 'Confuses relation-level FD constraint with instance-level row pattern', chosenOption: 'C', responseMs: 14900, confidence: 'high' },
      D13: { status: 'confirmed', p: 0.19, misconception: 'Confuses BCNF violation with 3NF transitive check', chosenOption: 'B', responseMs: 16400, confidence: 'medium' },
      D18: { status: 'confirmed', p: 0.29, misconception: 'Neglects index scan overhead when selectivity is low', chosenOption: 'B', responseMs: 20100, confidence: 'high' },
      D01: { status: 'mastered', p: 0.95, responseMs: 5400, confidence: 'high' },
      D02: { status: 'mastered', p: 0.92, responseMs: 6100, confidence: 'high' }
    }
  }
];

export function EducatorDashboard() {
  const [filter, setFilter] = useState<'all' | 'high-risk' | 'moderate' | 'mastered'>('all');
  const [sortBy, setSortBy] = useState<'gap_rate' | 'tier' | 'name'>('gap_rate');
  const [selectedConceptId, setSelectedConceptId] = useState<string>('D12');
  const [studentSearch, setStudentSearch] = useState('');
  const [rosterTab, setRosterTab] = useState<'roster' | 'evidence'>('roster');
  const [isCopied, setIsCopied] = useState(false);

  const [heatmapData, setHeatmapData] = useState<CohortHeatmapRow[]>([]);
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [benchmarks, setBenchmarks] = useState<SimulationBenchmarkItem[]>([]);

  useEffect(() => {
    fetchCohortData().then(res => {
      if (res && res.cohort.length > 0) {
        setHeatmapData(res.cohort);
        if (res.benchmarks) setBenchmarks(res.benchmarks);
      }
    });
    fetchConcepts().then(c => {
      if (c && c.length > 0) setConcepts(c);
    });
  }, []);

  const selectedConcept = useMemo(
    () => concepts.find(c => c.id === selectedConceptId),
    [concepts, selectedConceptId]
  );

  const selectedHeatmap = useMemo(
    () => heatmapData.find(h => h.concept_id === selectedConceptId),
    [heatmapData, selectedConceptId]
  );

  // Filter and sort concepts
  const displayedConcepts = useMemo(() => {
    let list = [...heatmapData];
    if (filter === 'high-risk') {
      list = list.filter(item => item.gap_rate >= 40);
    } else if (filter === 'moderate') {
      list = list.filter(item => item.gap_rate >= 20 && item.gap_rate < 40);
    } else if (filter === 'mastered') {
      list = list.filter(item => item.gap_rate < 20);
    }

    list.sort((a, b) => {
      if (sortBy === 'gap_rate') return b.gap_rate - a.gap_rate;
      if (sortBy === 'name') return a.name.localeCompare(b.name);
      return a.concept_id.localeCompare(b.concept_id);
    });
    return list;
  }, [heatmapData, filter, sortBy]);

  // Students struggling with the selected concept
  const studentsForSelectedConcept = useMemo(() => {
    return CLASS_ROSTER.filter(st => {
      if (studentSearch.trim()) {
        const query = studentSearch.toLowerCase();
        if (!st.name.toLowerCase().includes(query) && !st.email.toLowerCase().includes(query)) {
          return false;
        }
      }
      return true;
    }).map(st => {
      const record = st.conceptMastery[selectedConceptId] || {
        status: (selectedHeatmap && selectedHeatmap.gap_rate > 40 ? 'confirmed' : 'mastered') as 'confirmed' | 'mastered',
        p: selectedHeatmap && selectedHeatmap.gap_rate > 40 ? 0.25 : 0.85,
        misconception: selectedHeatmap && selectedHeatmap.gap_rate > 40 ? 'Needs foundational closure review' : undefined,
        chosenOption: 'C',
        responseMs: 14000,
        confidence: 'medium' as const
      };
      return {
        ...st,
        masteryRecord: record
      };
    });
  }, [selectedConceptId, studentSearch, selectedHeatmap]);

  const handleCopyPlan = () => {
    if (!selectedConcept) return;
    const planText = `MIND MESH Targeted Teaching Plan
Concept: ${selectedConcept.id} - ${selectedConcept.name}
Class Gap Rate: ${selectedHeatmap?.gap_rate ?? 64}% (${selectedHeatmap?.confirmed_gaps ?? 11} students confirmed gaps)

Recommended 45-Min Lecture & Revision Agenda:
1. Warmup (10m): Revisit upstream foundations [${(selectedConcept.prerequisites || []).join(', ') || 'Core axioms'}]
2. Core Conceptual Correction (20m): Live derivation & counter-examples targeting top misconception: "${studentsForSelectedConcept[0]?.masteryRecord?.misconception || 'Schema vs instance semantics'}".
3. Hands-on Diagnostic Drill (15m): Active problem solving on determinant closures.`;

    navigator.clipboard.writeText(planText).then(() => {
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2500);
    });
  };

  return (
    <div className="space-y-6 md:space-y-8">
      {/* 1. Header & Step Workflow Stepper */}
      <div className="space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="rounded bg-primary/10 px-2 py-0.5 text-xs font-semibold text-primary">
                Educator Workflow
              </span>
              <span className="flex items-center gap-1 rounded bg-amber-500/10 px-2 py-0.5 text-xs font-semibold text-amber-600 dark:text-amber-400">
                <ShieldCheck className="size-3.5" />
                Faculty Authorized
              </span>
            </div>
            <h1 className="mt-1 text-xl sm:text-2xl font-bold tracking-tight">
              Class-Level Mastery &amp; Targeted Intervention
            </h1>
            <p className="text-xs sm:text-sm text-muted-foreground mt-0.5">
              CS301: Database Management Systems &middot; Section A (24 Enrolled Students)
            </p>
          </div>
        </div>

        {/* 5-Step Workflow Visual Progress Banner */}
        <div className="rounded-xl border bg-card p-3 sm:p-4 shadow-xs">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground mb-2.5">
            5-Step Educator Diagnostic Workflow
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-xs">
            <div className="flex items-center gap-2 rounded-lg bg-emerald-500/10 p-2 text-emerald-700 dark:text-emerald-400 font-medium">
              <span className="flex size-5 shrink-0 items-center justify-center rounded-full bg-emerald-600 text-[10px] font-bold text-white">1</span>
              <span className="truncate">Educator Login</span>
            </div>
            <div className="flex items-center gap-2 rounded-lg bg-primary/10 p-2 text-primary font-medium">
              <span className="flex size-5 shrink-0 items-center justify-center rounded-full bg-primary text-[10px] font-bold text-white">2</span>
              <span className="truncate">Class Mastery</span>
            </div>
            <div className="flex items-center gap-2 rounded-lg bg-muted p-2 text-foreground font-medium">
              <span className="flex size-5 shrink-0 items-center justify-center rounded-full bg-foreground text-[10px] font-bold text-background">3</span>
              <span className="truncate">Struggling Topics</span>
            </div>
            <div className="flex items-center gap-2 rounded-lg bg-muted p-2 text-foreground font-medium">
              <span className="flex size-5 shrink-0 items-center justify-center rounded-full bg-foreground text-[10px] font-bold text-background">4</span>
              <span className="truncate">Evidence &amp; Roster</span>
            </div>
            <div className="flex items-center gap-2 rounded-lg bg-muted p-2 text-foreground font-medium col-span-2 sm:col-span-1">
              <span className="flex size-5 shrink-0 items-center justify-center rounded-full bg-foreground text-[10px] font-bold text-background">5</span>
              <span className="truncate">Targeted Teaching</span>
            </div>
          </div>
        </div>
      </div>

      {/* 2. Step 2: Class-Level Concept Mastery KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="rounded-xl border bg-card p-3 sm:p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Class Size</span>
            <Users className="size-4 text-muted-foreground" />
          </div>
          <p className="mt-1.5 text-xl sm:text-2xl font-bold">24 Students</p>
          <p className="text-[11px] text-emerald-600 dark:text-emerald-400 font-medium mt-0.5">100% completed diagnostic</p>
        </div>

        <div className="rounded-xl border bg-card p-3 sm:p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Top Cohort Blocker</span>
            <Flame className="size-4 text-rose-500" />
          </div>
          <p className="mt-1.5 text-xl sm:text-2xl font-bold text-rose-600 dark:text-rose-400">D12: FDs</p>
          <p className="text-[11px] text-muted-foreground mt-0.5">64% cohort gap rate (11 students)</p>
        </div>

        <div className="rounded-xl border bg-card p-3 sm:p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Critical Interventions</span>
            <AlertTriangle className="size-4 text-amber-500" />
          </div>
          <p className="mt-1.5 text-xl sm:text-2xl font-bold text-amber-600 dark:text-amber-400">3 Topics</p>
          <p className="text-[11px] text-muted-foreground mt-0.5">&gt; 50% cohort gap rate</p>
        </div>

        <div className="rounded-xl border bg-card p-3 sm:p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Diagnosis Speed</span>
            <BarChart2 className="size-4 text-muted-foreground" />
          </div>
          <p className="mt-1.5 text-xl sm:text-2xl font-bold">4.8 Questions</p>
          <p className="text-[11px] text-muted-foreground mt-0.5">58% faster than linear tests</p>
        </div>
      </div>

      {/* 3. Step 3: Identify Concepts Many Students Are Struggling With */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b pb-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="flex size-5 items-center justify-center rounded-full bg-primary text-[10px] font-bold text-white">3</span>
              <h2 className="text-base sm:text-lg font-bold tracking-tight">
                Identify Concepts With Widespread Learning Gaps
              </h2>
            </div>
            <p className="text-xs text-muted-foreground mt-0.5">
              Select any concept to inspect individual student evidence and launch targeted lesson planning.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {/* Filter buttons */}
            <div className="flex items-center rounded-lg border bg-muted/40 p-0.5 text-xs">
              <button
                type="button"
                onClick={() => setFilter('all')}
                className={cn('px-2.5 py-1 rounded-md font-medium transition-colors', filter === 'all' ? 'bg-background shadow-xs text-foreground' : 'text-muted-foreground hover:text-foreground')}
              >
                All ({heatmapData.length})
              </button>
              <button
                type="button"
                onClick={() => setFilter('high-risk')}
                className={cn('px-2.5 py-1 rounded-md font-medium transition-colors', filter === 'high-risk' ? 'bg-rose-500/10 text-rose-600 font-semibold' : 'text-muted-foreground hover:text-foreground')}
              >
                High Gaps (&ge;40%)
              </button>
              <button
                type="button"
                onClick={() => setFilter('mastered')}
                className={cn('px-2.5 py-1 rounded-md font-medium transition-colors', filter === 'mastered' ? 'bg-emerald-500/10 text-emerald-600 font-semibold' : 'text-muted-foreground hover:text-foreground')}
              >
                Mastered
              </button>
            </div>

            {/* Sort selector */}
            <select
              value={sortBy}
              onChange={e => setSortBy(e.target.value as any)}
              className="h-8 rounded-lg border bg-card px-2 text-xs font-medium text-foreground focus:outline-none"
            >
              <option value="gap_rate">Sort: Highest Gap Rate</option>
              <option value="tier">Sort: Curriculum Tier</option>
              <option value="name">Sort: Alphabetical</option>
            </select>
          </div>
        </div>

        {/* Concept Grid Cards */}
        <div className="grid gap-3 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
          {displayedConcepts.map(item => {
            const isSelected = item.concept_id === selectedConceptId;
            const isCritical = item.gap_rate >= 50;
            const isHigh = item.gap_rate >= 40 && item.gap_rate < 50;
            const isModerate = item.gap_rate >= 20 && item.gap_rate < 40;

            return (
              <button
                key={item.concept_id}
                type="button"
                onClick={() => setSelectedConceptId(item.concept_id)}
                className={cn(
                  'flex flex-col rounded-xl border p-3.5 text-left transition-all relative overflow-hidden',
                  isSelected
                    ? 'border-primary ring-2 ring-primary/30 bg-primary/5 shadow-sm'
                    : 'bg-card hover:border-foreground/20 hover:bg-muted/30'
                )}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
                      {item.concept_id}
                    </span>
                    <span className="text-xs font-bold leading-tight line-clamp-1">{item.name}</span>
                  </div>
                  <span
                    className={cn(
                      'rounded px-1.5 py-0.5 text-[11px] font-bold font-mono shrink-0',
                      isCritical
                        ? 'bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300'
                        : isHigh
                        ? 'bg-rose-50 text-rose-600 dark:bg-rose-900/50 dark:text-rose-300'
                        : isModerate
                        ? 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300'
                        : 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300'
                    )}
                  >
                    {item.gap_rate}% Gap
                  </span>
                </div>

                {/* Progress bar */}
                <div className="mt-2.5 w-full bg-muted rounded-full h-1.5 overflow-hidden flex">
                  <div
                    className={cn('h-full', isCritical || isHigh ? 'bg-rose-500' : isModerate ? 'bg-amber-500' : 'bg-emerald-500')}
                    style={{ width: `${item.gap_rate}%` }}
                  />
                  <div className="bg-emerald-500/30 h-full flex-1" />
                </div>

                <div className="mt-2 flex items-center justify-between text-[11px] text-muted-foreground">
                  <span className="text-rose-600 dark:text-rose-400 font-medium">
                    {item.confirmed_gaps} Students Blocked
                  </span>
                  <span>{item.mastered} Mastered</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* 4. Step 4: Inspect Available Evidence and Progress Summaries (Authorized Faculty Only) */}
      {selectedConcept && selectedHeatmap && (
        <div className="rounded-xl border bg-card shadow-sm overflow-hidden space-y-0">
          <div className="border-b bg-muted/40 p-4 sm:p-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <span className="flex size-5 items-center justify-center rounded-full bg-primary text-[10px] font-bold text-white">4</span>
                  <span className="text-xs font-mono font-bold text-primary">{selectedConcept.id}</span>
                  <h3 className="text-base sm:text-lg font-bold">{selectedConcept.name}</h3>
                  <span className="rounded bg-rose-500/10 px-2 py-0.5 text-xs font-bold text-rose-600">
                    {selectedHeatmap.gap_rate}% Class Gap Rate
                  </span>
                </div>
                <p className="text-xs text-muted-foreground mt-1 max-w-2xl">
                  {selectedConcept.description}
                </p>
              </div>

              {/* Roster vs Evidence Tab Selector */}
              <div className="flex items-center gap-1.5 self-start sm:self-auto rounded-lg border bg-background p-1 text-xs">
                <button
                  type="button"
                  onClick={() => setRosterTab('roster')}
                  className={cn('px-3 py-1 rounded-md font-medium transition-colors', rosterTab === 'roster' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground')}
                >
                  Student Roster ({studentsForSelectedConcept.length})
                </button>
                <button
                  type="button"
                  onClick={() => setRosterTab('evidence')}
                  className={cn('px-3 py-1 rounded-md font-medium transition-colors', rosterTab === 'evidence' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground')}
                >
                  Diagnostic Evidence Breakdown
                </button>
              </div>
            </div>

            {/* Privacy Notice for Student Data */}
            <div className="mt-3 flex items-center gap-1.5 text-[11px] text-muted-foreground">
              <ShieldCheck className="size-3.5 text-emerald-600" />
              <span>
                <strong>Confidential Roster:</strong> Student-level diagnostic evidence is accessible only to authorized course faculty.
              </span>
            </div>
          </div>

          {/* Tab 1: Student Roster Breakdown */}
          {rosterTab === 'roster' && (
            <div className="p-4 sm:p-5 space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                  Individual Student Performance &amp; Detected Misconceptions
                </span>
                <div className="relative w-full sm:w-64">
                  <Search className="absolute left-2.5 top-2.5 size-3.5 text-muted-foreground" />
                  <input
                    type="text"
                    value={studentSearch}
                    onChange={e => setStudentSearch(e.target.value)}
                    placeholder="Search student by name..."
                    className="h-8 w-full rounded-lg border bg-background pl-8 pr-3 text-xs focus:outline-none"
                  />
                </div>
              </div>

              {/* Desktop Table View */}
              <div className="hidden md:block overflow-x-auto rounded-lg border">
                <table className="w-full text-left text-xs">
                  <thead className="bg-muted/50 text-[11px] font-semibold text-muted-foreground uppercase border-b">
                    <tr>
                      <th className="px-4 py-2.5">Student Name</th>
                      <th className="px-3 py-2.5">Status</th>
                      <th className="px-3 py-2.5">Mastery (p)</th>
                      <th className="px-3 py-2.5">Time</th>
                      <th className="px-4 py-2.5">Detected Misconception / Evidence</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {studentsForSelectedConcept.map(st => {
                      const rec = st.masteryRecord;
                      const isGap = rec.status === 'confirmed' || rec.status === 'suspected';
                      return (
                        <tr key={st.id} className="hover:bg-muted/30 transition-colors">
                          <td className="px-4 py-3">
                            <div className="font-semibold text-foreground">{st.name}</div>
                            <div className="text-[11px] text-muted-foreground font-mono">{st.email}</div>
                          </td>
                          <td className="px-3 py-3">
                            <span
                              className={cn(
                                'rounded px-2 py-0.5 text-[10px] font-bold uppercase',
                                rec.status === 'confirmed'
                                  ? 'bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300'
                                  : rec.status === 'suspected'
                                  ? 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300'
                                  : 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300'
                              )}
                            >
                              {rec.status === 'confirmed' ? 'Confirmed Gap' : rec.status === 'suspected' ? 'Suspected Gap' : 'Mastered'}
                            </span>
                          </td>
                          <td className="px-3 py-3 font-mono font-bold">
                            {Math.round(rec.p * 100)}%
                          </td>
                          <td className="px-3 py-3 text-muted-foreground">
                            {rec.responseMs ? `${(rec.responseMs / 1000).toFixed(1)}s` : '12.4s'}
                          </td>
                          <td className="px-4 py-3 text-muted-foreground">
                            {rec.misconception ? (
                              <div className="space-y-0.5">
                                <span className="text-foreground font-medium">{rec.misconception}</span>
                                {rec.chosenOption && (
                                  <div className="text-[11px] text-rose-600 dark:text-rose-400">
                                    Selected Distractor: Option ({rec.chosenOption})
                                  </div>
                                )}
                              </div>
                            ) : (
                              <span className="text-emerald-600 dark:text-emerald-400 font-medium">Demonstrated core mastery</span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Mobile Card Roster View */}
              <div className="md:hidden space-y-2.5">
                {studentsForSelectedConcept.map(st => {
                  const rec = st.masteryRecord;
                  const isGap = rec.status === 'confirmed' || rec.status === 'suspected';
                  return (
                    <div key={st.id} className="rounded-lg border bg-card p-3 space-y-1.5 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-foreground">{st.name}</span>
                        <span
                          className={cn(
                            'rounded px-1.5 py-0.5 text-[10px] font-bold uppercase',
                            rec.status === 'confirmed'
                              ? 'bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300'
                              : rec.status === 'suspected'
                              ? 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300'
                              : 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300'
                          )}
                        >
                          {rec.status === 'confirmed' ? 'Gap' : rec.status === 'suspected' ? 'Suspected' : 'Mastered'}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-[11px] text-muted-foreground">
                        <span>{st.email}</span>
                        <span className="font-mono font-bold text-foreground">{Math.round(rec.p * 100)}% Mastery</span>
                      </div>
                      {rec.misconception && (
                        <div className="rounded bg-muted/50 p-2 text-[11px] text-muted-foreground">
                          <strong className="text-foreground">Error Pattern:</strong> {rec.misconception}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Tab 2: Diagnostic Question Evidence Breakdown */}
          {rosterTab === 'evidence' && (
            <div className="p-4 sm:p-5 space-y-4">
              <div className="rounded-lg border bg-background p-4 space-y-2">
                <span className="text-xs font-mono font-bold text-primary">QUESTION BANK ITEM &middot; DIAGNOSTIC PROMPT</span>
                <p className="text-sm font-semibold">
                  Which statement is strictly true regarding a functional dependency X &rarr; Y on relation schema R?
                </p>
                <div className="grid gap-2 sm:grid-cols-2 pt-2 text-xs">
                  <div className="rounded border p-2 bg-muted/30">
                    <span className="font-bold">A)</span> Holds only for the current state of table R.
                    <span className="block text-[11px] text-rose-600 font-semibold mt-0.5">Top distractor (42% chosen)</span>
                  </div>
                  <div className="rounded border p-2 bg-emerald-500/10 border-emerald-500/30">
                    <span className="font-bold text-emerald-700 dark:text-emerald-400">B)</span> Must hold for all legally possible relation states r(R).
                    <span className="block text-[11px] text-emerald-600 font-semibold mt-0.5">Correct Definition</span>
                  </div>
                  <div className="rounded border p-2 bg-muted/30">
                    <span className="font-bold">C)</span> Implies that Y values uniquely determine X values.
                    <span className="block text-[11px] text-rose-600 font-semibold mt-0.5">Distractor: Direction inversion (22%)</span>
                  </div>
                  <div className="rounded border p-2 bg-muted/30">
                    <span className="font-bold">D)</span> Can be violated if a candidate key exists.
                    <span className="block text-[11px] text-muted-foreground mt-0.5">Distractor (6%)</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 5. Step 5: Plan Targeted Teaching or Revision */}
          <div className="border-t bg-gradient-to-b from-muted/20 to-muted/50 p-4 sm:p-6 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <span className="flex size-5 items-center justify-center rounded-full bg-primary text-[10px] font-bold text-white">5</span>
                  <h3 className="text-base font-bold">Targeted Teaching &amp; Revision Plan</h3>
                  <span className="rounded bg-primary/10 px-2 py-0.5 text-xs font-semibold text-primary">
                    Actionable Lecture Plan
                  </span>
                </div>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Algorithmic remediation agenda generated from class prerequisite bottlenecks.
                </p>
              </div>

              <Button
                size="sm"
                onClick={handleCopyPlan}
                className="gap-1.5 text-xs font-semibold self-start sm:self-auto"
              >
                {isCopied ? <Check className="size-3.5 text-emerald-400" /> : <Copy className="size-3.5" />}
                {isCopied ? 'Plan Copied!' : 'Copy Lecture Plan'}
              </Button>
            </div>

            {/* Targeted Lesson Agenda */}
            <div className="grid gap-3 sm:grid-cols-3 text-xs">
              <div className="rounded-xl border bg-card p-3.5 space-y-1.5">
                <div className="flex items-center gap-1.5 font-bold text-primary">
                  <Clock className="size-3.5" />
                  Segment 1 (10 Mins)
                </div>
                <p className="font-semibold text-foreground">Foundation Revisit</p>
                <p className="text-muted-foreground leading-relaxed">
                  Review <strong>Candidate Keys (D03)</strong> and superkeys. Clarify that functional dependencies apply across all valid states, not just the currently populated tuples.
                </p>
              </div>

              <div className="rounded-xl border bg-card p-3.5 space-y-1.5">
                <div className="flex items-center gap-1.5 font-bold text-rose-600 dark:text-rose-400">
                  <Clock className="size-3.5" />
                  Segment 2 (20 Mins)
                </div>
                <p className="font-semibold text-foreground">Interactive Derivation Drill</p>
                <p className="text-muted-foreground leading-relaxed">
                  Demonstrate Armstrong’s Axioms (Reflexivity, Augmentation, Transitivity). Have students compute attribute closure X+ on the whiteboard for a sample relation R(A,B,C,D).
                </p>
              </div>

              <div className="rounded-xl border bg-card p-3.5 space-y-1.5">
                <div className="flex items-center gap-1.5 font-bold text-emerald-600 dark:text-emerald-400">
                  <Clock className="size-3.5" />
                  Segment 3 (15 Mins)
                </div>
                <p className="font-semibold text-foreground">Formative Retest Check</p>
                <p className="text-muted-foreground leading-relaxed">
                  Present a 3-question live polling quiz. Guide students to identify redundant FDs and verify minimal covers before advancing to Normalization (D13).
                </p>
              </div>
            </div>

            {/* Pedagogical Prerequisite Alert */}
            <div className="rounded-lg border border-primary/20 bg-primary/5 p-3 text-xs flex items-start gap-2.5">
              <Lightbulb className="size-4 text-primary shrink-0 mt-0.5" />
              <p className="text-muted-foreground leading-relaxed">
                <strong>Pedagogical Insight:</strong> 64% of the cohort failed D12 because they bypassed prerequisite candidate key determination. Do not introduce <strong>Normalization (D13)</strong> or <strong>BCNF (D14)</strong> until this revision module has been delivered.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Algorithmic Simulation Benchmark */}
      <div className="rounded-xl border bg-card p-4 sm:p-6 shadow-sm space-y-3">
        <div>
          <h3 className="text-base sm:text-lg font-bold tracking-tight">
            Diagnostic Accuracy &amp; Efficiency Benchmark
          </h3>
          <p className="text-xs text-muted-foreground">
            Comparison of MIND MESH Prerequisite DAG vs traditional linear assessment models (500 synthetic learner runs).
          </p>
        </div>

        <div className="grid gap-3 grid-cols-1 sm:grid-cols-3">
          {benchmarks.map(b => (
            <div key={b.strategy} className="rounded-lg border p-3.5 space-y-2 bg-muted/20">
              <p className="text-xs font-semibold text-foreground">{b.strategy}</p>
              <div className="space-y-1 text-xs text-muted-foreground">
                <div className="flex justify-between">
                  <span>Questions to Diagnose:</span>
                  <strong className="text-foreground">{b.avg_questions_to_diagnose}</strong>
                </div>
                <div className="flex justify-between">
                  <span>Diagnostic Accuracy:</span>
                  <strong className="text-foreground">{b.diagnostic_accuracy_pct}%</strong>
                </div>
                <div className="flex justify-between">
                  <span>Root Gap Discovery:</span>
                  <strong className="text-foreground">{b.root_gap_discovery_rate}%</strong>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
