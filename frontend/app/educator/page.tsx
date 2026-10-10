'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { EducatorDashboard } from '@/components/educator-dashboard';
import { AppNavBar } from '@/components/app-nav-bar';

export default function EducatorPage() {
  const router = useRouter();
  const [userName, setUserName] = useState('Dr. Aris Thorne');
  const [dark, setDark] = useState(false);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const logged = localStorage.getItem('mindmesh_logged_in') === 'true';
      const role = localStorage.getItem('mindmesh_role');
      if (!logged) {
        router.push('/signin?callbackUrl=/educator&role=educator');
      } else if (role !== 'educator') {
        router.push('/dashboard');
      }
      const savedUser = localStorage.getItem('mindmesh_user');
      if (savedUser) setUserName(savedUser);
    }
  }, [router]);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark);
    document.documentElement.classList.toggle('light', !dark);
  }, [dark]);

  const handleSignOut = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('mindmesh_logged_in');
      localStorage.removeItem('mindmesh_role');
      localStorage.removeItem('mindmesh_user');
      document.cookie = 'mindmesh_logged_in=; path=/; max-age=0';
      document.cookie = 'mindmesh_role=; path=/; max-age=0';
      document.cookie = 'mindmesh_user=; path=/; max-age=0';
    }
    router.push('/signin?role=educator');
  };

  return (
    <div className="min-h-screen bg-background text-foreground transition-colors duration-200">
      <AppNavBar
        currentTab="educator"
        role="educator"
        userName={userName}
        onSignOut={handleSignOut}
      />

      {/* Main Content */}
      <main className="max-w-6xl mx-auto p-3 sm:p-6 lg:p-8 pb-24 lg:pb-8">
        <EducatorDashboard />
      </main>
    </div>
  );
}
