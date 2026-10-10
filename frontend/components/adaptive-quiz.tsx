'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Question } from '@/lib/types';
import { Button } from './ui/button';
import { cn } from '../lib/utils';
import {
  Timer,
  ShieldCheck,
  ArrowRight,
  HelpCircle,
  ThumbsUp,
  Sparkles,
  Shuffle,
  BookOpen,
  Layers
} from 'lucide-react';

export const CONCEPT_NAMES: Record<string, string> = {
  D01: 'DBMS Basics',
  D02: 'Relational Model',
  D03: 'Keys',
  D04: 'Integrity Constraints',
  D05: 'ER Modeling',
  D06: 'ER-to-Relational Mapping',
  D07: 'Relational Algebra',
  D08: 'SQL Basics',
  D09: 'SQL Joins',
  D10: 'Aggregation & GROUP BY',
  D11: 'Subqueries & Views',
  D12: 'Functional Dependencies',
  D13: 'Normalization (1NF-3NF)',
  D14: 'BCNF & Decomposition',
  D15: 'Transactions & ACID',
  D16: 'Concurrency Control',
  D17: 'Indexing (B+ Trees)',
  D18: 'Query Optimization'
};

interface AdaptiveQuizProps {
  questions: Question[];
  totalBankCount?: number;
  onComplete: (sessionData: {
    responses: {
      question: Question;
      selectedOptionId: string;
      confidence: 'low' | 'medium' | 'high';
      responseMs: number;
      answerChanges: number;
    }[];
  }) => void;
  onCancel?: () => void;
  onReshuffle?: () => void;
  questionCount?: number;
  onQuestionCountChange?: (count: number) => void;
}

