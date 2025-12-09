'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import { api } from '@/lib/api';
import AppLayout from '@/components/layout/AppLayout';

interface DashboardStats {
  overview: {
    exercises_completed: number;
    total_attempts: number;
    success_rate: number;
    streak_days: number;
    total_time_hours: number;
    nodes_completed: number;
  };
  exercises_by_difficulty: {
    [key: string]: { completed: number; total: number };
  };
  weekly_activity: Array<{
    date: string;
    day: string;
    exercises: number;
  }>;
  recent_nodes: Array<{
    id: string;
    title: string;
    difficulty: string;
  }>;
}

export default function ProgressPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuthStore();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  useEffect(() => {
    if (isAuthenticated) {
      loadStats();
    }
  }, [isAuthenticated]);

  const loadStats = async () => {
    try {
      const data = await api.getDashboardStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (isLoading || loading) {
    return (
      <AppLayout>
        <div className="flex h-full items-center justify-center">
          <p>Loading...</p>
        </div>
      </AppLayout>
    );
  }

  if (!stats) {
    return (
      <AppLayout>
        <div className="flex h-full items-center justify-center">
          <p>No data available yet. Start learning to see your progress!</p>
        </div>
      </AppLayout>
    );
  }

  const maxWeeklyExercises = Math.max(
    ...stats.weekly_activity.map((d) => d.exercises),
    1
  );

  return (
    <AppLayout>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-800">Your Progress</h1>

        {/* Overview Cards */}
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
          <div className="rounded-lg bg-primary-50 p-4">
            <p className="text-sm text-primary-700">Exercises</p>
            <p className="mt-1 text-2xl font-bold text-primary-600">
              {stats.overview.exercises_completed}
            </p>
          </div>

          <div className="rounded-lg bg-green-50 p-4">
            <p className="text-sm text-green-700">Success Rate</p>
            <p className="mt-1 text-2xl font-bold text-green-600">
              {stats.overview.success_rate}%
            </p>
          </div>

          <div className="rounded-lg bg-orange-50 p-4">
            <p className="text-sm text-orange-700">Streak</p>
            <p className="mt-1 text-2xl font-bold text-orange-600">
              {stats.overview.streak_days} 🔥
            </p>
          </div>

          <div className="rounded-lg bg-blue-50 p-4">
            <p className="text-sm text-blue-700">Time Spent</p>
            <p className="mt-1 text-2xl font-bold text-blue-600">
              {stats.overview.total_time_hours}h
            </p>
          </div>

          <div className="rounded-lg bg-purple-50 p-4">
            <p className="text-sm text-purple-700">Nodes Done</p>
            <p className="mt-1 text-2xl font-bold text-purple-600">
              {stats.overview.nodes_completed}
            </p>
          </div>

          <div className="rounded-lg bg-gray-100 p-4">
            <p className="text-sm text-gray-700">Attempts</p>
            <p className="mt-1 text-2xl font-bold text-gray-600">
              {stats.overview.total_attempts}
            </p>
          </div>
        </div>

        {/* Weekly Activity Chart */}
        <div className="rounded-lg border border-gray-200 bg-white p-6">
          <h2 className="text-xl font-semibold text-gray-800">
            Weekly Activity
          </h2>
          <div className="mt-6 flex items-end justify-between space-x-2">
            {stats.weekly_activity.map((day, idx) => {
              const height = (day.exercises / maxWeeklyExercises) * 100;
              return (
                <div key={idx} className="flex flex-1 flex-col items-center">
                  <div className="relative w-full">
                    <div
                      className="w-full rounded-t-lg bg-primary-500 transition-all hover:bg-primary-600"
                      style={{
                        height: `${Math.max(height, 4)}px`,
                        minHeight: '4px',
                      }}
                      title={`${day.exercises} exercises`}
                    />
                  </div>
                  <p className="mt-2 text-xs text-gray-600">{day.day}</p>
                  <p className="text-xs font-medium text-gray-800">
                    {day.exercises}
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Progress by Difficulty */}
        <div className="rounded-lg border border-gray-200 bg-white p-6">
          <h2 className="text-xl font-semibold text-gray-800">
            Progress by Difficulty
          </h2>
          <div className="mt-6 space-y-4">
            {Object.entries(stats.exercises_by_difficulty).map(
              ([difficulty, data]) => {
                const percentage =
                  data.total > 0 ? (data.completed / data.total) * 100 : 0;
                return (
                  <div key={difficulty}>
                    <div className="flex items-center justify-between">
                      <span className="capitalize text-gray-700">
                        {difficulty}
                      </span>
                      <span className="text-sm text-gray-600">
                        {data.completed} / {data.total}
                      </span>
                    </div>
                    <div className="mt-2 h-3 overflow-hidden rounded-full bg-gray-200">
                      <div
                        className={`h-full rounded-full transition-all ${
                          difficulty === 'beginner'
                            ? 'bg-green-500'
                            : difficulty === 'intermediate'
                            ? 'bg-yellow-500'
                            : 'bg-red-500'
                        }`}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              }
            )}
          </div>
        </div>

        {/* Recent Nodes */}
        {stats.recent_nodes.length > 0 && (
          <div className="rounded-lg border border-gray-200 bg-white p-6">
            <h2 className="text-xl font-semibold text-gray-800">
              Recently Completed Nodes
            </h2>
            <div className="mt-4 space-y-3">
              {stats.recent_nodes.map((node) => (
                <div
                  key={node.id}
                  className="flex items-center justify-between rounded-lg border border-gray-200 p-3"
                >
                  <div>
                    <h3 className="font-medium text-gray-800">{node.title}</h3>
                    <span
                      className={`mt-1 inline-block rounded-full px-2 py-1 text-xs ${
                        node.difficulty === 'beginner'
                          ? 'bg-green-100 text-green-700'
                          : node.difficulty === 'intermediate'
                          ? 'bg-yellow-100 text-yellow-700'
                          : 'bg-red-100 text-red-700'
                      }`}
                    >
                      {node.difficulty}
                    </span>
                  </div>
                  <span className="text-2xl">✅</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
