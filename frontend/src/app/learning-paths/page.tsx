'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import LearningPathCard from '@/components/learning-path/LearningPathCard';

export default function LearningPathsPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading, loadUser } = useAuthStore();
  const [paths, setPaths] = useState([
    {
      id: 'python-basics',
      title: 'Python Mastery',
      description: 'Master Python from basics to advanced concepts',
      modules_count: 12,
      progress: 35,
      thumbnail: '🐍',
      color: '#3776AB'
    },
    {
      id: 'web-dev',
      title: 'Web Development',
      description: 'Build modern web applications with React & Node.js',
      modules_count: 15,
      progress: 20,
      thumbnail: '🌐',
      color: '#61DAFB'
    },
    {
      id: 'data-science',
      title: 'Data Science',
      description: 'Learn data analysis, visualization, and machine learning',
      modules_count: 18,
      progress: 0,
      thumbnail: '📊',
      color: '#FF6F00'
    },
    {
      id: 'algorithms',
      title: 'Algorithms & DSA',
      description: 'Master algorithms and data structures for interviews',
      modules_count: 20,
      progress: 10,
      thumbnail: '🧮',
      color: '#6A1B9A'
    }
  ]);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  const handleBrowsePath = (pathId: string) => {
    router.push(`/learning-paths/${pathId}`);
  };

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading your learning paths...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-4">
            🚀 Your Learning Journey
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400">
            Choose a path and start your adventure in mastering new skills
          </p>
        </motion.div>

        {/* Learning Paths Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-8 max-w-6xl mx-auto">
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
          className="max-w-4xl mx-auto mt-12 p-8 rounded-2xl bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-2xl"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <div className="flex items-center gap-4">
            <div className="text-5xl">🤖</div>
            <div className="flex-1">
              <h3 className="text-2xl font-bold mb-2">Need a Custom Path?</h3>
              <p className="text-white/90">
                Tell our AI what you want to learn, and we'll create a personalized learning path just for you!
              </p>
            </div>
            <motion.button
              className="px-8 py-4 bg-white text-purple-600 rounded-xl font-bold shadow-lg hover:shadow-2xl"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => router.push('/create-path')}
            >
              Create Path
            </motion.button>
          </div>
        </motion.div>

        {/* Stats Section */}
        <motion.div
          className="grid grid-cols-3 gap-6 max-w-4xl mx-auto mt-12"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <div className="text-center p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg">
            <div className="text-4xl font-bold text-primary-600 mb-2">65</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Total Modules</div>
          </div>
          <div className="text-center p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg">
            <div className="text-4xl font-bold text-green-600 mb-2">23</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Completed</div>
          </div>
          <div className="text-center p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg">
            <div className="text-4xl font-bold text-blue-600 mb-2">4</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">In Progress</div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
