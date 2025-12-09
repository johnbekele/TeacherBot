'use client';

import { Suspense, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import AppLayout from '@/components/layout/AppLayout';
import ExerciseView from '@/components/exercise/ExerciseView';

function ExercisePageContent({
  exerciseId,
}: {
  exerciseId: string;
}) {
  const searchParams = useSearchParams();
  const { isAuthenticated, isLoading, loadUser } = useAuthStore();
  const router = useRouter();

  // Get session ID from URL
  const sessionId = searchParams.get('session');

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  // Handle AI navigation actions
  const handleActionReceived = (action: any) => {
    console.log('AI Action received in exercise:', action);
    if (action.type === 'show_exercise' && action.data.exercise_id) {
      const url = `/exercise/${action.data.exercise_id}${sessionId ? `?session=${sessionId}` : ''}`;
      router.push(url);
    } else if (action.type === 'display_content' && action.data.content_id) {
      const nodeId = searchParams.get('nodeId') || 'unknown';
      const url = `/learn/${nodeId}?content=${action.data.content_id}${sessionId ? `&session=${sessionId}` : ''}`;
      router.push(url);
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <AppLayout
      sessionId={sessionId || undefined}
      contextType="exercise"
      contextId={exerciseId}
      onActionReceived={handleActionReceived}
    >
      <ExerciseView exerciseId={exerciseId} sessionId={sessionId || undefined} />
    </AppLayout>
  );
}

export default function ExercisePage({
  params,
}: {
  params: { exerciseId: string };
}) {
  const { exerciseId } = params;

  return (
    <Suspense fallback={
      <div className="flex h-screen items-center justify-center">
        <p>Loading exercise...</p>
      </div>
    }>
      <ExercisePageContent exerciseId={exerciseId} />
    </Suspense>
  );
}
