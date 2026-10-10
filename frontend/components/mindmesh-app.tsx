'use client';

import React, { useEffect, useMemo, useState } from 'react';
import Image from 'next/image';
import {
  LayoutGrid,
  Target,
  Network,
  GraduationCap,
  RotateCcw,
  Users,
  Moon,
  Sun,
  BookOpen,
  LogOut
} from 'lucide-react';
import { Button } from './ui/button';
import { cn } from '../lib/utils';
import {
  StudentMastery,
  ResponseRecord,
  Question
} from '@/lib/types';
import {
  diagnoseWithNetworkX,
  fetchQuestions,
  fetchStudentMastery,
  saveStudentMastery,
  saveQuizResponses
} from '@/lib/apiClient';

import { StudentDashboard } from './student-dashboard';
import { AdaptiveQuiz } from './adaptive-quiz';
import { DiagnosisReport } from './diagnosis-report';
import { RetestReport } from './retest-report';
import { EducatorDashboard } from './educator-dashboard';
import { AuthScreen } from './auth-screen';
import { ProfileModal } from './profile-modal';
import { AppNavBar, NavTabId } from './app-nav-bar';

type ViewMode = 'dashboard' | 'quiz' | 'diagnosis' | 'retest' | 'educator';

export function MindmeshApp() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [view, setView] = useState<ViewMode>('dashboard');
  const [dark, setDark] = useState(false);
  const [role, setRole] = useState<'student' | 'educator'>('student');
  const [userName, setUserName] = useState('Alex Chen');
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [selectedSubject, setSelectedSubject] = useState('dbms');

  // Mastery and response state from Supabase DB
  const [masteryMap, setMasteryMap] = useState<Record<string, StudentMastery>>({});
  const [responses, setResponses] = useState<ResponseRecord[]>([]);
  const [rootGapId, setRootGapId] = useState<string>('');

  const [diagnosticQuestions, setDiagnosticQuestions] = useState<Question[]>([]);

  useEffect(() => {
    fetchQuestions('A').then(qs => {
      if (qs && qs.length > 0) setDiagnosticQuestions(qs.slice(0, 5));
    });
  }, []);

  const loadUserMastery = (userId: string) => {
    fetchStudentMastery(userId).then(m => {
      if (m && Object.keys(m).length > 0) {
        setMasteryMap(m);
        const gaps = Object.values(m).filter(
          x => x.status === 'confirmed' || x.status === 'suspected'
        );
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
  };

  // Check saved session on mount and load user's real DB mastery
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('mindmesh_latest_diagnosis');
      const savedLogin = localStorage.getItem('mindmesh_logged_in') === 'true';
      const savedRole = localStorage.getItem('mindmesh_role') as 'student' | 'educator' | null;
      const savedUser = localStorage.getItem('mindmesh_user');
      const savedUserId = localStorage.getItem('mindmesh_user_id') || 'usr_alex_chen';
      if (savedLogin) {
        setIsAuthenticated(true);
        if (savedRole) setRole(savedRole);
        if (savedUser) setUserName(savedUser);
        if (savedRole === 'educator') setView('educator');

        loadUserMastery(savedUserId);
      }
    }
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark);
    document.documentElement.classList.toggle('light', !dark);
  }, [dark]);

  const handleQuizComplete = async (sessionData: {
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

    try {
      const diag = await diagnoseWithNetworkX(formatted);
      if (diag && diag.mastery_map) {
        setMasteryMap(diag.mastery_map);
        if (diag.root_gap_id) setRootGapId(diag.root_gap_id);
        const userId =
          typeof window !== 'undefined'
            ? localStorage.getItem('mindmesh_user_id') || 'usr_alex_chen'
            : 'usr_alex_chen';
        saveStudentMastery(userId, diag.mastery_map);
      }
    } catch {
      // In case backend is connecting
    }

    const newResponses: ResponseRecord[] = sessionData.responses.map(r => {
      const opt = r.question.options.find(o => o.id === r.selectedOptionId);
      return {
        id: 'R' + Date.now().toString().slice(-4),
        question_id: r.question.id,
        concept_id: r.question.concept,
        option_id: r.selectedOptionId,
        correct: !!opt?.correct,
        confidence: r.confidence,
        response_ms: r.responseMs,
        evidence_weight: r.confidence === 'high' ? 1.25 : 1.0,
        distractor_mapped_to: opt?.maps_to,
        misconception: opt?.misconception,
        timestamp: new Date().toLocaleTimeString()
      };
    });

    const userId =
      typeof window !== 'undefined'
        ? localStorage.getItem('mindmesh_user_id') || 'usr_alex_chen'
        : 'usr_alex_chen';
    saveQuizResponses(userId, newResponses);

    setResponses(prev => [...newResponses, ...prev]);
    setView('diagnosis');
  };

  const handleSignOut = () => {
    setIsAuthenticated(false);
    if (typeof window !== 'undefined') {
      localStorage.removeItem('mindmesh_logged_in');
      localStorage.removeItem('mindmesh_role');
      localStorage.removeItem('mindmesh_user');
      document.cookie = 'mindmesh_logged_in=; path=/; max-age=0';
      document.cookie = 'mindmesh_role=; path=/; max-age=0';
      document.cookie = 'mindmesh_user=; path=/; max-age=0';
    }
  };

  // STRICT LOGIN WALL: If not authenticated, require Sign In / Sign Up
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-background text-foreground flex flex-col justify-center transition-colors duration-200 relative">
        <header className="absolute top-0 right-0 p-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setDark(!dark)}
            aria-label={dark ? 'Light theme' : 'Dark theme'}
          >
            {dark ? <Sun data-icon="inline-start" /> : <Moon data-icon="inline-start" />}
          </Button>
        </header>

        <AuthScreen
          initialMode="signin"
          onSuccess={(newRole, newName) => {
            setRole(newRole);
            setUserName(newName);
            setIsAuthenticated(true);
            if (typeof window !== 'undefined') {
              localStorage.setItem('mindmesh_logged_in', 'true');
              localStorage.setItem('mindmesh_role', newRole);
              localStorage.setItem('mindmesh_user', newName);
              document.cookie = 'mindmesh_logged_in=true; path=/; max-age=86400; SameSite=Lax';
              document.cookie = `mindmesh_role=${newRole}; path=/; max-age=86400; SameSite=Lax`;
              document.cookie = `mindmesh_user=${encodeURIComponent(newName)}; path=/; max-age=86400; SameSite=Lax`;
              const uid = localStorage.getItem('mindmesh_user_id') || 'usr_alex_chen';
              loadUserMastery(uid);
            }
            if (newRole === 'educator') setView('educator');
            else setView('dashboard');
          }}
        />
      </div>
    );
  }

  // Simple, clean navigation items
  const studentNavItems = [
    { id: 'dashboard' as ViewMode, label: 'Dashboard', icon: LayoutGrid },
    { id: 'quiz' as ViewMode, label: 'Diagnostic Quiz', icon: Target },
    { id: 'diagnosis' as ViewMode, label: 'Diagnosis & Graph', icon: Network },
    { id: 'retest' as ViewMode, label: 'Retest & Report', icon: RotateCcw }
  ];

  const educatorNavItems = [
    { id: 'educator' as ViewMode, label: 'Educator Dashboard', icon: Users },
    { id: 'diagnosis' as ViewMode, label: 'Curriculum Graph', icon: Network }
  ];

  const navItems = role === 'student' ? studentNavItems : educatorNavItems;

  const masteredCount = Object.values(masteryMap).filter(m => m.status === 'mastered').length;
  const gapCount = Object.values(masteryMap).filter(
    m => m.status === 'confirmed' || m.status === 'suspected'
  ).length;

  return (
    <div className="min-h-screen bg-background text-foreground transition-colors duration-200">
      {/* Mobile Responsive Navigation Bar (Sticky Top Header + Mobile Drawer + Fixed Bottom Bar) */}
      <AppNavBar
        currentTab={view}
        onSelectTab={tab => setView(tab as ViewMode)}
        role={role}
        userName={userName}
        onSignOut={handleSignOut}
        onOpenProfile={() => setIsAuthOpen(true)}
      />

      {/* Main Container */}
      <div className="mx-auto flex max-w-6xl flex-col px-3 sm:px-6 lg:flex-row pb-20 lg:pb-8">
        {/* Desktop Sidebar Navigation (Hidden on mobile/tablet to give full screen width) */}
        <aside className="hidden lg:block lg:w-52 lg:shrink-0 lg:border-r lg:py-6 lg:pr-5">
          <nav className="flex flex-col gap-1" aria-label="Desktop Navigation">
            {navItems.map(({ id, label, icon: Icon }) => {
              const isActive = view === id;
              return (
                <button
                  key={id}
                  onClick={() => setView(id)}
                  className={cn(
                    'flex items-center gap-2.5 rounded-lg px-3 py-2 text-left text-xs font-medium transition-colors',
                    isActive
                      ? 'bg-primary/10 font-bold text-primary shadow-xs'
                      : 'text-muted-foreground hover:bg-muted/60 hover:text-foreground'
                  )}
                >
                  <Icon className={cn('size-4 shrink-0', isActive ? 'text-primary' : 'text-muted-foreground')} />
                  <span>{label}</span>
                </button>
              );
            })}
          </nav>
        </aside>

        {/* Content Body */}
        <main className="min-w-0 flex-1 py-4 sm:py-6 lg:pl-8">
          {view === 'dashboard' && (
            <StudentDashboard
              userName={userName}
              selectedSubject={selectedSubject}
              onSelectSubject={setSelectedSubject}
              onStartQuiz={() => setView('quiz')}
              onViewDiagnosis={() => setView('diagnosis')}
              onRetest={() => setView('retest')}
              masteryCount={masteredCount}
              gapCount={gapCount}
              rootGapId={rootGapId}
              responses={responses}
            />
          )}

          {view === 'quiz' && (
            <AdaptiveQuiz
              questions={diagnosticQuestions}
              onComplete={handleQuizComplete}
              onCancel={() => setView('dashboard')}
            />
          )}

          {view === 'diagnosis' && (
            <DiagnosisReport
              masteryMap={masteryMap}
              responses={responses}
              rootGapId={rootGapId}
              onRetest={() => setView('retest')}
              onRetakeQuiz={() => setView('quiz')}
              isDark={dark}
            />
          )}

          {view === 'retest' && (
            <RetestReport
              onBackToDashboard={() => setView('dashboard')}
              onViewDiagnosis={() => setView('diagnosis')}
            />
          )}

          {view === 'educator' && <EducatorDashboard />}
        </main>
      </div>

      {/* Profile Section Modal */}
      <ProfileModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        userName={userName}
        role={role}
        onUpdateName={newName => {
          setUserName(newName);
          if (typeof window !== 'undefined') {
            localStorage.setItem('mindmesh_user', newName);
            document.cookie = `mindmesh_user=${encodeURIComponent(newName)}; path=/; max-age=86400; SameSite=Lax`;
          }
        }}
        onSignOut={handleSignOut}
      />
    </div>
  );
}
