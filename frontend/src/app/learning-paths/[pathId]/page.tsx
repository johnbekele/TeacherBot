'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import ModuleNode from '@/components/learning-path/ModuleNode';

export default function LearningPathDetailPage({ params }: { params: { pathId: string } }) {
  const router = useRouter();
  const { isAuthenticated, isLoading, loadUser } = useAuthStore();

  // Mock data - will be replaced with API call
  const [path, setPath] = useState({
    id: params.pathId,
    title: 'Python Mastery',
    description: 'Complete Python learning journey from basics to advanced',
    color: '#3776AB',
    modules: [
      {
        id: 'py-basics-1',
        title: 'Python Basics',
        description: 'Variables, data types, and basic operations',
        order: 1,
        status: 'completed' as const,
        exercises_count: 8
      },
      {
        id: 'py-control-2',
        title: 'Control Flow',
        description: 'If statements, loops, and conditionals',
        order: 2,
        status: 'completed' as const,
        exercises_count: 12
      },
      {
        id: 'py-functions-3',
        title: 'Functions & Modules',
        description: 'Creating and using functions, importing modules',
        order: 3,
        status: 'in_progress' as const,
        exercises_count: 10
      },
      {
        id: 'py-data-4',
        title: 'Data Structures',
        description: 'Lists, dictionaries, sets, and tuples',
        order: 4,
        status: 'available' as const,
        exercises_count: 15
      },
      {
        id: 'py-oop-5',
        title: 'Object-Oriented Programming',
        description: 'Classes, objects, inheritance, and polymorphism',
        order: 5,
        status: 'locked' as const,
        exercises_count: 14
      },
      {
        id: 'py-files-6',
        title: 'File Handling',
        description: 'Reading and writing files, working with JSON and CSV',
        order: 6,
        status: 'locked' as const,
        exercises_count: 10
      },
      {
        id: 'py-advanced-7',
        title: 'Advanced Topics',
        description: 'Decorators, generators, and context managers',
        order: 7,
        status: 'locked' as const,
        exercises_count: 12
      }
    ]
  });

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  const completedCount = path.modules.filter(m => m.status === 'completed').length;
  const progress = Math.round((completedCount / path.modules.length) * 100);

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading learning path...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="container mx-auto px-4 py-12">
        {/* Back Button */}
        <motion.button
          onClick={() => router.push('/learning-paths')}
          className="mb-8 flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
          whileHover={{ x: -5 }}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Learning Paths
        </motion.button>

        {/* Path Header */}
        <motion.div
          className="mb-12"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center gap-6 mb-6">
            <div
              className="w-20 h-20 rounded-2xl flex items-center justify-center text-4xl shadow-lg"
              style={{ backgroundColor: `${path.color}20` }}
            >
              🐍
            </div>
            <div className="flex-1">
              <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-2">
                {path.title}
              </h1>
              <p className="text-xl text-gray-600 dark:text-gray-400">
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
          <div className="flex gap-6 text-sm text-gray-600 dark:text-gray-400">
            <span>📚 {path.modules.length} modules</span>
            <span>✅ {completedCount} completed</span>
            <span>⏳ {path.modules.filter(m => m.status === 'in_progress').length} in progress</span>
          </div>
        </motion.div>

        {/* Module Thread */}
        <div className="max-w-2xl mx-auto space-y-8">
          {path.modules.map((module, index) => (
            <ModuleNode
              key={module.id}
              module={module}
              pathColor={path.color}
              isLast={index === path.modules.length - 1}
            />
          ))}
        </div>

        {/* Completion Message */}
        {progress === 100 && (
          <motion.div
            className="max-w-2xl mx-auto mt-12 p-8 rounded-2xl bg-gradient-to-r from-green-400 to-blue-500 text-white shadow-2xl text-center"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6 }}
          >
            <div className="text-6xl mb-4">🎉</div>
            <h2 className="text-3xl font-bold mb-2">Congratulations!</h2>
            <p className="text-xl mb-6">You've completed the entire {path.title} path!</p>
            <motion.button
              className="px-8 py-4 bg-white text-blue-600 rounded-xl font-bold shadow-lg"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Get Your Certificate 🏆
            </motion.button>
          </motion.div>
        )}
      </div>
    </div>
  );
}
