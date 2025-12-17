'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';

interface LearningPathCardProps {
  path: {
    id: string;
    title: string;
    description: string;
    modules_count: number;
    progress: number;
    thumbnail: string;
    color: string;
  };
  onBrowse: (pathId: string) => void;
}

export default function LearningPathCard({ path, onBrowse }: LearningPathCardProps) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <motion.div
      className="relative overflow-hidden rounded-2xl bg-white dark:bg-gray-800 shadow-lg hover:shadow-2xl transition-all duration-300 cursor-pointer"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      whileHover={{ scale: 1.02, y: -5 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Gradient Background */}
      <div
        className="absolute inset-0 opacity-10"
        style={{
          background: `linear-gradient(135deg, ${path.color}00 0%, ${path.color} 100%)`
        }}
      />

      {/* Content */}
      <div className="relative p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              {path.title}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {path.description}
            </p>
          </div>

          {/* Emoji/Icon */}
          <div
            className="w-16 h-16 rounded-full flex items-center justify-center text-3xl"
            style={{ backgroundColor: `${path.color}20` }}
          >
            {path.thumbnail}
          </div>
        </div>

        {/* Stats */}
        <div className="flex items-center gap-4 mb-4">
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {path.modules_count} modules
            </span>
          </div>

          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {path.progress}% complete
            </span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-4">
          <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <motion.div
              className="h-full rounded-full"
              style={{ backgroundColor: path.color }}
              initial={{ width: 0 }}
              animate={{ width: `${path.progress}%` }}
              transition={{ duration: 1, delay: 0.3 }}
            />
          </div>
        </div>

        {/* Browse Button */}
        <motion.button
          onClick={() => onBrowse(path.id)}
          className="w-full py-3 rounded-lg font-semibold text-white transition-all"
          style={{ backgroundColor: path.color }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          {isHovered ? '🚀 Start Learning' : '📚 Browse Path'}
        </motion.button>
      </div>

      {/* Hover Effect */}
      <motion.div
        className="absolute inset-0 pointer-events-none"
        initial={{ opacity: 0 }}
        animate={{ opacity: isHovered ? 1 : 0 }}
        transition={{ duration: 0.2 }}
      >
        <div
          className="absolute inset-0 opacity-5"
          style={{
            background: `radial-gradient(circle at 50% 50%, ${path.color} 0%, transparent 70%)`
          }}
        />
      </motion.div>
    </motion.div>
  );
}
