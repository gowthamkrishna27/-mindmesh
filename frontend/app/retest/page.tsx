'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { RetestReport } from '@/components/retest-report';
import { AppNavBar } from '@/components/app-nav-bar';

export default function RetestPage() {
  const router = useRouter();

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const logged = localStorage.getItem('mindmesh_logged_in') === 'true';
      if (!logged) {
        router.push('/signin?callbackUrl=/retest');
      }
    }
  }, [router]);

  return (
    <div className="min-h-screen bg-background text-foreground transition-colors duration-200">
      <AppNavBar currentTab="retest" />
      <div className="p-3 sm:p-6 lg:p-8 max-w-6xl mx-auto pb-24 lg:pb-8">
        <RetestReport
          onBackToDashboard={() => router.push('/dashboard')}
          onViewDiagnosis={() => router.push('/diagnosis')}
        />
      </div>
    </div>
  );
}
