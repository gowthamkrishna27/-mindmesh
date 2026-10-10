'use client';

import React, { useEffect, useState } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { GraduationCap, Users, AlertCircle, Loader2 } from 'lucide-react';
import { Button } from './ui/button';
import { cn } from '../lib/utils';
import { authenticateUserInDB, registerUserInDB } from '@/lib/supabase';

interface AuthScreenProps {
  initialMode?: 'signin' | 'signup';
  initialRole?: 'student' | 'educator';
  onSuccess?: (role: 'student' | 'educator', name: string) => void;
  isStandalone?: boolean;
}

export function AuthScreen({
  initialMode = 'signin',
  initialRole = 'student',
  onSuccess
}: AuthScreenProps) {
  const router = useRouter();
  const [mode, setMode] = useState<'signin' | 'signup'>(initialMode);
  const [role, setRole] = useState<'student' | 'educator'>(initialRole);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Auto-detect role from URL params (?role=educator or callbackUrl=/educator)
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const roleParam = params.get('role');
      const callbackParam = params.get('callbackUrl');
      if (initialRole === 'educator' || roleParam === 'educator' || callbackParam?.includes('educator')) {
        setRole('educator');
      }
    }
  }, [initialRole]);

  const handleRoleChange = (newRole: 'student' | 'educator') => {
    setRole(newRole);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (mode === 'signin') {
        // Authenticate live against Supabase users table
        const res = await authenticateUserInDB(email, password);
        if (!res.success || !res.user) {
          setError(res.error || 'Authentication failed. Please verify credentials.');
          setLoading(false);
          return;
        }

        const user = res.user;
        const userRole = (user.role as 'student' | 'educator') || role;
        const finalName = user.name || (userRole === 'student' ? 'Alex Chen' : 'Dr. Aris Thorne');

        if (typeof window !== 'undefined') {
          document.cookie = 'mindmesh_logged_in=true; path=/; max-age=86400; SameSite=Lax';
          document.cookie = `mindmesh_role=${userRole}; path=/; max-age=86400; SameSite=Lax`;
          document.cookie = `mindmesh_user=${encodeURIComponent(finalName)}; path=/; max-age=86400; SameSite=Lax`;
          localStorage.setItem('mindmesh_role', userRole);
          localStorage.setItem('mindmesh_user', finalName);
          localStorage.setItem('mindmesh_user_id', user.id);
          localStorage.setItem('mindmesh_email', user.email || email);
          localStorage.setItem('mindmesh_logged_in', 'true');
        }

        if (onSuccess) {
          onSuccess(userRole, finalName);
        } else {
          const params = typeof window !== 'undefined' ? new URLSearchParams(window.location.search) : null;
          const callbackUrl = params?.get('callbackUrl');
          router.push(callbackUrl || (userRole === 'educator' ? '/educator' : '/dashboard'));
        }
      } else {
        // Register new user live into Supabase
        const finalName = name.trim() || (role === 'student' ? 'Alex Chen' : 'Dr. Aris Thorne');
        const res = await registerUserInDB({
          email,
          name: finalName,
          role,
          password
        });

        if (!res.success || !res.user) {
          setError(res.error || 'Registration failed.');
          setLoading(false);
          return;
        }

        const user = res.user;
        const userRole = (user.role as 'student' | 'educator') || role;

        if (typeof window !== 'undefined') {
          document.cookie = 'mindmesh_logged_in=true; path=/; max-age=86400; SameSite=Lax';
          document.cookie = `mindmesh_role=${userRole}; path=/; max-age=86400; SameSite=Lax`;
          document.cookie = `mindmesh_user=${encodeURIComponent(user.name)}; path=/; max-age=86400; SameSite=Lax`;
          localStorage.setItem('mindmesh_role', userRole);
          localStorage.setItem('mindmesh_user', user.name);
          localStorage.setItem('mindmesh_user_id', user.id);
          localStorage.setItem('mindmesh_email', user.email || email);
          localStorage.setItem('mindmesh_logged_in', 'true');
        }

        if (onSuccess) {
          onSuccess(userRole, user.name);
        } else {
          router.push(userRole === 'educator' ? '/educator' : '/dashboard');
        }
      }
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-[75vh] items-center justify-center p-4">
      <div className="w-full max-w-[340px] rounded-xl border bg-card p-5 shadow-sm space-y-4">
        {/* Brand Header */}
        <div className="flex flex-col items-center text-center">
          <div className="flex items-center gap-2">
            <Image
              src="/logo.png"
              alt="Mind Mesh Logo"
              width={32}
              height={22}
              className="h-6 w-auto object-contain"
              priority
            />
            <span className="font-brand text-lg font-extrabold tracking-tight text-foreground">
              Mind Mesh
            </span>
          </div>
          <h1 className="mt-2 text-base font-bold">
            {mode === 'signin' ? 'Sign In' : 'Create Account'}
          </h1>
          <p className="text-[11px] text-muted-foreground mt-0.5">
            {role === 'educator' ? 'Faculty & Instructor Access' : 'Adaptive Learning Platform'}
          </p>
        </div>

        {/* Clean Segmented Role Switcher */}
        <div className="grid grid-cols-2 p-1 bg-muted/60 rounded-lg text-xs font-medium">
          <button
            type="button"
            onClick={() => handleRoleChange('student')}
            className={cn(
              'py-1.5 rounded-md text-xs font-semibold transition-all flex items-center justify-center gap-1.5',
              role === 'student'
                ? 'bg-background text-foreground shadow-xs'
                : 'text-muted-foreground hover:text-foreground'
            )}
          >
            <GraduationCap className="size-3.5" />
            Student
          </button>
          <button
            type="button"
            onClick={() => handleRoleChange('educator')}
            className={cn(
              'py-1.5 rounded-md text-xs font-semibold transition-all flex items-center justify-center gap-1.5',
              role === 'educator'
                ? 'bg-background text-foreground shadow-xs'
                : 'text-muted-foreground hover:text-foreground'
            )}
          >
            <Users className="size-3.5" />
            Educator
          </button>
        </div>

        {/* Error notification */}
        {error && (
          <div className="rounded-lg bg-destructive/10 p-2.5 text-xs text-destructive flex items-center gap-2">
            <AlertCircle className="size-4 shrink-0" />
            <p className="leading-tight">{error}</p>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-2.5">
          {mode === 'signup' && (
            <div>
              <input
                type="text"
                value={name}
                onChange={e => setName(e.target.value)}
                placeholder={role === 'educator' ? 'Full Name (e.g. Dr. Aris Thorne)' : 'Full Name'}
                className="w-full h-8 rounded-md border bg-background px-2.5 text-xs outline-none focus:border-primary transition-colors"
                required
              />
            </div>
          )}

          <div>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="Email address"
              className="w-full h-8 rounded-md border bg-background px-2.5 text-xs outline-none focus:border-primary transition-colors"
              required
            />
          </div>

          <div>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="Password"
              className="w-full h-8 rounded-md border bg-background px-2.5 text-xs outline-none focus:border-primary transition-colors"
              required
            />
          </div>

          <Button
            type="submit"
            size="sm"
            disabled={loading}
            className="w-full h-8 text-xs font-semibold mt-1"
          >
            {loading ? (
              <Loader2 className="size-3.5 animate-spin mr-1.5" />
            ) : null}
            {mode === 'signin'
              ? role === 'educator'
                ? 'Sign In as Educator'
                : 'Sign In as Student'
              : 'Create Account'}
          </Button>
        </form>

        {/* Footer Toggle */}
        <div className="text-center text-[11px] text-muted-foreground pt-1 border-t">
          {mode === 'signin' ? (
            <p>
              No account?{' '}
              <button
                type="button"
                onClick={() => {
                  setMode('signup');
                  setError(null);
                }}
                className="font-semibold text-primary hover:underline"
              >
                Sign up
              </button>
            </p>
          ) : (
            <p>
              Have an account?{' '}
              <button
                type="button"
                onClick={() => {
                  setMode('signin');
                  setError(null);
                }}
                className="font-semibold text-primary hover:underline"
              >
                Sign in
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
