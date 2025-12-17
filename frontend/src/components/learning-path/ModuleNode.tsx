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
        return 'bg-green-100 dark:bg-green-900 border-green-500';
      case 'in_progress':
        return 'bg-blue-100 dark:bg-blue-900 border-blue-500';
      case 'available':
        return 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600';
      case 'locked':
        return 'bg-gray-100 dark:bg-gray-900 border-gray-400 dark:border-gray-700';
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
        className={`relative z-10 w-full max-w-md p-6 rounded-2xl border-2 ${getStatusColor()} shadow-lg cursor-pointer transition-all duration-300`}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        onDoubleClick={handleDoubleClick}
        initial={{ opacity: 0, x: -50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, delay: module.order * 0.1 }}
        whileHover={{
          scale: 1.05,
          boxShadow: `0 20px 40px rgba(0,0,0,0.15)`,
        }}
      >
        {/* Module Number Badge */}
        <div
          className="absolute -left-4 top-6 w-12 h-12 rounded-full flex items-center justify-center font-bold text-white shadow-lg"
          style={{ backgroundColor: pathColor }}
        >
          {module.order}
        </div>

        {/* Status Icon */}
        <div className="absolute -right-3 -top-3 text-3xl">
          <motion.div
            animate={{
              scale: module.status === 'in_progress' ? [1, 1.2, 1] : 1,
            }}
            transition={{
              duration: 2,
              repeat: module.status === 'in_progress' ? Infinity : 0,
            }}
          >
            {getStatusIcon()}
          </motion.div>
        </div>

        {/* Content */}
        <div className="pl-6">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
            {module.title}
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            {module.description}
          </p>

          {/* Stats */}
          <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
            <span>📝 {module.exercises_count} exercises</span>
            {module.status === 'completed' && <span className="text-green-600 dark:text-green-400 font-semibold">Completed! 🎉</span>}
            {module.status === 'locked' && <span className="text-gray-400">Complete previous module first</span>}
          </div>
        </div>

        {/* Hover Tooltip */}
        {isHovered && module.status !== 'locked' && (
          <motion.div
            className="absolute -bottom-12 left-1/2 transform -translate-x-1/2 bg-gray-900 dark:bg-gray-700 text-white text-xs px-4 py-2 rounded-lg shadow-lg whitespace-nowrap"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            🖱️ Double click to open this module
            <div className="absolute -top-1 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-gray-900 dark:bg-gray-700 rotate-45" />
          </motion.div>
        )}

        {/* Locked Overlay */}
        {module.status === 'locked' && (
          <div className="absolute inset-0 bg-gray-900 bg-opacity-50 rounded-2xl flex items-center justify-center">
            <div className="text-center">
              <div className="text-4xl mb-2">🔒</div>
              <p className="text-white font-semibold">Locked</p>
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