export function AdaptiveQuiz({
  questions,
  totalBankCount = 236,
  onComplete,
  onCancel,
  onReshuffle,
  questionCount = 8,
  onQuestionCountChange
}: AdaptiveQuizProps) {
  const [hasConsented, setHasConsented] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedOptionId, setSelectedOptionId] = useState<string | null>(null);
  const [confidence, setConfidence] = useState<'low' | 'medium' | 'high'>('medium');
  const [answerChanges, setAnswerChanges] = useState(0);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [submittedResponses, setSubmittedResponses] = useState<{
    question: Question;
    selectedOptionId: string;
    confidence: 'low' | 'medium' | 'high';
    responseMs: number;
    answerChanges: number;
  }[]>([]);

  const questionStartTimeRef = useRef<number>(Date.now());

  useEffect(() => {
    if (hasConsented) {
      questionStartTimeRef.current = Date.now();
      setElapsedSeconds(0);
      setAnswerChanges(0);
      setSelectedOptionId(null);
      setConfidence('medium');

      const interval = setInterval(() => {
        setElapsedSeconds(s => s + 1);
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [currentIndex, hasConsented]);

  if (!questions || questions.length === 0) {
    return (
      <div className="flex min-h-[300px] flex-col items-center justify-center rounded-xl border bg-card p-8 text-center space-y-4">
        <div className="size-10 rounded-full border-2 border-primary border-t-transparent animate-spin" />
        <p className="text-sm font-medium text-foreground">
          Loading and shuffling questions from 236-question bank...
        </p>
        <p className="text-xs text-muted-foreground">
          Selecting optimal diagnostic sampling across all 18 DBMS concepts
        </p>
      </div>
    );
  }

  const currentQuestion = questions[currentIndex] || questions[0];
  const conceptName = CONCEPT_NAMES[currentQuestion?.concept] || currentQuestion?.concept || 'DBMS Concept';

  const handleSelectOption = (optionId: string) => {
    if (selectedOptionId !== null && selectedOptionId !== optionId) {
      setAnswerChanges(c => c + 1);
    }
    setSelectedOptionId(optionId);
  };

  const handleNextQuestion = () => {
    if (!selectedOptionId || !currentQuestion) return;

    const responseMs = Date.now() - questionStartTimeRef.current;
    const newRecord = {
      question: currentQuestion,
      selectedOptionId,
      confidence,
      responseMs,
      answerChanges
    };

    const nextList = [...submittedResponses, newRecord];
    setSubmittedResponses(nextList);

    if (currentIndex < questions.length - 1) {
      setCurrentIndex(idx => idx + 1);
    } else {
      onComplete({ responses: nextList });
    }
  };

  // Screen 1: Clean Consent Screen with Shuffling Controls
  if (!hasConsented) {
    return (
      <div className="mx-auto max-w-xl">
        <div className="rounded-xl border bg-card p-6 sm:p-8 space-y-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="flex size-10 items-center justify-center rounded-full bg-primary/10 text-primary">
                <ShieldCheck className="size-5" />
              </span>
              <div>
                <h1 className="text-xl font-bold">Adaptive Diagnostic Quiz</h1>
                <p className="text-xs text-muted-foreground">Database Management Systems</p>
              </div>
            </div>
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-xs font-semibold border border-emerald-500/20">
              <Layers className="size-3.5" />
              <span>{totalBankCount} Questions In Bank</span>
            </div>
          </div>

          <p className="text-sm text-muted-foreground leading-relaxed">
            Every quiz session automatically draws a fresh, shuffled set of questions across all 18 DBMS curriculum concepts so you never repeat the same test.
          </p>

          {/* Quiz Length Selector */}
          {onQuestionCountChange && (
            <div className="rounded-lg border bg-muted/20 p-3.5 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-foreground">Session Quiz Length:</span>
                <span className="text-muted-foreground">{questions.length} questions selected</span>
              </div>
              <div className="grid grid-cols-3 gap-2">
                {[5, 8, 12].map(n => (
                  <button
                    key={n}
                    type="button"
                    onClick={() => onQuestionCountChange(n)}
                    className={cn(
                      'py-1.5 px-3 rounded-md text-xs font-medium border transition-all text-center',
                      questionCount === n
                        ? 'border-primary bg-primary text-primary-foreground shadow-sm font-semibold'
                        : 'border-border bg-card text-muted-foreground hover:bg-muted'
                    )}
                  >
                    {n} Questions {n === 8 ? '(Balanced)' : n === 5 ? '(Quick)' : '(In-depth)'}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="rounded-md border bg-muted/30 p-4 space-y-2 text-xs">
            <p className="font-semibold text-foreground flex items-center gap-1.5">
              <Sparkles className="size-3.5 text-primary" />
              Smart Shuffling & Diagnostic Rules:
            </p>
            <div className="space-y-1 text-muted-foreground">
              <p>• Randomly stratifies across foundational, intermediate, and advanced tiers</p>
              <p>• Prioritizes questions you have not answered recently</p>
              <p>• Shuffles question choices so you test concepts, not answer letters</p>
              <p>• Bayesian NetworkX engine traces distractors directly to root knowledge gaps</p>
            </div>
          </div>

          <div className="flex items-center justify-between pt-2 gap-3">
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="sm" onClick={onCancel} className="text-muted-foreground">
                Back to Dashboard
              </Button>
              {onReshuffle && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onReshuffle}
                  className="flex items-center gap-1.5 text-xs"
                  title="Reshuffle for a completely new set of questions"
                >
                  <Shuffle className="size-3.5" />
                  <span>Reshuffle</span>
                </Button>
              )}
            </div>
            <Button onClick={() => setHasConsented(true)} className="px-5">
              Start Quiz
              <ArrowRight className="ml-2 size-4" />
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // Screen 2: Clean Quiz Interface with Concept and Shuffled Presentation
  return (
    <div className="mx-auto max-w-2xl space-y-5">
      {/* Quiz Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Question {currentIndex + 1} of {questions.length}
            </span>
            <span className="text-muted-foreground/40">•</span>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-primary/10 text-primary border border-primary/20">
              <BookOpen className="size-3" />
              {currentQuestion.concept}: {conceptName}
            </span>
          </div>
          <h2 className="text-base sm:text-lg font-bold mt-1">
            {conceptName}
          </h2>
        </div>
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span className="flex items-center gap-1 font-mono bg-muted/50 px-2.5 py-1 rounded-md border">
            <Timer className="size-3.5 text-primary" />
            {Math.floor(elapsedSeconds / 60)}:
            {(elapsedSeconds % 60).toString().padStart(2, '0')}
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="h-1.5 w-full rounded-full bg-muted overflow-hidden">
        <div
          className="h-full bg-primary transition-all duration-300"
          style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
        />
      </div>

      {/* Question Card */}
      <div className="rounded-xl border bg-card p-6 shadow-sm space-y-6">
        <h3 className="text-base font-semibold leading-relaxed text-foreground">
          {currentQuestion.prompt}
        </h3>

        {/* Options */}
        <div className="space-y-2.5">
          {currentQuestion.options.map((opt, i) => {
            const isSelected = selectedOptionId === opt.id;
            return (
              <button
                key={opt.id}
                onClick={() => handleSelectOption(opt.id)}
                className={cn(
                  'flex w-full items-start gap-3 rounded-lg border p-3.5 text-left text-sm transition-all',
                  isSelected
                    ? 'border-primary bg-primary/5 ring-1 ring-primary'
                    : 'border-border hover:bg-muted/50'
                )}
              >
                <span
                  className={cn(
                    'flex size-5 shrink-0 items-center justify-center rounded-full border text-xs font-semibold',
                    isSelected
                      ? 'border-primary bg-primary text-primary-foreground'
                      : 'border-muted-foreground/30 text-muted-foreground'
                  )}
                >
                  {String.fromCharCode(65 + i)}
                </span>
                <span className="leading-snug">{opt.text}</span>
              </button>
            );
          })}
        </div>

        {/* Confidence Tap */}
        <div className="border-t pt-4">
          <p className="text-xs font-semibold text-muted-foreground mb-2">
            How confident are you in this answer?
          </p>
          <div className="grid grid-cols-3 gap-2">
            {(
              [
                { id: 'low', label: 'Not Sure', icon: HelpCircle },
                { id: 'medium', label: 'Fairly Sure', icon: Sparkles },
                { id: 'high', label: 'Confident', icon: ThumbsUp }
              ] as const
            ).map(item => (
              <button
                key={item.id}
                type="button"
                onClick={() => setConfidence(item.id)}
                className={cn(
                  'flex items-center justify-center gap-1.5 rounded-md border p-2 text-xs transition-all',
                  confidence === item.id
                    ? 'border-primary bg-muted font-semibold text-foreground'
                    : 'border-border text-muted-foreground hover:bg-muted/40'
                )}
              >
                <item.icon className="size-3.5 text-primary" />
                <span>{item.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Footer controls */}
        <div className="flex items-center justify-between pt-2 border-t">
          <Button variant="ghost" size="sm" onClick={onCancel} className="text-muted-foreground">
            Exit
          </Button>
          <Button
            disabled={!selectedOptionId}
            onClick={handleNextQuestion}
            className="px-5"
          >
            {currentIndex === questions.length - 1 ? 'Finish & See Diagnosis' : 'Next Question'}
            <ArrowRight className="ml-1.5 size-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
