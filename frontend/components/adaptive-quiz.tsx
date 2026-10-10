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
  Sparkles
} from 'lucide-react';

interface AdaptiveQuizProps {
  questions: Question[];
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
}

export function AdaptiveQuiz({ questions, onComplete, onCancel }: AdaptiveQuizProps) {
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
      <div className="flex min-h-[300px] items-center justify-center rounded-xl border bg-card p-8">
        <p className="text-sm text-muted-foreground animate-pulse">
          Loading diagnostic questions from database...
        </p>
      </div>
    );
  }

  const currentQuestion = questions[currentIndex] || questions[0];

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

  // Screen 1: Clean Consent Screen
  if (!hasConsented) {
    return (
      <div className="mx-auto max-w-xl">
        <div className="rounded-lg border bg-card p-6 sm:p-8 space-y-6">
          <div className="flex items-center gap-3">
            <span className="flex size-10 items-center justify-center rounded-full bg-primary/10 text-primary">
              <ShieldCheck className="size-5" />
            </span>
            <div>
              <h1 className="text-xl font-bold">Diagnostic Check</h1>
              <p className="text-xs text-muted-foreground">Database Management Systems</p>
            </div>
          </div>

          <p className="text-sm text-muted-foreground leading-relaxed">
            This quick 5-question check identifies your strengths and flags missing prerequisite foundations.
          </p>

          <div className="rounded-md border bg-muted/30 p-4 space-y-2 text-xs">
            <p className="font-semibold text-foreground">How it works:</p>
            <div className="space-y-1.5 text-muted-foreground">
              <p>• One question at a time with optional confidence rating</p>
              <p>• Traces incorrect answers to root foundational concepts</p>
              <p>• Builds your custom study roadmap immediately after completion</p>
            </div>
          </div>

          <div className="flex items-center justify-between pt-2">
            <Button variant="ghost" size="sm" onClick={onCancel} className="text-muted-foreground">
              Back to Dashboard
            </Button>
            <Button onClick={() => setHasConsented(true)}>
              Start Diagnostic
              <ArrowRight className="ml-2 size-4" />
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // Screen 2: Clean Quiz Interface
  return (
    <div className="mx-auto max-w-2xl space-y-5">
      {/* Quiz Header */}
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Question {currentIndex + 1} of {questions.length}
          </span>
          <h2 className="text-lg font-bold">
            {currentQuestion?.concept ? `Topic ${currentQuestion.concept}` : 'Diagnostic Question'}
          </h2>
        </div>
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span className="flex items-center gap-1 font-mono">
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
      <div className="rounded-lg border bg-card p-6 shadow-sm space-y-6">
        <h3 className="text-base font-semibold leading-relaxed">
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
