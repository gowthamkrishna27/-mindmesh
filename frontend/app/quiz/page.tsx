'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { AdaptiveQuiz } from '@/components/adaptive-quiz';
import { AppNavBar } from '@/components/app-nav-bar';
import { Question } from '@/lib/types';
import { fetchQuestions, diagnoseWithNetworkX, saveStudentMastery, saveQuizResponses } from '@/lib/apiClient';
import { ResponseRecord } from '@/lib/types';

export default function QuizPage() {
  const router = useRouter();
  const [questions, setQuestions] = useState<Question[]>([]);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const logged = localStorage.getItem('mindmesh_logged_in') === 'true';
      if (!logged) {
        router.push('/signin?callbackUrl=/quiz');
        return;
      }
    }
    fetchQuestions('A').then(qs => {
      if (qs && qs.length > 0) setQuestions(qs.slice(0, 5));
    });
  }, [router]);

  const handleComplete = async (sessionData: {
    responses: {
      question: Question;
      selectedOptionId: string;
      confidence: 'low' | 'medium' | 'high';
      responseMs: number;
      answerChanges: number;
    }[];
  }) => {
    const formatted = sessionData.responses.map(r => {
      const opt = r.question.options.find(o => o.id === r.selectedOptionId);
      return {
        question_id: r.question.id,
        concept_id: r.question.concept,
        option_id: r.selectedOptionId,
        confidence: r.confidence,
        response_ms: r.responseMs,
        correct: !!opt?.correct
      };
    });

    const userId =
      typeof window !== 'undefined'
        ? localStorage.getItem('mindmesh_user_id') || 'usr_alex_chen'
        : 'usr_alex_chen';

    try {
      const diag = await diagnoseWithNetworkX(formatted, userId);
      if (diag && diag.mastery_map) {
        await saveStudentMastery(userId, diag.mastery_map);
      }
      const responseRecords: ResponseRecord[] = sessionData.responses.map(r => {
        const opt = r.question.options.find(o => o.id === r.selectedOptionId);
        return {
          id: 'R_' + Date.now() + '_' + Math.random().toString(36).substr(2, 4),
          question_id: r.question.id,
          concept_id: r.question.concept,
          option_id: r.selectedOptionId,
          correct: !!opt?.correct,
          confidence: r.confidence,
          response_ms: r.responseMs,
          evidence_weight: r.confidence === 'high' ? 1.25 : 1.0,
          distractor_mapped_to: opt?.maps_to,
          misconception: opt?.misconception,
          timestamp: new Date().toISOString()
        };
      });
      await saveQuizResponses(userId, responseRecords);
    } catch (err) {
      console.warn('NetworkX diagnose error:', err);
    }

    router.push('/diagnosis');
  };

  return (
    <div className="min-h-screen bg-background text-foreground transition-colors duration-200">
      <AppNavBar currentTab="quiz" />
      <div className="p-3 sm:p-6 lg:p-8 max-w-4xl mx-auto pb-24 lg:pb-8">
        <AdaptiveQuiz
          questions={questions}
          onComplete={handleComplete}
          onCancel={() => router.push('/dashboard')}
        />
      </div>
    </div>
  );
}
