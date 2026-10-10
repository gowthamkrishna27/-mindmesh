'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import {
  LayoutGrid,
  Target,
  Network,
  RotateCcw,
  Users,
  Sun,
  Moon,
  LogOut,
  User,
  ShieldCheck
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export type NavTabId = 'dashboard' | 'quiz' | 'diagnosis' | 'retest' | 'educator';

interface AppNavBarProps {
  currentTab: NavTabId;
  onSelectTab?: (tab: NavTabId) => void;
  role?: 'student' | 'educator';
  userName?: string;
  onSignOut?: () => void;
  onOpenProfile?: () => void;
}

export function AppNavBar({
  currentTab,
  onSelectTab,
  role: propRole,
  userName: propUserName,
  onSignOut,
  onOpenProfile
}: AppNavBarProps) {
  const router = useRouter();
  const [dark, setDark] = useState(false);
  const [role, setRole] = useState<'student' | 'educator'>(propRole || 'student');
  const [userName, setUserName] = useState<string>(propUserName || 'Alex Chen');

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedRole = localStorage.getItem('mindmesh_role') as 'student' | 'educator' | null;
      const savedUser = localStorage.getItem('mindmesh_user');
      if (savedRole && !propRole) setRole(savedRole);
      if (savedUser && !propUserName) setUserName(savedUser);

      // Check current dark theme
      const isDarkTheme = document.documentElement.classList.contains('dark');
      setDark(isDarkTheme);
    }
  }, [propRole, propUserName]);

  const toggleTheme = () => {
    const nextDark = !dark;
    setDark(nextDark);
    if (typeof document !== 'undefined') {
      document.documentElement.classList.toggle('dark', nextDark);
      document.documentElement.classList.toggle('light', !nextDark);
    }
  };

  const handleTabClick = (tabId: NavTabId) => {
    if (onSelectTab) {
      onSelectTab(tabId);
    } else {
      router.push('/' + tabId);
    }
  };

  const handleSignOutAction = () => {
    if (onSignOut) {
      onSignOut();
    } else if (typeof window !== 'undefined') {
      localStorage.removeItem('mindmesh_logged_in');
      localStorage.removeItem('mindmesh_role');
      localStorage.removeItem('mindmesh_user');
      document.cookie = 'mindmesh_logged_in=; path=/; max-age=0';
      document.cookie = 'mindmesh_role=; path=/; max-age=0';
      document.cookie = 'mindmesh_user=; path=/; max-age=0';
      router.push('/signin' + (role === 'educator' ? '?role=educator' : ''));
    }
  };

  // Student vs Educator Navigation Tabs
  const studentTabs: { id: NavTabId; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutGrid },
    { id: 'quiz', label: 'Quiz', icon: Target },
    { id: 'diagnosis', label: 'Diagnosis', icon: Network },
    { id: 'retest', label: 'Retest', icon: RotateCcw }
  ];

  const educatorTabs: { id: NavTabId; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
    { id: 'educator', label: 'Class Heatmap', icon: Users },
    { id: 'diagnosis', label: 'Curriculum Graph', icon: Network }
  ];

  const tabs = role === 'educator' ? educatorTabs : studentTabs;

  return (
    <>
      {/* 1. TOP NAVBAR (Sticky clean header) */}
      <header className="border-b bg-background/95 sticky top-0 z-40 backdrop-blur transition-colors">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-3 sm:px-6">
          {/* Left: Brand Logo & Title */}
          <button
            onClick={() => handleTabClick(role === 'educator' ? 'educator' : 'dashboard')}
            className="flex items-center gap-2.5 transition-opacity hover:opacity-90"
            aria-label="Mind Mesh home"
          >
            <Image
              src="/logo.png"
              alt="Mind Mesh Logo"
              width={40}
              height={28}
              className="h-7 sm:h-8 w-auto object-contain"
              priority
            />
            <span className="font-brand text-xl sm:text-2xl font-extrabold tracking-tight text-foreground">
              Mind Mesh
            </span>
            {role === 'educator' ? (
              <span className="hidden sm:inline ml-1.5 rounded bg-primary/10 px-2 py-0.5 text-xs font-semibold text-primary">
                Educator Portal
              </span>
            ) : (
              <span className="hidden sm:inline ml-1.5 rounded bg-muted px-2 py-0.5 text-[11px] font-medium text-muted-foreground">
                Student
              </span>
            )}
          </button>

          {/* Center: Desktop Navigation links */}
          <nav className="hidden lg:flex items-center gap-1">
            {tabs.map(({ id, label, icon: Icon }) => {
              const isActive = currentTab === id;
              return (
                <button
                  key={id}
                  onClick={() => handleTabClick(id)}
                  className={cn(
                    'flex items-center gap-2 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors',
                    isActive
                      ? 'bg-primary/10 text-primary font-semibold'
                      : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                  )}
                >
                  <Icon className={cn('size-3.5', isActive ? 'text-primary' : 'text-muted-foreground')} />
                  <span>{label}</span>
                </button>
              );
            })}
          </nav>

          {/* Right: Quick actions (Theme, Avatar, Sign Out) */}
          <div className="flex items-center gap-1.5 sm:gap-2">
            {/* Theme Toggle */}
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleTheme}
              className="size-8 sm:size-9 text-muted-foreground hover:text-foreground"
              aria-label={dark ? 'Light mode' : 'Dark mode'}
            >
              {dark ? <Sun className="size-4" /> : <Moon className="size-4" />}
            </Button>

            {/* Profile Avatar */}
            <button
              onClick={() => (onOpenProfile ? onOpenProfile() : router.push('/profile'))}
              className="flex size-8 items-center justify-center rounded-full bg-muted text-xs font-bold hover:ring-2 hover:ring-primary transition-all text-foreground"
              title={`Logged in as ${userName} (${role})`}
            >
              {userName
                .split(' ')
                .map(n => n[0])
                .join('')
                .toUpperCase() || 'MM'}
            </button>

            {/* Sign Out */}
            <button
              onClick={handleSignOutAction}
              className="flex items-center gap-1 text-xs font-medium text-muted-foreground hover:text-rose-600 transition-colors px-2 py-1"
              title="Sign Out"
            >
              <LogOut className="size-3.5" />
              <span className="hidden sm:inline">Sign Out</span>
            </button>
          </div>
        </div>
      </header>

      {/* 2. MOBILE BOTTOM NAVIGATION BAR (Fixed at bottom for easy one-thumb reach on mobile) */}
      <nav
        aria-label="Mobile Bottom Navigation"
        className="lg:hidden fixed bottom-0 left-0 right-0 z-40 bg-background/95 backdrop-blur-md border-t px-2 py-1 shadow-lg transition-transform"
      >
        <div className="mx-auto flex max-w-md items-center justify-around">
          {tabs.map(({ id, label, icon: Icon }) => {
            const isActive = currentTab === id;
            return (
              <button
                key={id}
                type="button"
                onClick={() => handleTabClick(id)}
                className={cn(
                  'flex flex-col items-center justify-center flex-1 py-1.5 px-1 rounded-lg transition-colors relative min-h-[48px]',
                  isActive
                    ? 'text-primary font-bold'
                    : 'text-muted-foreground hover:text-foreground font-medium'
                )}
              >
                <div className="relative">
                  <Icon className={cn('size-5', isActive ? 'text-primary scale-110 transition-transform' : 'text-muted-foreground')} />
                  {isActive && (
                    <span className="absolute -top-0.5 -right-0.5 size-1.5 rounded-full bg-primary" />
                  )}
                </div>
                <span className="text-[10px] mt-0.5 tracking-tight truncate max-w-[72px]">
                  {label}
                </span>
              </button>
            );
          })}
        </div>
      </nav>
    </>
  );
}
