'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import { useNodeStore } from '@/stores/nodeStore';
import AppLayout from '@/components/layout/AppLayout';
import { api } from '@/lib/api';

export default function NodeDetailPage({
  params,
}: {
  params: { nodeId: string };
}) {
  const { nodeId } = params;
  const { isAuthenticated, isLoading, loadUser } = useAuthStore();
  const { currentNode, selectNode, startNode } = useNodeStore();
  const router = useRouter();
  const [isStarting, setIsStarting] = useState(false);

  // Load user once on mount
  useEffect(() => {
    loadUser();
  }, []); // Empty deps - only run once

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  useEffect(() => {
    if (isAuthenticated) {
      selectNode(nodeId);
    }
  }, [isAuthenticated, nodeId]); // Removed selectNode from deps

  const handleStartNode = async () => {
    try {
      setIsStarting(true);
      console.log('Starting AI learning session for node:', nodeId);

      // Start AI-driven learning session
      const response = await api.startLearningSession(nodeId);
      console.log('AI session started:', response);

      // Navigate based on AI's decision, always include session_id
      if (response.content_id) {
        // AI generated content - show learning view
        console.log('Navigating to content:', response.content_id);
        router.push(`/learn/${nodeId}?content=${response.content_id}&session=${response.session_id}`);
      } else if (response.exercise_id) {
        // AI jumped straight to exercise
        console.log('Navigating to exercise:', response.exercise_id);
        router.push(`/exercise/${response.exercise_id}?session=${response.session_id}`);
      } else {
        // Default to learning session view with chat
        console.log('Navigating to learning session view');
        router.push(`/learn/${nodeId}?session=${response.session_id}`);
      }
    } catch (error) {
      console.error('Failed to start learning:', error);
      setIsStarting(false);
      // Show error to user
      alert('Failed to start AI learning session. Falling back to basic mode.');
      // Fallback: just mark node as started
      await startNode(nodeId);
      selectNode(nodeId);
    }
  };

  if (isLoading || !currentNode) {
    return (
      <div className="flex h-screen items-center justify-center">
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">
            {currentNode.title}
          </h1>
          <p className="mt-2 text-gray-600">{currentNode.description}</p>

          <div className="mt-4 flex items-center space-x-4">
            <span
              className={`rounded-full px-3 py-1 text-sm ${
                currentNode.difficulty === 'beginner'
                  ? 'bg-green-100 text-green-700'
                  : currentNode.difficulty === 'intermediate'
                  ? 'bg-yellow-100 text-yellow-700'
                  : 'bg-red-100 text-red-700'
              }`}
            >
              {currentNode.difficulty}
            </span>
            <span className="text-sm text-gray-500">
              {currentNode.estimated_duration} minutes
            </span>
          </div>
        </div>

        {/* Content */}
        <div className="rounded-lg bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-gray-800">Introduction</h2>
          <p className="mt-3 text-gray-700">{currentNode.content.introduction}</p>

          <h3 className="mt-6 text-lg font-semibold text-gray-800">
            What You'll Learn
          </h3>
          <ul className="mt-3 list-inside list-disc space-y-1 text-gray-700">
            {currentNode.content.concepts.map((concept, idx) => (
              <li key={idx}>{concept}</li>
            ))}
          </ul>

          <h3 className="mt-6 text-lg font-semibold text-gray-800">
            Practical Applications
          </h3>
          <ul className="mt-3 list-inside list-disc space-y-1 text-gray-700">
            {currentNode.content.practical_applications.map((app, idx) => (
              <li key={idx}>{app}</li>
            ))}
          </ul>
        </div>

        {/* Exercises */}
        <div className="rounded-lg bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-gray-800">Exercises</h2>
          <div className="mt-4 space-y-3">
            {currentNode.exercises?.map((exercise) => (
              <button
                key={exercise.exercise_id}
                onClick={() => router.push(`/exercise/${exercise.exercise_id}`)}
                className="flex w-full items-center justify-between rounded-lg border border-gray-300 p-4 text-left hover:border-primary-500 hover:shadow-sm"
              >
                <div>
                  <h3 className="font-medium text-gray-800">
                    {exercise.title}
                  </h3>
                  <p className="text-sm text-gray-500">{exercise.difficulty}</p>
                </div>
                {exercise.completed && (
                  <span className="text-2xl">✅</span>
                )}
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={handleStartNode}
          disabled={isStarting}
          className="w-full rounded-lg bg-primary-600 py-3 font-medium text-white hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
        >
          {isStarting ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Starting AI Teacher...
            </>
          ) : (
            'Start Learning'
          )}
        </button>
      </div>
    </AppLayout>
  );
}
