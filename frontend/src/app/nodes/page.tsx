'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import { useNodeStore } from '@/stores/nodeStore';
import AppLayout from '@/components/layout/AppLayout';

export default function NodesPage() {
  const { isAuthenticated, isLoading, loadUser } = useAuthStore();
  const { nodes, loadNodes } = useNodeStore();
  const router = useRouter();

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  useEffect(() => {
    if (isAuthenticated) {
      loadNodes();
    }
  }, [isAuthenticated, loadNodes]);

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-800">Learning Path</h1>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {nodes.map((node) => (
            <button
              key={node.node_id}
              onClick={() => router.push(`/nodes/${node.node_id}`)}
              disabled={node.locked}
              className={`rounded-lg border p-6 text-left transition-all ${
                node.locked
                  ? 'border-gray-200 bg-gray-50 opacity-50'
                  : 'border-gray-300 bg-white hover:border-primary-500 hover:shadow-md'
              }`}
            >
              <div className="flex items-start justify-between">
                <h3 className="text-lg font-semibold text-gray-800">
                  {node.title}
                </h3>
                {node.locked && <span className="text-2xl">🔒</span>}
              </div>

              <p className="mt-2 text-sm text-gray-600">{node.description}</p>

              <div className="mt-4 flex items-center justify-between text-sm">
                <span
                  className={`rounded-full px-3 py-1 ${
                    node.difficulty === 'beginner'
                      ? 'bg-green-100 text-green-700'
                      : node.difficulty === 'intermediate'
                      ? 'bg-yellow-100 text-yellow-700'
                      : 'bg-red-100 text-red-700'
                  }`}
                >
                  {node.difficulty}
                </span>
                <span className="text-gray-500">
                  {node.estimated_duration} min
                </span>
              </div>

              {node.completion_percentage > 0 && (
                <div className="mt-4">
                  <div className="h-2 w-full rounded-full bg-gray-200">
                    <div
                      className="h-2 rounded-full bg-primary-600"
                      style={{ width: `${node.completion_percentage}%` }}
                    />
                  </div>
                  <p className="mt-1 text-xs text-gray-500">
                    {node.completion_percentage}% complete
                  </p>
                </div>
              )}
            </button>
          ))}
        </div>
      </div>
    </AppLayout>
  );
}
