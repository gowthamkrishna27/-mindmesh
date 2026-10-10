'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Target, ArrowRight, BookOpen, Network, CheckCircle2, RotateCcw } from 'lucide-react';
import { ResponseRecord, Concept } from '@/lib/types';
import { fetchConcepts } from '@/lib/apiClient';

interface StudentDashboardProps {
  userName: string;
  selectedSubject: string;
  onSelectSubject: (subject: string) => void;
  onStartQuiz: () => void;
  onViewDiagnosis: () => void;
  onViewRoadmap?: () => void;
  onRetest: () => void;
  masteryCount: number;
  gapCount: number;
  rootGapId: string;
  responses: ResponseRecord[];
}

export function StudentDashboard({
  userName,
  onStartQuiz,
  onViewDiagnosis,
  onViewRoadmap,
  onRetest,
  masteryCount,
  gapCount,
  rootGapId,
}: StudentDashboardProps) {
  const [concepts, setConcepts] = useState<Concept[]>([]);

  useEffect(() => {
    fetchConcepts().then(c => {
      if (c && c.length > 0) setConcepts(c);
    });
  }, []);

  const totalConcepts = concepts.length > 0 ? concepts.length : 18;
  const currentRootConcept = concepts.find(c => c.id === rootGapId);
  const targetBlockedConcept = concepts.find(c => c.prerequisites?.includes(rootGapId));

  const hasGaps = gapCount > 0 && !!rootGapId;

  let rootTitle = 'Take Diagnostic Assessment';
  let rootDescription =
    'Diagnose your database management knowledge graph across 18 concepts. Mind Mesh will pinpoint your prerequisite gaps and build a customized recovery roadmap.';
  let cardTag = 'GET STARTED';
  let cardSubTag = 'Diagnostic Assessment';

  if (hasGaps && currentRootConcept) {
    cardTag = 'RECOMMENDED NEXT STEP';
    cardSubTag = 'Root Gap';
    rootTitle = `${currentRootConcept.name} (${currentRootConcept.id})`;
    rootDescription = targetBlockedConcept
      ? `Missing foundation for ${targetBlockedConcept.name} (${targetBlockedConcept.id}). Study this prerequisite first to unlock database design mastery.`
      : currentRootConcept.description ||
        `Identified as foundational root gap. Study this prerequisite first to unlock downstream database concepts.`;
  } else if (gapCount === 0 && masteryCount > 0) {
    cardTag = 'STATUS UPDATE';
    cardSubTag = 'Mastery Verified';
    rootTitle = 'All Prerequisites Mastered';
    rootDescription =
      'All core prerequisites mastered! Ready to take a retest or explore advanced database topics.';
  }

  return (
    <div className="space-y-8 max-w-3xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
            Welcome, {userName}
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Database Management Systems · {totalConcepts} concepts
          </p>
        </div>
        {hasGaps || masteryCount > 0 ? (
          <Button onClick={onViewDiagnosis} className="sm:self-start">
            <Network className="mr-2 size-4" />
            View Diagnostic Report
          </Button>
        ) : (
          <Button onClick={onStartQuiz} className="sm:self-start">
            <Target className="mr-2 size-4" />
            Take Diagnostic Quiz
          </Button>
        )}
      </div>

      {/* Minimal Stat Strip */}
      <div className="grid grid-cols-3 gap-6 border-y py-5">
        <div>
          <p className="text-2xl font-bold text-foreground">{masteryCount}</p>
          <p className="text-xs text-muted-foreground mt-0.5">Mastered</p>
        </div>
        <div>
          <p className="text-2xl font-bold text-rose-600 dark:text-rose-400">{gapCount}</p>
          <p className="text-xs text-muted-foreground mt-0.5">
            Active Gaps {hasGaps ? `(Root: ${rootGapId})` : gapCount === 0 && masteryCount > 0 ? '(0 Gaps)' : '(Pending Quiz)'}
          </p>
        </div>
        <div>
          <p className="text-2xl font-bold text-foreground">{totalConcepts}</p>
          <p className="text-xs text-muted-foreground mt-0.5">Total Concepts</p>
        </div>
      </div>

      {/* Single Clean Focus Card */}
      <div className="rounded-lg border bg-card p-6 space-y-4 shadow-sm">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-rose-600 dark:text-rose-400">
            {cardTag}
          </span>
          <span className="text-xs text-muted-foreground">{cardSubTag}</span>
        </div>

        <div>
          <h2 className="text-xl font-bold">{rootTitle}</h2>
          <p className="mt-1.5 text-sm text-muted-foreground leading-relaxed">
            {rootDescription}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 pt-2">
          {hasGaps ? (
            <>
              <Button onClick={onViewDiagnosis} className="w-full sm:w-auto">
                <Network className="mr-2 size-4" />
                View Diagnosis &amp; Graph
                <ArrowRight className="ml-2 size-4" />
              </Button>
              <Button variant="outline" onClick={onRetest} className="w-full sm:w-auto">
                <RotateCcw className="mr-2 size-4" />
                Retest Concepts
              </Button>
            </>
          ) : gapCount === 0 && masteryCount > 0 ? (
            <>
              <Button onClick={onRetest} className="w-full sm:w-auto">
                <CheckCircle2 className="mr-2 size-4" />
                Take Certification Retest
                <ArrowRight className="ml-2 size-4" />
              </Button>
              <Button variant="outline" onClick={onViewDiagnosis} className="w-full sm:w-auto">
                <Network className="mr-2 size-4" />
                View Concept Graph
              </Button>
            </>
          ) : (
            <>
              <Button onClick={onStartQuiz} className="w-full sm:w-auto">
                <Target className="mr-2 size-4" />
                Start Diagnostic Quiz
                <ArrowRight className="ml-2 size-4" />
              </Button>
              <Button variant="outline" onClick={onViewDiagnosis} className="w-full sm:w-auto">
                <Network className="mr-2 size-4" />
                Preview Concept Graph
              </Button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
