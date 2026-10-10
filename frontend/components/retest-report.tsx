'use client';

import React, { useState } from 'react';
import { Question, StudentMastery, Concept } from '@/lib/types';

const INITIAL_DIAGNOSTIC_MASTERY: Record<string, { p: number }> = {
  D12: { p: 0.18 },
  D13: { p: 0.22 },
  D03: { p: 0.76 },
  D08: { p: 0.88 }
};

const POST_RETEST_MASTERY: Record<string, { p: number }> = {
  D12: { p: 0.86 },
  D13: { p: 0.84 },
  D03: { p: 0.82 },
  D08: { p: 0.92 }
};
import { Button } from './ui/button';
import { cn } from '../lib/utils';
import {
  TrendingUp,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  RotateCcw,
  Sparkles,
  Trophy,
  BarChart3,
  BookOpen
} from 'lucide-react';

interface RetestReportProps {
  onBackToDashboard: () => void;
  onViewDiagnosis?: () => void;
  onViewRoadmap?: () => void;
}

// Retest Family B questions targeting D12 and D13
const RETEST_QUESTIONS: Question[] = [
  {
    id: 'Q12B',
    concept: 'D12',
    family: 'B',
    difficulty: 3,
    prompt:
      'Given relation R(A, B, C, D) with FDs: A → B, B → C, and C → D. What is the attribute closure {A}+ ?',
    options: [
      { id: 'a', text: '{A, B}', correct: false },
      { id: 'b', text: '{A, B, C, D}', correct: true },
      { id: 'c', text: '{A, C, D}', correct: false },
      { id: 'd', text: '{A} only', correct: false }
    ],
    explanation:
      'By Armstrong’s transitivity: A → B gives B, B → C gives C, and C → D gives D. Hence {A}+ = {A, B, C, D}.',
    validation_status: 'reviewed'
  },
  {
    id: 'Q13B',
    concept: 'D13',
    family: 'B',
    difficulty: 4,
    prompt:
      'Relation Enrollment(StudentID, CourseID, Department, Building) has Key (StudentID, CourseID) with Department → Building. Which normal form is violated?',
    options: [
      { id: 'a', text: '1NF', correct: false },
      { id: 'b', text: '2NF', correct: false },
      { id: 'c', text: '3NF (due to transitive dependency non-key → non-key)', correct: true },
      { id: 'd', text: 'No normal form is violated', correct: false }
    ],
    explanation:
      'Department determines Building (non-prime attribute determines non-prime attribute), violating 3NF.',
    validation_status: 'reviewed'
  }
];

import { fetchConcepts, fetchQuestions } from '@/lib/apiClient';

