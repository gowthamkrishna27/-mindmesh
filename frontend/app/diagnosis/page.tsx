'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { DiagnosisReport } from '@/components/diagnosis-report';
import { AppNavBar } from '@/components/app-nav-bar';
import { StudentMastery, ResponseRecord } from '@/lib/types';
import { fetchStudentMastery } from '@/lib/apiClient';

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
          onRetakeQuiz={() => router.push('/quiz')}
          isDark={false}
        />
      </div>
    </div>
  );
}
