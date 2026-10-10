'use client';

import React, { useState } from 'react';
import { LearningPathItem, Concept } from '@/lib/types';

const DEFAULT_LEARNING_PATH: LearningPathItem[] = [
  {
    id: "PATH-1",
    position: 1,
    concept_id: "D12",
    concept_name: "Functional Dependencies",
    rationale: "Identified as Root Gap: Direct prerequisite of Normalization (D13).",
    completed: false,
    estimated_mins: 8,
    key_takeaways: [
      "X -> Y holds if whenever two tuples agree on attributes X, they agree on Y.",
      "Armstrong's Axioms: Reflexivity, Augmentation, Transitivity.",
      "Attribute Closure (X+) collects all attributes functionally determined by X."
    ],
    practice_prompt: "Given R(A,B,C,D,E) with FDs: A -> B, BC -> D, D -> E. Compute closure of {A, C}.",
    practice_solution: "{A, C}+ = {A, B, C, D, E}. Thus {A, C} is a candidate key!"
  },
  {
    id: "PATH-2",
    position: 2,
    concept_id: "D13",
    concept_name: "Normalization (1NF to 3NF)",
    rationale: "Target Concept: Re-learn Normalization now that Functional Dependencies foundation is fortified.",
    completed: false,
    estimated_mins: 10,
    key_takeaways: [
      "1NF: Atomic domain values, no repeating groups.",
      "2NF: In 1NF and no non-prime attribute partially dependent on candidate key.",
      "3NF: In 2NF and no non-prime attribute transitively dependent on candidate key."
    ],
    practice_prompt: "Given R(CourseID, Instructor, Office) with CourseID -> Instructor, Instructor -> Office. What normal form is violated?",
    practice_solution: "Violates 3NF due to transitive dependency Instructor -> Office."
  }
];
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import {
  CheckCircle2,
  BookOpen,
  ArrowRight,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Layers,
  HelpCircle,
  RotateCcw,
  Video,
  FileText,
  Wrench,
  Sparkles,
  Link as LinkIcon,
  AlertCircle
} from 'lucide-react';

interface LearningRoadmapProps {
  onStartRetest: () => void;
  rootGapId?: string;
}

type DepthLevel = 'basic' | 'intermediate' | 'advanced';

interface SourceLink {
  title: string;
  url: string;
  summary: string;
  type: 'Guide' | 'Video' | 'Interactive Tool' | 'Cheatsheet';
  estTime: string;
  isPrerequisite?: boolean;
}

const SUGGESTED_SOURCE_LINKS: Record<string, SourceLink[]> = {
  D12: [
    {
      title: "Stanford CS145: Functional Dependencies & Schema Design",
      url: "https://web.stanford.edu/class/cs145/",
      summary: "University lecture notes on Armstrong's axioms, closure algorithm, and minimal covers.",
      type: "Guide",
      estTime: "12 min read",
      isPrerequisite: true
    },
    {
      title: "GeeksforGeeks: Attribute Closure & Candidate Keys",
      url: "https://www.geeksforgeeks.org/finding-attribute-closure-and-candidate-keys-using-functional-dependencies/",
      summary: "Step-by-step algorithms and solved gate problems for computing {X}+.",
      type: "Cheatsheet",
      estTime: "8 min read",
      isPrerequisite: true
    },
    {
      title: "NPTEL DBMS Video: Armstrong Axioms & FD Derivation",
      url: "https://nptel.ac.in/courses/106106093",
      summary: "Visual lecture series demonstrating reflexivity, augmentation, and transitivity rules.",
      type: "Video",
      estTime: "18 min watch",
      isPrerequisite: true
    },
    {
      title: "RelaX: Interactive FD & Closure Calculator",
      url: "https://dbis-uibk.github.io/relax/",
      summary: "Online sandbox to input relations, test FDs, and compute attribute closures.",
      type: "Interactive Tool",
      estTime: "Hands-on",
      isPrerequisite: true
    }
  ],
  D13: [
    {
      title: "MIT 6.830: Database Normalization (1NF through 3NF)",
      url: "https://ocw.mit.edu/courses/6-830-database-systems-fall-2010/",
      summary: "In-depth lecture slides on eliminating insertion, deletion, and update anomalies.",
      type: "Guide",
      estTime: "15 min read"
    },
    {
      title: "GeeksforGeeks: Normal Forms in DBMS with Examples",
      url: "https://www.geeksforgeeks.org/introduction-of-database-normalization/",
      summary: "Concise summary of 1NF atomic domains, 2NF partial dependencies, and 3NF transitive dependencies.",
      type: "Cheatsheet",
      estTime: "10 min read"
    },
    {
      title: "RelaX: Normal Form Tester & Decomposition Visualizer",
      url: "https://dbis-uibk.github.io/relax/calc/normal-forms",
      summary: "Interactive web calculator to test whether a decomposed relation satisfies 2NF or 3NF.",
      type: "Interactive Tool",
      estTime: "Hands-on"
    }
  ],
  D03: [
    {
      title: "GeeksforGeeks: Candidate, Super, Primary, and Foreign Keys",
      url: "https://www.geeksforgeeks.org/types-of-keys-in-relational-model-candidate-super-primary-alternate-and-foreign/",
      summary: "Foundational definitions of minimal uniqueness and referential integrity constraints.",
      type: "Guide",
      estTime: "7 min read",
      isPrerequisite: true
    },
    {
      title: "W3Schools: SQL Primary & Foreign Keys Explained",
      url: "https://www.w3schools.com/sql/sql_primarykey.asp",
      summary: "Practical syntax and referential integrity rules across modern relational databases.",
      type: "Cheatsheet",
      estTime: "5 min read",
      isPrerequisite: true
    }
  ]
};

