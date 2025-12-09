'use client';

import { useEffect } from 'react';
import { useAuthStore } from '@/stores/authStore';

export default function AuthProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const { loadUser } = useAuthStore();

  useEffect(() => {
    // Load user from localStorage token on mount
    loadUser();
  }, [loadUser]);

  return <>{children}</>;
}
