'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import { api } from '@/lib/api';
import AppLayout from '@/components/layout/AppLayout';
import ModuleNode from '@/components/learning-path/ModuleNode';

export default function LearningPathDetailPage({ params }: { params: { pathId: string } }) {
  const router = useRouter();
  const { isAuthenticated, isLoading, loadUser } = useAuthStore();
  const [path, setPath] = useState<any>(null);
  const [pathLoading, setPathLoading] = useState(true);
  const [pathError, setPathError] = useState<string | null>(null);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  // Fetch learning path details from API
  useEffect(() => {
    const fetchPathDetail = async () => {
      if (!isAuthenticated) return;

      try {
        setPathLoading(true);
        setPathError(null);

        const data = await api.getLearningPathDetail(params.pathId);
        console.log('📚 Path details loaded:', data);
        setPath(data);
      } catch (error: any) {
        console.error('Failed to fetch path details:', error);
        setPathError(error.response?.data?.detail || error.message || 'Failed to load path');
      } finally {
        setPathLoading(false);
      }
    };

    fetchPathDetail();
  }, [isAuthenticated, params.pathId]);

  if (isLoading || pathLoading) {
    return (
      <AppLayout>
        <div className="flex h-full items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">Loading learning path...</p>
          </div>
        </div>
      </AppLayout>
    );
  }

  if (pathError || !path) {
    return (
      <AppLayout>
        <div className="flex h-full items-center justify-center">
          <div className="text-center">
            <div className="text-5xl mb-4">⚠️</div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Failed to Load Path</h2>
            <p className="text-gray-600 dark:text-gray-400 mb-4">{pathError || 'Path not found'}</p>
            <button
              onClick={() => router.push('/learning-paths')}
              className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Back to Learning Paths
            </button>
          </div>
        </div>
      </AppLayout>
    );
  }

  const progress = path.progress || 0;
  const completedCount = path.completed_count || 0;

  return (
    <AppLayout>
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Back Button */}
        <motion.button
          onClick={() => router.push('/learning-paths')}
          className="mb-6 sm:mb-8 flex items-center gap-2 text-sm sm:text-base text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-lg p-2"
          whileHover={{ x: -5 }}
          aria-label="Back to learning paths"
        >
          <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          <span className="hidden sm:inline">Back to Learning Paths</span>
          <span className="inline sm:hidden">Back</span>
        </motion.button>

        {/* Path Header */}
        <motion.div
          className="mb-8 sm:mb-12"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 sm:gap-6 mb-6">
            <div
              className="w-16 h-16 sm:w-20 sm:h-20 rounded-xl sm:rounded-2xl flex items-center justify-center text-3xl sm:text-4xl shadow-lg flex-shrink-0"
              style={{ backgroundColor: `${path.color}20` }}
              aria-hidden="true"
            >
              {path.thumbnail}
            </div>
            <div className="flex-1 min-w-0">
              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 dark:text-white mb-2 break-words">
                {path.title}
              </h1>
              <p className="text-base sm:text-lg lg:text-xl text-gray-600 dark:text-gray-400">
                {path.description}
              </p>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                Overall Progress
              </span>
              <span className="text-sm font-bold" style={{ color: path.color }}>
                {progress}%
              </span>
            </div>
            <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <motion.div
                className="h-full rounded-full"
                style={{ backgroundColor: path.color }}
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 1.5, ease: 'easeOut' }}
              />
            </div>
          </div>

          {/* Stats */}
          <div className="flex flex-wrap gap-3 sm:gap-6 text-xs sm:text-sm text-gray-600 dark:text-gray-400">
            <span>📚 {path.total_count} modules</span>
            <span>✅ {completedCount} completed</span>
            <span>⏳ {path.modules?.filter((m: any) => m.status === 'in_progress').length || 0} in progress</span>
          </div>
        </motion.div>

        {/* Module Thread */}
        <div className="max-w-2xl mx-auto space-y-6 sm:space-y-8">
          {path.modules?.map((module: any, index: number) => (
            <ModuleNode
              key={module.id}
              module={module}
              pathColor={path.color}
              isLast={index === path.modules.length - 1}
            />
          )) || (
            <div className="text-center text-gray-500 dark:text-gray-400">
              No modules found for this path.
            </div>
          )}
        </div>

        {/* Completion Message */}
        {progress === 100 && (
          <motion.div
            className="max-w-2xl mx-auto mt-8 sm:mt-12 p-6 sm:p-8 rounded-xl sm:rounded-2xl bg-gradient-to-r from-green-400 to-blue-500 text-white shadow-2xl text-center"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6 }}
            role="status"
            aria-live="polite"
          >
            <div className="text-5xl sm:text-6xl mb-3 sm:mb-4">🎉</div>
            <h2 className="text-2xl sm:text-3xl font-bold mb-2">Congratulations!</h2>
            <p className="text-lg sm:text-xl mb-4 sm:mb-6">You've completed the entire {path.title} path!</p>
            <motion.button
              className="px-6 sm:px-8 py-3 sm:py-4 bg-white text-blue-600 rounded-lg sm:rounded-xl text-sm sm:text-base font-bold shadow-lg focus:outline-none focus:ring-4 focus:ring-white"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              aria-label="Get your certificate"
            >
              Get Your Certificate 🏆
            </motion.button>
          </motion.div>
        )}
      </div>
    </AppLayout>
  );
}