import { fetchConcepts } from '@/lib/apiClient';

export function LearningRoadmap({ onStartRetest, rootGapId }: LearningRoadmapProps) {
  const [items, setItems] = useState<LearningPathItem[]>(DEFAULT_LEARNING_PATH);
  const [activeConceptId, setActiveConceptId] = useState<string>(rootGapId || 'D12');
  const [depth, setDepth] = useState<DepthLevel>('intermediate');
  const [showSolution, setShowSolution] = useState<Record<string, boolean>>({});
  const [concepts, setConcepts] = useState<Concept[]>([]);

  React.useEffect(() => {
    if (rootGapId) setActiveConceptId(rootGapId);
  }, [rootGapId]);

  React.useEffect(() => {
    fetchConcepts().then(c => {
      if (c && c.length > 0) setConcepts(c);
    });
  }, []);

  const toggleComplete = (id: string) => {
    setItems(list =>
      list.map(item => (item.id === id ? { ...item, completed: !item.completed } : item))
    );
  };

  const activeItem = items.find(i => i.concept_id === activeConceptId) || items[0];
  const activeConceptDetails = concepts.find(c => c.id === activeItem.concept_id);
  const sourceLinks = SUGGESTED_SOURCE_LINKS[activeItem.concept_id] || [];

  // Prerequisite concept source links (if active concept has prereqs, e.g. D12 has prereq D03)
  const prereqConceptIds = activeConceptDetails?.prerequisites || [];

  const getSourceIcon = (type: SourceLink['type']) => {
    switch (type) {
      case 'Video':
        return <Video className="size-3.5 text-rose-500" />;
      case 'Interactive Tool':
        return <Wrench className="size-3.5 text-blue-500" />;
      case 'Cheatsheet':
        return <FileText className="size-3.5 text-amber-500" />;
      default:
        return <BookOpen className="size-3.5 text-emerald-500" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
              Study Path &amp; Recommended Links
            </span>
            <h1 className="text-2xl font-bold tracking-tight">Sources</h1>
            <p className="mt-1 text-xs text-muted-foreground">
              Review suggested source links for missing prerequisites to fix gaps in topological order.
            </p>
          </div>
          <Button onClick={onStartRetest} className="shadow-sm">
            <RotateCcw className="mr-1.5 size-4" />
            Take Retest Verification
            <ArrowRight className="ml-1.5 size-4" />
          </Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_1.45fr]">
        {/* Left Column: Ordered Concept List */}
        <div className="space-y-3">
          <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Ordered Study Sequence
          </p>

          <div className="space-y-3">
            {items.map((item, idx) => {
              const isSelected = item.concept_id === activeConceptId;
              const isPrereqGap = item.position === 1;
              return (
                <div
                  key={item.id}
                  onClick={() => setActiveConceptId(item.concept_id)}
                  className={cn(
                    'cursor-pointer rounded-lg border p-4 transition-all',
                    isSelected
                      ? 'border-primary bg-primary/5 ring-1 ring-primary'
                      : 'border-border bg-card hover:bg-muted/50'
                  )}
                >
                  <div className="flex items-start gap-3">
                    <button
                      type="button"
                      onClick={e => {
                        e.stopPropagation();
                        toggleComplete(item.id);
                      }}
                      className={cn(
                        'mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full border transition-colors',
                        item.completed
                          ? 'border-emerald-500 bg-emerald-500 text-white'
                          : 'border-muted-foreground/30 hover:border-primary'
                      )}
                      aria-label={item.completed ? 'Mark incomplete' : 'Mark complete'}
                    >
                      {item.completed ? (
                        <CheckCircle2 className="size-3.5" />
                      ) : (
                        <span className="text-[10px] font-semibold">{idx + 1}</span>
                      )}
                    </button>

                    <div className="min-w-0 flex-1">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5">
                          <span className="text-xs font-bold text-primary">
                            {item.concept_id}
                          </span>
                          {isPrereqGap && (
                            <span className="rounded bg-rose-500/10 px-1.5 py-0.2 text-[10px] font-bold text-rose-600 dark:text-rose-400">
                              Suggested Prerequisite
                            </span>
                          )}
                        </div>
                        <span className="text-[11px] text-muted-foreground">
                          {item.estimated_mins} mins
                        </span>
                      </div>
                      <h3
                        className={cn(
                          'mt-1 font-semibold text-sm',
                          item.completed && 'text-muted-foreground line-through'
                        )}
                      >
                        {item.concept_name}
                      </h3>
                      <p className="mt-1 text-xs text-muted-foreground line-clamp-2">
                        {item.rationale}
                      </p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Progress overview */}
          <div className="rounded-lg border bg-muted/30 p-3.5 text-xs text-muted-foreground">
            <div className="flex items-center justify-between font-medium text-foreground">
              <span>Path Progress</span>
              <span>
                {items.filter(i => i.completed).length} of {items.length} completed
              </span>
            </div>
            <div className="mt-2 h-1.5 w-full rounded-full bg-muted overflow-hidden">
              <div
                className="h-full bg-emerald-500 transition-all duration-300"
                style={{
                  width: `${(items.filter(i => i.completed).length / items.length) * 100}%`
                }}
              />
            </div>
          </div>
        </div>

        {/* Right Column: Active Concept Details & Suggested Sources */}
        <div className="rounded-lg border bg-card p-5 sm:p-6 shadow-sm space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b pb-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-primary">{activeItem.concept_id}</span>
                {activeItem.position === 1 && (
                  <span className="rounded bg-rose-500/10 px-1.5 py-0.5 text-[10px] font-bold text-rose-600 dark:text-rose-400">
                    Root Prerequisite Blocker
                  </span>
                )}
              </div>
              <h2 className="text-xl font-bold mt-0.5">{activeItem.concept_name}</h2>
            </div>

            {/* Depth Selector */}
            <div className="flex items-center rounded-lg border bg-muted p-0.5 text-xs">
              {(['basic', 'intermediate', 'advanced'] as DepthLevel[]).map(d => (
                <button
                  key={d}
                  onClick={() => setDepth(d)}
                  className={cn(
                    'rounded-md px-2.5 py-1 font-medium capitalize transition-all',
                    depth === d
                      ? 'bg-card text-foreground shadow-sm'
                      : 'text-muted-foreground hover:text-foreground'
                  )}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>

          {/* Suggested Source Links Section */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5">
                <LinkIcon className="size-3.5 text-primary" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                  Suggested Source Links
                </h3>
              </div>
              <span className="text-[11px] text-muted-foreground">
                {sourceLinks.length} verified references
              </span>
            </div>

            <div className="grid gap-2.5">
              {sourceLinks.map((src, i) => (
                <a
                  key={i}
                  href={src.url}
                  target="_blank"
                  rel="noreferrer"
                  className="group flex items-start justify-between rounded-lg border bg-card p-3 text-xs transition-all hover:border-primary/50 hover:bg-muted/30"
                >
                  <div className="space-y-1 pr-3">
                    <div className="flex items-center gap-2">
                      <span className="flex items-center gap-1 font-semibold text-foreground group-hover:text-primary transition-colors">
                        {getSourceIcon(src.type)}
                        {src.title}
                      </span>
                      <span className="rounded bg-muted px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
                        {src.type}
                      </span>
                      <span className="text-[10px] text-muted-foreground">
                        {src.estTime}
                      </span>
                    </div>
                    <p className="text-muted-foreground leading-relaxed text-[11px]">
                      {src.summary}
                    </p>
                  </div>
                  <ExternalLink className="size-3.5 text-muted-foreground shrink-0 mt-1 group-hover:text-primary transition-colors" />
                </a>
              ))}
            </div>
          </div>

          {/* If there are foundational prerequisites of this prerequisite (e.g., D03 Keys for D12) */}
          {prereqConceptIds.length > 0 && (
            <div className="rounded-lg border bg-muted/20 p-3.5 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-foreground flex items-center gap-1.5">
                  <BookOpen className="size-3.5 text-primary" />
                  Prerequisite Source Links for {prereqConceptIds.join(', ')}
                </span>
                <span className="text-[10px] text-muted-foreground">Upstream foundation</span>
              </div>
              <p className="text-[11px] text-muted-foreground leading-relaxed">
                Need to review keys before solving functional dependencies?
              </p>
              <div className="space-y-1.5 pt-1">
                {(SUGGESTED_SOURCE_LINKS['D03'] || []).map((pSrc, pIdx) => (
                  <a
                    key={pIdx}
                    href={pSrc.url}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center justify-between rounded border bg-card px-2.5 py-1.5 text-[11px] hover:border-primary transition-colors"
                  >
                    <span className="font-medium text-foreground truncate pr-2">
                      {pSrc.title}
                    </span>
                    <ExternalLink className="size-3 text-muted-foreground shrink-0" />
                  </a>
                ))}
              </div>
            </div>
          )}

          {/* Lesson Content Takeaways */}
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5 mb-2.5">
              <Layers className="size-3.5" />
              Lesson Summary ({depth} depth)
            </h3>
            <div className="space-y-1.5">
              {activeItem.key_takeaways.map((takeaway, i) => (
                <div key={i} className="flex items-start gap-2 text-xs leading-relaxed text-muted-foreground">
                  <span className="mt-1 size-1 shrink-0 rounded-full bg-primary" />
                  <span className="text-foreground">{takeaway}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Practice Problem */}
          <div className="rounded-md border bg-muted/20 p-3.5 space-y-2.5">
            <div className="flex items-center justify-between text-xs font-semibold">
              <span className="flex items-center gap-1 text-primary">
                <HelpCircle className="size-3.5" />
                Practice Problem
              </span>
              <button
                onClick={() =>
                  setShowSolution(s => ({ ...s, [activeItem.id]: !s[activeItem.id] }))
                }
                className="text-[11px] text-muted-foreground hover:text-foreground flex items-center gap-1"
              >
                {showSolution[activeItem.id] ? 'Hide Solution' : 'Reveal Solution'}
                {showSolution[activeItem.id] ? (
                  <ChevronUp className="size-3" />
                ) : (
                  <ChevronDown className="size-3" />
                )}
              </button>
            </div>
            <p className="text-xs font-medium leading-relaxed">{activeItem.practice_prompt}</p>

            {showSolution[activeItem.id] && (
              <div className="rounded border bg-emerald-500/10 p-2.5 text-[11px] text-emerald-800 dark:text-emerald-300 leading-relaxed">
                <strong>Solution:</strong> {activeItem.practice_solution}
              </div>
            )}
          </div>

          {/* Bottom Action Footer */}
          <div className="flex items-center justify-between pt-3 border-t">
            <Button
              variant="outline"
              size="sm"
              onClick={() => toggleComplete(activeItem.id)}
            >
              {activeItem.completed ? 'Mark Incomplete' : 'Mark Concept Complete'}
            </Button>
            <Button size="sm" onClick={onStartRetest}>
              Proceed to Retest
              <ArrowRight className="ml-1.5 size-3.5" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