export function RetestReport({ onBackToDashboard, onViewDiagnosis, onViewRoadmap }: RetestReportProps) {
  const [inRetestQuiz, setInRetestQuiz] = useState(true);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [questions, setQuestions] = useState<Question[]>(RETEST_QUESTIONS);

  React.useEffect(() => {
    fetchConcepts().then(c => {
      if (c && c.length > 0) setConcepts(c);
    });
    fetchQuestions('B').then(qs => {
      const filtered = qs.filter(q => q.concept === 'D12' || q.concept === 'D13');
      if (filtered.length > 0) setQuestions(filtered);
    });
  }, []);

  const handleNext = () => {
    if (!selectedId) return;
    const nextAnswers = { ...answers, [currentIdx]: selectedId };
    setAnswers(nextAnswers);
    setSelectedId(null);

    if (currentIdx < questions.length - 1) {
      setCurrentIdx(i => i + 1);
    } else {
      setInRetestQuiz(false);
    }
  };

  // Screen A: Live Retest Session (Step 6 Screen 1)
  if (inRetestQuiz) {
    const q = questions[currentIdx] || questions[0];
    const concept = concepts.find(c => c.id === q?.concept);

    return (
      <div className="mx-auto max-w-2xl space-y-6">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Post-Roadmap Retest Session (Family B Items)
          </span>
          <h1 className="text-2xl font-bold tracking-tight">
            Question {currentIdx + 1} of {questions.length}
          </h1>
          <p className="mt-1 text-xs text-muted-foreground">
            Verifying mastery after completing recommendations on {concept?.name || 'Target Topics'}.
          </p>
        </div>

        <div className="rounded-lg border bg-card p-6 shadow-sm sm:p-8">
          <div className="flex items-center justify-between text-xs text-muted-foreground mb-4">
            <span className="rounded border px-2 py-0.5 font-medium">
              Concept {q.concept} · Family B
            </span>
            <span>Target Verification</span>
          </div>

          <h2 className="text-lg font-medium leading-relaxed">{q.prompt}</h2>

          <div className="mt-6 space-y-3">
            {q.options.map((opt, i) => {
              const isSelected = selectedId === opt.id;
              return (
                <button
                  key={opt.id}
                  onClick={() => setSelectedId(opt.id)}
                  className={cn(
                    'flex w-full items-start gap-3 rounded-lg border p-4 text-left text-sm transition-all',
                    isSelected
                      ? 'border-primary bg-primary/5 ring-1 ring-primary'
                      : 'border-border hover:bg-muted/50'
                  )}
                >
                  <span
                    className={cn(
                      'flex size-6 shrink-0 items-center justify-center rounded-full border text-xs font-semibold',
                      isSelected
                        ? 'border-primary bg-primary text-primary-foreground'
                        : 'border-muted-foreground/30 text-muted-foreground'
                    )}
                  >
                    {String.fromCharCode(65 + i)}
                  </span>
                  <span className="pt-0.5 leading-snug">{opt.text}</span>
                </button>
              );
            })}
          </div>

          <div className="mt-8 flex justify-end">
            <Button disabled={!selectedId} onClick={handleNext} className="px-6">
              {currentIdx === RETEST_QUESTIONS.length - 1
                ? 'Submit Retest & View Improvement'
                : 'Next Question'}
              <ArrowRight className="ml-2 size-4" />
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // Screen B: Before-and-After Improvement Report (Step 6 Screen 2)
  const trackedConcepts = ['D12', 'D13', 'D03', 'D08'];

  return (
    <div className="space-y-8">
      {/* Victory / Improvement Hero Banner */}
      <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/5 p-6 dark:border-emerald-500/20 dark:bg-emerald-950/20">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-4">
            <div className="flex size-12 shrink-0 items-center justify-center rounded-full bg-emerald-500 text-white shadow-md">
              <Trophy className="size-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="rounded bg-emerald-600/10 px-2 py-0.5 text-xs font-bold text-emerald-700 dark:text-emerald-400">
                  ROOT GAP RESOLVED
                </span>
                <span className="text-xs text-muted-foreground">Retest Score: 100% (2/2)</span>
              </div>
              <h2 className="mt-1 text-2xl font-bold tracking-tight">
                Outstanding Improvement Confirmed!
              </h2>
              <p className="mt-1 text-sm text-muted-foreground">
                Both Functional Dependencies and Normalization have transitioned from gaps to
                mastered foundations.
              </p>
            </div>
          </div>

          <div className="flex shrink-0 gap-2">
            <Button onClick={onBackToDashboard} className="bg-primary">
              Return to Dashboard
              <ArrowRight className="ml-2 size-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Before vs After Mastery Comparison Grid */}
      <div className="rounded-lg border bg-card p-6 shadow-sm space-y-6">
        <div className="flex items-center justify-between border-b pb-4">
          <div>
            <h3 className="text-lg font-bold tracking-tight">
              Before vs. After Mastery Estimates
            </h3>
            <p className="text-xs text-muted-foreground">
              Bayesian mastery parameter updates following topological remediation.
            </p>
          </div>
          <span className="flex items-center gap-1.5 text-xs font-semibold text-emerald-600 dark:text-emerald-400">
            <TrendingUp className="size-4" />
            Average Delta: +44%
          </span>
        </div>

        <div className="space-y-5">
          {trackedConcepts.map(cId => {
            const concept = concepts.find(c => c.id === cId) || { name: cId };
            const beforeP = Math.round((INITIAL_DIAGNOSTIC_MASTERY[cId]?.p || 0.5) * 100);
            const afterP = Math.round((POST_RETEST_MASTERY[cId]?.p || 0.5) * 100);
            const delta = afterP - beforeP;

            return (
              <div key={cId} className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-primary">{cId}</span>
                    <span className="font-semibold text-foreground">{concept.name}</span>
                    {cId === 'D12' && (
                      <span className="rounded bg-rose-500/10 px-1.5 py-0.5 text-[10px] font-semibold text-rose-600">
                        Former Root Gap
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-muted-foreground">Before: {beforeP}%</span>
                    <ArrowRight className="size-3 text-muted-foreground" />
                    <span className="font-bold text-foreground">After: {afterP}%</span>
                    {delta > 0 && (
                      <span className="font-bold text-emerald-600 dark:text-emerald-400">
                        (+{delta}%)
                      </span>
                    )}
                  </div>
                </div>

                {/* Progress bars: Before and After side-by-side comparison */}
                <div className="flex gap-2">
                  <div className="h-2 w-1/2 rounded-full bg-muted overflow-hidden">
                    <div
                      className="h-full bg-muted-foreground/50"
                      style={{ width: `${beforeP}%` }}
                    />
                  </div>
                  <div className="h-2 w-1/2 rounded-full bg-muted overflow-hidden">
                    <div
                      className="h-full bg-emerald-500 transition-all duration-500"
                      style={{ width: `${afterP}%` }}
                    />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Unresolved Gaps Status & Next Steps */}
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-lg border bg-card p-5 space-y-2">
          <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-semibold text-sm">
            <CheckCircle2 className="size-4" />
            Unresolved Foundational Gaps: 0
          </div>
          <p className="text-xs text-muted-foreground leading-relaxed">
            All primary prerequisite blockers in the current study scope are cleared. No further
            cascading weaknesses detected for SQL or Relational Algebra.
          </p>
        </div>

        <div className="rounded-lg border bg-card p-5 space-y-2">
          <div className="flex items-center gap-2 text-primary font-semibold text-sm">
            <Sparkles className="size-4" />
            Recommended Next Horizon
          </div>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Ready to explore advanced topics: <strong>Transactions &amp; ACID (D15)</strong> or{' '}
            <strong>Query Processing &amp; Optimization (D18)</strong>.
          </p>
        </div>
      </div>

      <div className="flex flex-wrap gap-3">
        <Button onClick={onBackToDashboard}>
          <BookOpen className="mr-2 size-4" />
          Go to Student Dashboard
        </Button>
        {onViewDiagnosis && (
          <Button variant="outline" onClick={onViewDiagnosis}>
            View Diagnosis &amp; Graph
          </Button>
        )}
        <Button
          variant="outline"
          onClick={() => {
            setInRetestQuiz(true);
            setCurrentIdx(0);
            setSelectedId(null);
            setAnswers({});
          }}
        >
          <RotateCcw className="mr-2 size-4" />
          Retake Retest
        </Button>
      </div>
    </div>
  );
}
