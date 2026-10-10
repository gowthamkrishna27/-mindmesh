'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Mail,
  GraduationCap,
  LogOut,
  ArrowLeft,
  Check
} from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function ProfilePage() {
  const router = useRouter();
  const [userName, setUserName] = useState('Alex Chen');
  const [role, setRole] = useState<'student' | 'educator'>('student');
  const [isEditing, setIsEditing] = useState(false);
  const [nameInput, setNameInput] = useState('');

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const logged = localStorage.getItem('mindmesh_logged_in') === 'true';
      if (!logged) {
        router.push('/signin?callbackUrl=/profile');
        return;
      }
      const savedUser = localStorage.getItem('mindmesh_user') || 'Alex Chen';
      const savedRole = (localStorage.getItem('mindmesh_role') as 'student' | 'educator') || 'student';
      setUserName(savedUser);
      setNameInput(savedUser);
      setRole(savedRole);
    }
  }, [router]);

  const handleSaveName = (e: React.FormEvent) => {
    e.preventDefault();
    if (nameInput.trim()) {
      setUserName(nameInput.trim());
      setIsEditing(false);
      if (typeof window !== 'undefined') {
        localStorage.setItem('mindmesh_user', nameInput.trim());
        document.cookie = `mindmesh_user=${encodeURIComponent(nameInput.trim())}; path=/; max-age=86400; SameSite=Lax`;
      }
    }
  };

  const handleSignOut = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('mindmesh_logged_in');
      localStorage.removeItem('mindmesh_role');
      localStorage.removeItem('mindmesh_user');
      document.cookie = 'mindmesh_logged_in=; path=/; max-age=0';
      document.cookie = 'mindmesh_role=; path=/; max-age=0';
      document.cookie = 'mindmesh_user=; path=/; max-age=0';
    }
    router.push(role === 'educator' ? '/signin?role=educator' : '/signin');
  };

  const initials = userName
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase() || 'MM';

  const email = role === 'student' ? 'alex.chen@mindmesh.edu' : 'aris.thorne@mindmesh.edu';

  return (
    <div className="min-h-screen bg-background text-foreground p-6 sm:p-8 max-w-xl mx-auto space-y-6">
      {/* Back button */}
      <div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push(role === 'educator' ? '/educator' : '/dashboard')}
          className="text-xs text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="mr-1.5 size-3.5" />
          Back to {role === 'educator' ? 'Educator Portal' : 'Dashboard'}
        </Button>
      </div>

      {/* Main Profile Card */}
      <div className="rounded-2xl border bg-card p-6 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="flex size-14 shrink-0 items-center justify-center rounded-2xl bg-primary text-primary-foreground font-brand text-xl font-bold shadow-sm">
              {initials}
            </div>
            <div>
              {isEditing ? (
                <form onSubmit={handleSaveName} className="flex items-center gap-2">
                  <input
                    type="text"
                    value={nameInput}
                    onChange={e => setNameInput(e.target.value)}
                    className="rounded-md border bg-background px-3 py-1 text-sm font-bold focus:outline-none focus:ring-1 focus:ring-primary"
                    autoFocus
                  />
                  <Button size="icon" type="submit" className="size-7">
                    <Check className="size-3.5" />
                  </Button>
                </form>
              ) : (
                <div className="flex items-center gap-2">
                  <h1 className="text-lg font-bold tracking-tight">{userName}</h1>
                  <button
                    type="button"
                    onClick={() => setIsEditing(true)}
                    className="text-xs text-muted-foreground hover:text-primary transition-colors underline"
                  >
                    Edit
                  </button>
                </div>
              )}
              <p className="text-xs text-muted-foreground flex items-center gap-1.5 mt-1">
                <Mail className="size-3.5 shrink-0" />
                {email}
              </p>
            </div>
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={handleSignOut}
            className="sm:self-start text-xs font-semibold text-destructive hover:text-destructive hover:bg-destructive/10"
          >
            <LogOut className="mr-1.5 size-3.5" />
            Sign Out
          </Button>
        </div>

        {/* Minimal Details Strip */}
        <div className="rounded-xl border bg-muted/40 divide-y text-xs">
          <div className="flex items-center justify-between px-4 py-3">
            <span className="text-muted-foreground">Account Role</span>
            <span className="font-semibold flex items-center gap-1.5 text-foreground">
              <GraduationCap className="size-4 text-primary" />
              {role === 'student' ? 'Undergraduate Student' : 'Faculty Instructor'}
            </span>
          </div>
          <div className="flex items-center justify-between px-4 py-3">
            <span className="text-muted-foreground">Domain</span>
            <span className="font-medium text-foreground">Database Management Systems</span>
          </div>
        </div>
      </div>
    </div>
  );
}
