'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import { api } from '@/lib/api';
import AppLayout from '@/components/layout/AppLayout';
import LearningPathCard from '@/components/learning-path/LearningPathCard';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Loader2, RefreshCw, Sparkles, BookOpen, CheckCircle, Compass } from 'lucide-react';

export default function LearningPathsPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading, loadUser } = useAuthStore();
  const [paths, setPaths] = useState<any[]>([]);
  const [pathsLoading, setPathsLoading] = useState(true);
  const [pathsError, setPathsError] = useState<string | null>(null);

  // Load user once on mount
  useEffect(() => {
    loadUser();
  }, []);

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
        console.log('Learning paths loaded:', data.paths);
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
        <div className="flex h-full items-center justify-center py-20">
          <div className="text-center">
            <Loader2 className="h-10 w-10 animate-spin text-primary mx-auto mb-4" />
            <p className="text-muted-foreground">Loading your learning paths...</p>
          </div>
        </div>
      </AppLayout>
    );
  }

  if (pathsError) {
    return (
      <AppLayout>
        <div className="flex h-full items-center justify-center py-20">
          <Card className="text-center p-8 max-w-md">
            <div className="text-5xl mb-4">
              <span role="img" aria-label="warning">&#9888;&#65039;</span>
            </div>
            <h2 className="text-xl font-bold text-foreground mb-2">Failed to Load Learning Paths</h2>
            <p className="text-muted-foreground mb-6">{pathsError}</p>
            <Button onClick={() => window.location.reload()}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Retry
            </Button>
          </Card>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          className="text-center mb-8 sm:mb-12"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-foreground mb-3">
            Your Learning Journey
          </h1>
          <p className="text-sm sm:text-base lg:text-lg text-muted-foreground max-w-2xl mx-auto">
            Choose a path and start your adventure in mastering new skills
          </p>
        </motion.div>

        {/* Learning Paths Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4 sm:gap-6 mb-10">
          {paths.map((path, index) => (
            <motion.div
              key={path.id}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: index * 0.08 }}
            >
              <LearningPathCard path={path} onBrowse={handleBrowsePath} />
            </motion.div>
          ))}
        </div>

        {/* AI Suggestion Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <Card className="max-w-4xl mx-auto p-6 sm:p-8 bg-gradient-to-br from-primary/10 via-primary/5 to-transparent border-primary/20">
            <div className="flex flex-col sm:flex-row items-center gap-4 sm:gap-6">
              <div className="p-4 bg-primary/10 rounded-2xl">
                <Sparkles className="w-8 h-8 text-primary" />
              </div>
              <div className="flex-1 text-center sm:text-left">
                <h3 className="text-lg sm:text-xl font-semibold text-foreground mb-1">Need a Custom Path?</h3>
                <p className="text-sm sm:text-base text-muted-foreground">
                  Tell our AI what you want to learn, and we'll create a personalized learning path just for you!
                </p>
              </div>
              <Button
                size="lg"
                onClick={() => router.push('/dashboard')}
                className="w-full sm:w-auto"
              >
                Chat with AI
              </Button>
            </div>
          </Card>
        </motion.div>

        {/* Stats Section */}
        <motion.div
          className="grid grid-cols-3 gap-3 sm:gap-6 max-w-3xl mx-auto mt-10"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <Card className="text-center p-4 sm:p-6">
            <div className="flex justify-center mb-2">
              <BookOpen className="w-5 h-5 text-primary" />
            </div>
            <div className="text-xl sm:text-3xl font-bold text-foreground mb-1">
              {paths.reduce((acc, p) => acc + (p.total_count || 0), 0)}
            </div>
            <div className="text-xs sm:text-sm text-muted-foreground">Total Modules</div>
          </Card>
          <Card className="text-center p-4 sm:p-6">
            <div className="flex justify-center mb-2">
              <CheckCircle className="w-5 h-5 text-success" />
            </div>
            <div className="text-xl sm:text-3xl font-bold text-foreground mb-1">
              {paths.reduce((acc, p) => acc + (p.completed_count || 0), 0)}
            </div>
            <div className="text-xs sm:text-sm text-muted-foreground">Completed</div>
          </Card>
          <Card className="text-center p-4 sm:p-6">
            <div className="flex justify-center mb-2">
              <Compass className="w-5 h-5 text-info" />
            </div>
            <div className="text-xl sm:text-3xl font-bold text-foreground mb-1">
              {paths.length}
            </div>
            <div className="text-xs sm:text-sm text-muted-foreground">Learning Paths</div>
          </Card>
        </motion.div>
      </div>
    </AppLayout>
  );
}
