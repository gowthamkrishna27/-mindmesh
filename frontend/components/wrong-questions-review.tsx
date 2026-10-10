'use client';

import React from 'react';
import { Concept, StudentMastery, ResponseRecord, Question } from '@/lib/types';
import seedQuestionsData from '@/lib/seed-questions.json';
import {
  Clock,
  AlertCircle,
  CheckCircle2,
  XCircle,
  HelpCircle,
  BookOpen,
  ArrowRight,
  Sparkles,
  Zap,
  Layers,
  GraduationCap
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { CONCEPT_NAMES } from './adaptive-quiz';

interface WrongQuestionsReviewProps {
  responses: ResponseRecord[];
  concepts: Concept[];
  masteryMap: Record<string, StudentMastery>;
  onSelectConcept?: (concept: Concept) => void;
  onGoToRoadmap?: () => void;
}

export function WrongQuestionsReview({
  responses,
  concepts,
  masteryMap,
  onSelectConcept,
  onGoToRoadmap
}: WrongQuestionsReviewProps) {
  // Filter for incorrect responses only
  const wrongResponses = responses.filter(r => !r.correct);

  // Build a lookup map of all questions by id
  const questionsMap = React.useMemo(() => {
    const map = new Map<string, Question>();
    (seedQuestionsData as Question[]).forEach(q => {
      map.set(q.id, q);
    });
    return map;
  }, []);

  if (wrongResponses.length === 0) {
    if (responses.length === 0) {
      return null;
    }
    return (
      <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-6 text-center space-y-2">
        <div className="inline-flex size-10 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
          <CheckCircle2 className="size-5" />
        </div>
        <h3 className="text-base font-bold text-foreground">Perfect Accuracy on Tested Questions!</h3>
        <p className="text-xs text-muted-foreground max-w-md mx-auto">
          You answered all diagnostic questions correctly without triggering any distractor misconceptions. You can proceed directly to verification retesting.
        </p>
      </div>
    );
  }

  // Calculate average response time on incorrect questions
  const totalMs = wrongResponses.reduce((sum, r) => sum + (r.response_ms || 0), 0);
  const avgSeconds = (totalMs / wrongResponses.length / 1000).toFixed(1);

  return (
    <div className="rounded-xl border bg-card p-5 sm:p-6 shadow-xs space-y-6">
      {/* Section Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="flex size-7 items-center justify-center rounded-lg bg-rose-500/10 text-rose-600 dark:text-rose-400">
              <AlertCircle className="size-4" />
            </span>
            <h2 className="text-base font-bold text-foreground">
              Incorrect Questions &amp; Prerequisite Analysis
            </h2>
            <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20">
              {wrongResponses.length} {wrongResponses.length === 1 ? 'Error' : 'Errors'}
            </span>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Detailed breakdown of time taken per question and the specific prerequisite foundations you need to study.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs text-muted-foreground bg-muted/30 px-3 py-1.5 rounded-lg border w-fit">
          <Clock className="size-3.5 text-primary" />
          <span>Avg Time on Errors: <strong className="text-foreground">{avgSeconds}s</strong></span>
        </div>
      </div>

      {/* List of Wrong Questions */}
      <div className="space-y-6">
        {wrongResponses.map((r, idx) => {
          const q = questionsMap.get(r.question_id);
          const concept = concepts.find(c => c.id === r.concept_id);
          const conceptTitle = CONCEPT_NAMES[r.concept_id] || concept?.name || r.concept_id;

          const secondsTaken = ((r.response_ms || 0) / 1000).toFixed(1);
          const isRapid = (r.response_ms || 0) < 3000;
          const isSlow = (r.response_ms || 0) > 15000;

          // Find the student's selected option and correct option
          const selectedOption = q?.options.find(o => o.id === r.option_id);
          const correctOption = q?.options.find(o => o.correct);

          // Get prerequisite concepts for this question's concept
          const prereqIds = concept?.prerequisites || [];
          const prereqConcepts = prereqIds
            .map(id => concepts.find(c => c.id === id))
            .filter(Boolean) as Concept[];

          // Check if distractor maps to a specific concept
          const rootCauseConceptId = r.distractor_mapped_to;
          const rootCauseConcept = rootCauseConceptId ? concepts.find(c => c.id === rootCauseConceptId) : null;

          return (
            <div
              key={r.id || idx}
              className="rounded-xl border border-border/80 bg-background/50 p-4 sm:p-5 space-y-4 transition-all hover:border-border"
            >
              {/* Question Meta Header */}
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border/50 pb-3">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-xs font-bold text-muted-foreground bg-muted/60 px-2 py-0.5 rounded">
                    Q{idx + 1}
                  </span>
                  <span className="text-xs font-semibold text-foreground flex items-center gap-1.5">
                    <BookOpen className="size-3 text-primary" />
                    {r.concept_id}: {conceptTitle}
                  </span>
                  <span className="inline-flex items-center gap-1 text-[11px] font-medium text-rose-600 dark:text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20">
                    <XCircle className="size-3" />
                    Incorrect Answer
                  </span>
                </div>

                {/* Time Taken & Confidence Tags */}
                <div className="flex flex-wrap items-center gap-2">
                  {/* Time taken */}
                  <span
                    className={cn(
                      'inline-flex items-center gap-1 text-[11px] font-mono font-medium px-2 py-0.5 rounded border',
                      isRapid
                        ? 'bg-amber-500/10 text-amber-700 dark:text-amber-400 border-amber-500/20'
                        : isSlow
                        ? 'bg-purple-500/10 text-purple-700 dark:text-purple-400 border-purple-500/20'
                        : 'bg-muted text-muted-foreground border-border'
                    )}
                    title={isRapid ? 'Quick response (< 3s)' : isSlow ? 'High deliberation (> 15s)' : 'Standard pace'}
                  >
                    <Clock className="size-3" />
                    Time Taken: <strong>{secondsTaken}s</strong>
                    {isRapid && <Zap className="size-2.5 text-amber-500" />}
                  </span>

                  {/* Confidence */}
                  <span
                    className={cn(
                      'inline-flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded border',
                      r.confidence === 'high'
                        ? 'bg-rose-500/10 text-rose-700 dark:text-rose-400 border-rose-500/20'
                        : r.confidence === 'low'
                        ? 'bg-sky-500/10 text-sky-700 dark:text-sky-400 border-sky-500/20'
                        : 'bg-muted text-muted-foreground border-border'
                    )}
                  >
                    <HelpCircle className="size-3" />
                    Confidence: <span className="capitalize">{r.confidence}</span>
                  </span>
                </div>
              </div>

              {/* Timing Latency Insight */}
              <div className="text-[11px] text-muted-foreground flex items-center gap-1.5 bg-muted/20 px-2.5 py-1 rounded">
                <span className="font-semibold text-foreground">Time Behavior:</span>
                {isRapid ? (
                  <span>Answered in only {secondsTaken}s (rapid response suggests guessing or missing critical premise).</span>
                ) : isSlow ? (
                  <span>Spent {secondsTaken}s deliberating (signals active confusion between distractor choices).</span>
                ) : (
                  <span>Answered in {secondsTaken}s with normal pacing.</span>
                )}
                {r.confidence === 'high' && (
                  <span className="text-rose-600 dark:text-rose-400 font-medium ml-1">
                    • High confidence on a wrong answer indicates an entrenched misconception!
                  </span>
                )}
              </div>

              {/* Question Prompt */}
              {q ? (
                <div className="space-y-3">
                  <p className="text-sm font-medium text-foreground leading-relaxed">
                    {q.prompt}
                  </p>

                  {/* Selected vs Correct Option */}
                  <div className="grid gap-2.5 sm:grid-cols-2 text-xs">
                    {/* Student Selection */}
                    <div className="rounded-lg border border-rose-500/30 bg-rose-500/5 p-3 space-y-1.5">
                      <div className="flex items-center gap-1.5 text-rose-700 dark:text-rose-400 font-semibold text-[11px] uppercase tracking-wide">
                        <XCircle className="size-3.5" />
                        Your Selected Answer (Incorrect)
                      </div>
                      <p className="text-foreground font-medium">
                        {selectedOption ? selectedOption.text : `Option ${r.option_id?.toUpperCase()}`}
                      </p>
                      {/* Identified Misconception */}
                      {(r.misconception || selectedOption?.misconception) && (
                        <div className="text-[11px] text-rose-600 dark:text-rose-400 border-t border-rose-500/20 pt-1.5 mt-1.5">
                          <strong>Cognitive Misconception:</strong>{' '}
                          {r.misconception || selectedOption?.misconception}
                        </div>
                      )}
                    </div>

                    {/* Correct Answer */}
                    <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/5 p-3 space-y-1.5">
                      <div className="flex items-center gap-1.5 text-emerald-700 dark:text-emerald-400 font-semibold text-[11px] uppercase tracking-wide">
                        <CheckCircle2 className="size-3.5" />
                        Correct Answer
                      </div>
                      <p className="text-foreground font-medium">
                        {correctOption ? correctOption.text : 'Verified Correct Option'}
                      </p>
                      {q.explanation && (
                        <div className="text-[11px] text-muted-foreground border-t border-emerald-500/20 pt-1.5 mt-1.5">
                          <strong>Why:</strong> {q.explanation}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-xs text-muted-foreground">
                  Question ID: <span className="font-mono font-semibold">{r.question_id}</span>
                  {r.misconception && (
                    <p className="text-rose-600 dark:text-rose-400 mt-1">
                      Misconception: {r.misconception}
                    </p>
                  )}
                </div>
              )}

              {/* What Prerequisites Need to Learn */}
              <div className="rounded-lg border border-primary/20 bg-primary/5 p-3.5 sm:p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <GraduationCap className="size-4 text-primary" />
                    <h3 className="text-xs font-bold uppercase tracking-wider text-primary">
                      Prerequisites You Need To Learn
                    </h3>
                  </div>
                  {rootCauseConcept && (
                    <span className="text-[11px] font-semibold text-rose-600 dark:text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20">
                      Root Blocker: {rootCauseConcept.id}
                    </span>
                  )}
                </div>

                {/* Specific Distractor Mapping Notification */}
                {rootCauseConcept && (
                  <div className="text-xs text-rose-700 dark:text-rose-300 bg-rose-500/10 border border-rose-500/20 rounded p-2.5">
                    <strong>Root Cause Diagnosis:</strong> Your error on <em>{conceptTitle}</em> directly traces back to a missing foundation in{' '}
                    <strong>{rootCauseConcept.id} ({rootCauseConcept.name})</strong>. Mastering this prerequisite first will eliminate this failure pattern.
                  </div>
                )}

                {/* List of Prerequisite Concepts */}
                {prereqConcepts.length > 0 ? (
                  <div className="space-y-2">
                    <p className="text-xs text-muted-foreground">
                      To master <strong>{conceptTitle}</strong>, you must first learn these upstream prerequisite concepts:
                    </p>
                    <div className="grid gap-2 sm:grid-cols-2">
                      {prereqConcepts.map(p => {
                        const mastery = masteryMap[p.id];
                        const pScore = mastery ? Math.round(mastery.p * 100) : 50;
                        return (
                          <div
                            key={p.id}
                            className="flex flex-col justify-between rounded-lg border bg-card p-3 text-xs space-y-2 shadow-2xs hover:border-primary/50 transition-all"
                          >
                            <div>
                              <div className="flex items-center justify-between">
                                <span className="font-mono font-bold text-primary">{p.id}</span>
                                <span className="text-[10px] text-muted-foreground font-semibold uppercase">
                                  Tier {p.tier || 1} Prerequisite
                                </span>
                              </div>
                              <h4 className="font-semibold text-foreground text-xs mt-1">
                                {p.name}
                              </h4>
                              <p className="text-[11px] text-muted-foreground line-clamp-2 mt-0.5">
                                {p.description}
                              </p>

                              {/* Learning objectives preview */}
                              {p.learning_objectives && p.learning_objectives.length > 0 && (
                                <ul className="mt-2 text-[10px] text-muted-foreground space-y-0.5 list-disc list-inside">
                                  {p.learning_objectives.slice(0, 2).map((obj, oIdx) => (
                                    <li key={oIdx} className="line-clamp-1">{obj}</li>
                                  ))}
                                </ul>
                              )}
                            </div>

                            <div className="pt-2 border-t flex items-center justify-between">
                              <span className="text-[11px] text-muted-foreground">
                                Mastery: <strong className={pScore >= 70 ? 'text-emerald-600' : 'text-rose-600'}>{pScore}%</strong>
                              </span>
                              {onSelectConcept && (
                                <button
                                  type="button"
                                  onClick={() => onSelectConcept(p)}
                                  className="text-[11px] font-semibold text-primary hover:underline flex items-center gap-1"
                                >
                                  Study Concept
                                  <ArrowRight className="size-3" />
                                </button>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ) : (
                  <div className="text-xs text-muted-foreground flex items-center justify-between">
                    <span>
                      <strong>{conceptTitle}</strong> is a foundational Tier 1 concept with no upstream prerequisites. Review core definitions and schema architecture directly.
                    </span>
                    {concept && onSelectConcept && (
                      <button
                        type="button"
                        onClick={() => onSelectConcept(concept)}
                        className="text-xs font-semibold text-primary hover:underline ml-2 shrink-0"
                      >
                        Study {concept.id}
                      </button>
                    )}
                  </div>
                )}

                {/* Link to Learning Roadmap */}
                {onGoToRoadmap && (
                  <div className="pt-1 flex justify-end">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={onGoToRoadmap}
                      className="text-xs gap-1.5 h-7"
                    >
                      <Layers className="size-3 text-primary" />
                      View Personalized Prerequisite Roadmap
                    </Button>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
