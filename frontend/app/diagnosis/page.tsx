'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { DiagnosisReport } from '@/components/diagnosis-report';
import { AppNavBar } from '@/components/app-nav-bar';
import { StudentMastery, ResponseRecord } from '@/lib/types';
import { fetchStudentMastery, fetchQuizResponses } from '@/lib/apiClient';

export default function DiagnosisPage() {
  const router = useRouter();
  const [masteryMap, setMasteryMap] = useState<Record<string, StudentMastery>>({});
  const [rootGapId, setRootGapId] = useState('');
  const [responses, setResponses] = useState<ResponseRecord[]>([]);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const logged = localStorage.getItem('mindmesh_logged_in') === 'true';
      if (!logged) {
        router.push('/signin?callbackUrl=/diagnosis');
        return;
      }
      localStorage.removeItem('mindmesh_latest_diagnosis');
      const savedUserId = localStorage.getItem('mindmesh_user_id') || 'usr_alex_chen';

      // 1. Try reading the latest quiz responses from session/local storage
      try {
        const stored = localStorage.getItem('mindmesh_latest_quiz_responses');
        if (stored) {
          const parsed = JSON.parse(stored);
          if (Array.isArray(parsed) && parsed.length > 0) {
            setResponses(parsed);
          }
        }
      } catch {
        // Fallback to DB
      }

      // 2. Fetch student mastery from DB
      fetchStudentMastery(savedUserId).then(m => {
        if (m && Object.keys(m).length > 0) {
          setMasteryMap(m);
          const gaps = Object.values(m).filter(x => x.status === 'confirmed' || x.status === 'suspected');
          if (gaps.length > 0) {
            gaps.sort((a, b) => (b.blocker_score ?? 0) - (a.blocker_score ?? 0) || a.p - b.p);
            setRootGapId(gaps[0].concept_id);
          } else {
            setRootGapId('');
          }
        } else {
          setMasteryMap({});
          setRootGapId('');
        }
      });

      // 3. If responses still empty, load from database
      fetchQuizResponses(savedUserId).then(dbResponses => {
        if (dbResponses && dbResponses.length > 0) {
          setResponses(prev => (prev.length > 0 ? prev : dbResponses));
        }
      });
    }
  }, [router]);

  return (
    <div className="min-h-screen bg-background text-foreground transition-colors duration-200">
      <AppNavBar currentTab="diagnosis" />
      <div className="p-3 sm:p-6 lg:p-8 max-w-6xl mx-auto pb-24 lg:pb-8">
        <DiagnosisReport
          masteryMap={masteryMap}
          responses={responses}
          rootGapId={rootGapId}
          onRetest={() => router.push('/retest')}
          onGoToRoadmap={() => router.push('/dashboard')}
          isDark={false}
        />
      </div>
    </div>
  );
}
