'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import { api } from '@/lib/api';
import AppLayout from '@/components/layout/AppLayout';
import LearningPathCard from '@/components/learning-path/LearningPathCard';

export default function LearningPathsPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading, loadUser } = useAuthStore();
  const [paths, setPaths] = useState<any[]>([]);
  const [pathsLoading, setPathsLoading] = useState(true);
  const [pathsError, setPathsError] = useState<string | null>(null);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  // Fetch learning paths from API
  useEffect(() => {
    const fetchPaths = async () => {
      if (!isAuthenticated) return;

      try {
        setPathsLoading(true);
        setPathsError(null);

        const data = await api.getLearningPaths();
        console.log('📚 Learning paths loaded:', data.paths);
        setPaths(data.paths || []);
      } catch (error: any) {
        console.error('Failed to fetch learning paths:', error);
        setPathsError(error.response?.data?.detail || error.message || 'Failed to load learning paths');
      } finally {
        setPathsLoading(false);
      }
    };

    fetchPaths();
  }, [isAuthenticated]);

  const handleBrowsePath = (pathId: string) => {
    router.push(`/learning-paths/${pathId}`);
  };

  if (isLoading || pathsLoading) {
    return (
      <AppLayout>
        <div className="flex h-full items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">Loading your learning paths...</p>
          </div>
        </div>
      </AppLayout>
    );
  }

  if (pathsError) {
    return (
      <AppLayout>
        <div className="flex h-full items-center justify-center">
          <div className="text-center">
            <div className="text-5xl mb-4">⚠️</div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Failed to Load Learning Paths</h2>
            <p className="text-gray-600 dark:text-gray-400 mb-4">{pathsError}</p>
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          className="text-center mb-8 sm:mb-12 px-4"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 dark:text-white mb-3 sm:mb-4">
            🚀 Your Learning Journey
          </h1>
          <p className="text-base sm:text-lg lg:text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Choose a path and start your adventure in mastering new skills
          </p>
        </motion.div>

        {/* Learning Paths Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-4 sm:gap-6 lg:gap-8 max-w-7xl mx-auto px-4">
          {paths.map((path, index) => (
            <motion.div
              key={path.id}
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <LearningPathCard path={path} onBrowse={handleBrowsePath} />
            </motion.div>
          ))}
        </div>

        {/* AI Suggestion Card */}
        <motion.div
          className="max-w-4xl mx-auto mt-12 p-6 sm:p-8 rounded-2xl bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-2xl"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <div className="flex flex-col sm:flex-row items-center gap-4">
            <div className="text-4xl sm:text-5xl">🤖</div>
            <div className="flex-1 text-center sm:text-left">
              <h3 className="text-xl sm:text-2xl font-bold mb-2">Need a Custom Path?</h3>
              <p className="text-sm sm:text-base text-white/90">
                Tell our AI what you want to learn, and we'll create a personalized learning path just for you!
              </p>
            </div>
            <motion.button
              className="px-6 sm:px-8 py-3 sm:py-4 bg-white text-purple-600 rounded-lg sm:rounded-xl text-sm sm:text-base font-bold shadow-lg hover:shadow-2xl"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => router.push('/dashboard')}
            >
              Chat with AI
            </motion.button>
          </div>
        </motion.div>

        {/* Stats Section */}
        <motion.div
          className="grid grid-cols-3 gap-3 sm:gap-6 max-w-4xl mx-auto mt-8 sm:mt-12"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <div className="text-center p-4 sm:p-6 bg-card dark:bg-card rounded-xl shadow-lg border border-border">
            <div className="text-2xl sm:text-4xl font-bold text-primary mb-1 sm:mb-2">{paths.reduce((acc, p) => acc + (p.total_count || 0), 0)}</div>
            <div className="text-xs sm:text-sm text-muted-foreground">Total Modules</div>
          </div>
          <div className="text-center p-4 sm:p-6 bg-card dark:bg-card rounded-xl shadow-lg border border-border">
            <div className="text-2xl sm:text-4xl font-bold text-green-600 dark:text-green-400 mb-1 sm:mb-2">{paths.reduce((acc, p) => acc + (p.completed_count || 0), 0)}</div>
            <div className="text-xs sm:text-sm text-muted-foreground">Completed</div>
          </div>
          <div className="text-center p-4 sm:p-6 bg-card dark:bg-card rounded-xl shadow-lg border border-border">
            <div className="text-2xl sm:text-4xl font-bold text-blue-600 dark:text-blue-400 mb-1 sm:mb-2">{paths.length}</div>
            <div className="text-xs sm:text-sm text-muted-foreground">Learning Paths</div>
          </div>
        </motion.div>
      </div>
    </AppLayout>
  );
}
