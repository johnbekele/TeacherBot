'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';

interface Module {
  id: string;
  title: string;
  description: string;
  order: number;
  status: 'locked' | 'available' | 'in_progress' | 'completed';
  exercises_count: number;
}

interface ModuleNodeProps {
  module: Module;
  pathColor: string;
  isLast: boolean;
}

export default function ModuleNode({ module, pathColor, isLast }: ModuleNodeProps) {
  const [isHovered, setIsHovered] = useState(false);
  const router = useRouter();

  const handleDoubleClick = () => {
    if (module.status !== 'locked') {
      router.push(`/nodes/${module.id}`);
    }
  };

  const getStatusIcon = () => {
    switch (module.status) {
      case 'completed':
        return '✅';
      case 'in_progress':
        return '⏳';
      case 'available':
        return '🔓';
      case 'locked':
        return '🔒';
    }
  };

  const getStatusColor = () => {
    switch (module.status) {
      case 'completed':
        return 'bg-green-50 dark:bg-green-900/30 border-green-500 dark:border-green-600';
      case 'in_progress':
        return 'bg-blue-50 dark:bg-blue-900/30 border-blue-500 dark:border-blue-600';
      case 'available':
        return 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600';
      case 'locked':
        return 'bg-gray-50 dark:bg-gray-900/50 border-gray-300 dark:border-gray-700';
    }
  };

  return (
    <div className="relative flex items-center">
      {/* Connection Line to Previous Node */}
      {!isLast && (
        <motion.div
          className="absolute left-8 top-24 w-0.5 h-20 bg-gradient-to-b from-gray-300 to-gray-400 dark:from-gray-600 dark:to-gray-700"
          initial={{ height: 0 }}
          animate={{ height: 80 }}
          transition={{ duration: 0.5, delay: module.order * 0.1 }}
        />
      )}

      {/* Module Card */}
      <motion.div
        className={`relative z-10 w-full max-w-md p-4 sm:p-6 rounded-xl sm:rounded-2xl border-2 ${getStatusColor()} shadow-lg cursor-pointer transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-primary-500 active:scale-[0.98]`}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        onClick={handleDoubleClick}
        initial={{ opacity: 0, x: -50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, delay: module.order * 0.1 }}
        whileHover={{
          scale: module.status === 'locked' ? 1 : 1.03,
          boxShadow: module.status === 'locked' ? undefined : `0 20px 40px rgba(0,0,0,0.15)`,
        }}
        whileTap={{ scale: module.status === 'locked' ? 1 : 0.98 }}
        role="button"
        aria-label={`${module.title} module - ${module.status}. Click to open.`}
        tabIndex={module.status === 'locked' ? -1 : 0}
        onKeyDown={(e) => {
          if ((e.key === 'Enter' || e.key === ' ') && module.status !== 'locked') {
            e.preventDefault();
            handleDoubleClick();
          }
        }}
      >
        {/* Module Number Badge */}
        <div
          className="absolute -left-3 sm:-left-4 top-4 sm:top-6 w-10 h-10 sm:w-12 sm:h-12 rounded-full flex items-center justify-center text-sm sm:text-base font-bold text-white shadow-lg"
          style={{ backgroundColor: pathColor }}
          aria-hidden="true"
        >
          {module.order}
        </div>

        {/* Status Icon */}
        <div className="absolute -right-2 sm:-right-3 -top-2 sm:-top-3 text-2xl sm:text-3xl">
          <motion.div
            animate={{
              scale: module.status === 'in_progress' ? [1, 1.2, 1] : 1,
            }}
            transition={{
              duration: 2,
              repeat: module.status === 'in_progress' ? Infinity : 0,
            }}
            aria-label={`Status: ${module.status.replace('_', ' ')}`}
          >
            {getStatusIcon()}
          </motion.div>
        </div>

        {/* Content */}
        <div className="pl-4 sm:pl-6">
          <h3 className="text-lg sm:text-xl font-bold text-gray-900 dark:text-white mb-2 break-words">
            {module.title}
          </h3>
          <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mb-3 sm:mb-4 line-clamp-2">
            {module.description}
          </p>

          {/* Stats */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 sm:gap-4 text-xs text-gray-500 dark:text-gray-400">
            <span>📝 {module.exercises_count} exercises</span>
            {module.status === 'completed' && <span className="text-green-600 dark:text-green-400 font-semibold">Completed! 🎉</span>}
            {module.status === 'locked' && <span className="text-gray-400">Complete previous module first</span>}
          </div>
        </div>

        {/* Hover Tooltip - Hidden on mobile, shown on hover for desktop */}
        {isHovered && module.status !== 'locked' && (
          <motion.div
            className="hidden sm:block absolute -bottom-14 left-1/2 transform -translate-x-1/2 bg-gray-900 dark:bg-gray-700 text-white text-xs px-4 py-2 rounded-lg shadow-xl whitespace-nowrap z-50"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            role="tooltip"
            style={{ pointerEvents: 'none' }}
          >
            Click to open this module
            <div className="absolute -top-1 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-gray-900 dark:bg-gray-700 rotate-45" />
          </motion.div>
        )}

        {/* Locked Overlay */}
        {module.status === 'locked' && (
          <div className="absolute inset-0 bg-gray-900 bg-opacity-50 rounded-xl sm:rounded-2xl flex items-center justify-center" aria-label="Module locked">
            <div className="text-center">
              <div className="text-3xl sm:text-4xl mb-2">🔒</div>
              <p className="text-white text-sm sm:text-base font-semibold">Locked</p>
            </div>
          </div>
        )}

        {/* Completion Animation */}
        {module.status === 'completed' && (
          <motion.div
            className="absolute inset-0 pointer-events-none"
            initial={{ opacity: 0 }}
            animate={{ opacity: [0, 1, 0] }}
            transition={{ duration: 2, delay: 0.5 }}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-green-400 to-blue-500 opacity-20 rounded-2xl" />
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}
