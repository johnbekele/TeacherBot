'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { BookOpen, Zap } from 'lucide-react';

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
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={() => onBrowse(path.id)}
      whileHover={{ scale: 1.02, y: -4 }}
      whileTap={{ scale: 0.98 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card
        className="relative overflow-hidden cursor-pointer h-full transition-all duration-200 hover:border-primary/50"
        role="button"
        aria-label={`${path.title} learning path. Click to browse.`}
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            onBrowse(path.id);
          }
        }}
      >
        {/* Gradient Background */}
        <div
          className="absolute inset-0 opacity-5"
          style={{
            background: `linear-gradient(135deg, transparent 0%, ${path.color} 100%)`
          }}
        />

        {/* Content */}
        <div className="relative p-5 sm:p-6">
          {/* Header */}
          <div className="flex items-start justify-between mb-4 gap-3">
            <div className="flex-1 min-w-0">
              <h3 className="text-lg sm:text-xl font-semibold text-foreground mb-2 break-words leading-tight">
                {path.title}
              </h3>
              <p className="text-sm text-muted-foreground line-clamp-2 leading-relaxed">
                {path.description}
              </p>
            </div>

            {/* Emoji/Icon */}
            <div
              className="w-12 h-12 sm:w-14 sm:h-14 rounded-xl flex items-center justify-center text-2xl flex-shrink-0 transition-transform duration-200"
              style={{ backgroundColor: `${path.color}15` }}
              aria-hidden="true"
            >
              {path.thumbnail}
            </div>
          </div>

          {/* Stats */}
          <div className="flex items-center gap-4 mb-4 text-sm">
            <div className="flex items-center gap-1.5 text-muted-foreground">
              <BookOpen className="w-4 h-4" />
              <span>{path.modules_count} modules</span>
            </div>
            <div className="flex items-center gap-1.5 text-muted-foreground">
              <Zap className="w-4 h-4" />
              <span>{path.progress}% complete</span>
            </div>
          </div>

          {/* Progress Bar */}
          <div
            className="mb-4"
            role="progressbar"
            aria-valuenow={path.progress}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label={`${path.title} progress: ${path.progress}%`}
          >
            <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
              <motion.div
                className="h-full rounded-full"
                style={{ backgroundColor: path.color }}
                initial={{ width: 0 }}
                animate={{ width: `${path.progress}%` }}
                transition={{ duration: 0.8, delay: 0.2 }}
              />
            </div>
          </div>

          {/* Browse Button */}
          <Button
            className="w-full"
            style={{
              backgroundColor: path.color,
              color: 'white'
            }}
          >
            {isHovered ? 'Start Learning' : 'Browse Path'}
          </Button>
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
      </Card>
    </motion.div>
  );
}
