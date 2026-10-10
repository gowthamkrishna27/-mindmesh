'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { StudentDashboard } from '@/components/student-dashboard';
import { EducatorDashboard } from '@/components/educator-dashboard';
import { AppNavBar } from '@/components/app-nav-bar';
import { ResponseRecord } from '@/lib/types';
import { fetchStudentMastery } from '@/lib/apiClient';

export default function DashboardPage() {
  const router = useRouter();
  const [role, setRole] = useState<'student' | 'educator'>('student');
  const [userName, setUserName] = useState('Alex Chen');
  const [masteryCount, setMasteryCount] = useState(0);
  const [gapCount, setGapCount] = useState(0);
  const [rootGapId, setRootGapId] = useState('');
  const [responses, setResponses] = useState<ResponseRecord[]>([]);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const logged = localStorage.getItem('mindmesh_logged_in') === 'true';
      if (!logged) {
        router.push('/signin');
        return;
      }
      localStorage.removeItem('mindmesh_latest_diagnosis');
      const savedRole = localStorage.getItem('mindmesh_role') as 'student' | 'educator' | null;
      const savedUser = localStorage.getItem('mindmesh_user');
      const savedUserId = localStorage.getItem('mindmesh_user_id') || 'usr_alex_chen';
      if (savedRole) setRole(savedRole);
      if (savedUser) setUserName(savedUser);

      fetchStudentMastery(savedUserId).then(m => {
        if (m && Object.keys(m).length > 0) {
          const mastered = Object.values(m).filter(x => x.status === 'mastered').length;
          const gaps = Object.values(m).filter(x => x.status === 'confirmed' || x.status === 'suspected');
          setMasteryCount(mastered);
          setGapCount(gaps.length);
          if (gaps.length > 0) {
            gaps.sort((a, b) => (b.blocker_score ?? 0) - (a.blocker_score ?? 0) || a.p - b.p);
            setRootGapId(gaps[0].concept_id);
          } else {
            setRootGapId('');
          }
        } else {
          setMasteryCount(0);
          setGapCount(0);
          setRootGapId('');
        }
      });
    }
  }, [router]);

  return (
    <div className="min-h-screen bg-background text-foreground transition-colors duration-200">
      <AppNavBar
        currentTab={role === 'educator' ? 'educator' : 'dashboard'}
        role={role}
        userName={userName}
      />
      <div className="p-3 sm:p-6 lg:p-8 max-w-6xl mx-auto pb-24 lg:pb-8">
        {role === 'educator' ? (
          <EducatorDashboard />
        ) : (
          <StudentDashboard
            userName={userName}
            selectedSubject="dbms"
            onSelectSubject={() => {}}
            onStartQuiz={() => router.push('/quiz')}
            onViewDiagnosis={() => router.push('/diagnosis')}
            onRetest={() => router.push('/retest')}
            masteryCount={masteryCount}
            gapCount={gapCount}
            rootGapId={rootGapId}
            responses={responses}
          />
        )}
      </div>
    </div>
  );
}
