'use client';

import React, { useState } from 'react';
import {
  X,
  Mail,
  GraduationCap,
  LogOut,
  Check
} from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
  userName: string;
  role: 'student' | 'educator';
  onUpdateName: (newName: string) => void;
  onSignOut: () => void;
}

export function ProfileModal({
  isOpen,
  onClose,
  userName,
  role,
  onUpdateName,
  onSignOut,
}: ProfileModalProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [nameInput, setNameInput] = useState(userName);

  if (!isOpen) return null;

  const handleSaveName = (e: React.FormEvent) => {
    e.preventDefault();
    if (nameInput.trim()) {
      onUpdateName(nameInput.trim());
      setIsEditing(false);
    }
  };

  const initials = userName
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase() || 'MM';

  const email =
    (typeof window !== 'undefined' ? localStorage.getItem('mindmesh_email') : null) ||
    (role === 'student' ? 'student@mindmesh.edu' : 'educator@mindmesh.edu');
  const roleLabel = role === 'student' ? 'Student' : 'Educator';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div
        className="relative w-full max-w-sm rounded-xl border bg-card p-5 shadow-lg space-y-5 animate-in zoom-in-95 duration-200"
        role="dialog"
        aria-modal="true"
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-md p-1 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
          aria-label="Close profile modal"
        >
          <X className="size-4" />
        </button>

        {/* User Card */}
        <div className="flex items-center gap-3.5 pt-1">
          <div className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-primary text-primary-foreground font-brand text-base font-bold">
            {initials}
          </div>
          <div className="min-w-0 flex-1">
            {isEditing ? (
              <form onSubmit={handleSaveName} className="flex items-center gap-1.5">
                <input
                  type="text"
                  value={nameInput}
                  onChange={e => setNameInput(e.target.value)}
                  className="w-full rounded border bg-background px-2 py-0.5 text-sm font-semibold focus:outline-none focus:ring-1 focus:ring-primary"
                  autoFocus
                />
                <Button size="icon" type="submit" className="size-6 shrink-0">
                  <Check className="size-3" />
                </Button>
              </form>
            ) : (
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold tracking-tight truncate">{userName}</h2>
                <button
                  type="button"
                  onClick={() => setIsEditing(true)}
                  className="text-xs text-muted-foreground hover:text-foreground transition-colors"
                >
                  Edit
                </button>
              </div>
            )}
            <p className="text-xs text-muted-foreground flex items-center gap-1 truncate mt-0.5">
              <Mail className="size-3 shrink-0" />
              <span className="truncate">{email}</span>
            </p>
          </div>
        </div>

        {/* Minimal Details Strip */}
        <div className="rounded-lg border bg-muted/40 divide-y text-xs">
          <div className="flex items-center justify-between px-3 py-2">
            <span className="text-muted-foreground">Account Role</span>
            <span className="font-semibold flex items-center gap-1">
              <GraduationCap className="size-3.5 text-primary" />
              {roleLabel}
            </span>
          </div>
          <div className="flex items-center justify-between px-3 py-2">
            <span className="text-muted-foreground">Domain</span>
            <span className="font-medium text-foreground">Database Management Systems</span>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-between pt-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="text-xs"
          >
            Close
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              onClose();
              onSignOut();
            }}
            className="text-xs text-destructive hover:text-destructive hover:bg-destructive/10"
          >
            <LogOut className="mr-1.5 size-3.5" />
            Sign Out
          </Button>
        </div>
      </div>
    </div>
  );
}
