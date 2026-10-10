'use client';

import React from 'react';
import { X } from 'lucide-react';
import { AuthScreen } from './auth-screen';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentRole: 'student' | 'educator';
  currentUser: string;
  onSelectRoleAndUser: (role: 'student' | 'educator', name: string) => void;
}

export function AuthModal({
  isOpen,
  onClose,
  onSelectRoleAndUser
}: AuthModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="relative w-full max-w-[340px]">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 z-10 rounded-md p-1.5 text-muted-foreground hover:bg-muted bg-card border"
          aria-label="Close"
        >
          <X className="size-4" />
        </button>
        <AuthScreen
          initialMode="signin"
          onSuccess={(role, name) => {
            onSelectRoleAndUser(role, name);
            onClose();
          }}
        />
      </div>
    </div>
  );
}
