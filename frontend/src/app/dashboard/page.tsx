'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import { useChatStore } from '@/stores/chatStore';
import { useChatContext } from '@/contexts/ChatContext';
import AppLayout from '@/components/layout/AppLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { BookOpen, TrendingUp, Target, Clock, Sparkles, ArrowRight } from 'lucide-react';

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading, user, loadUser } = useAuthStore();
  const { clearChat } = useChatStore();
  const { setContext } = useChatContext();
  const [greeting, setGreeting] = useState('');

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, authLoading, router]);

  // Set context to planning mode when entering dashboard
  useEffect(() => {
    if (isAuthenticated) {
      clearChat();
      setContext('planning', 'dashboard');

      // Set time-based greeting
      const hour = new Date().getHours();
      if (hour < 12) setGreeting('Good morning');
      else if (hour < 18) setGreeting('Good afternoon');
      else setGreeting('Good evening');
    }
  }, [isAuthenticated, clearChat, setContext]);

  if (authLoading) {
    return (
      <AppLayout contextType="planning" contextId="dashboard">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8 space-y-2">
            <Skeleton className="h-8 w-64" />
            <Skeleton className="h-4 w-96" />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[1, 2, 3, 4].map((i) => (
              <Card key={i}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-10 w-10 rounded-lg" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-8 w-16 mb-2" />
                  <Skeleton className="h-3 w-20" />
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout contextType="planning" contextId="dashboard">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8 animate-slide-up">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {greeting}, {user?.full_name?.split(' ')[0] || 'there'}!
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Ready to continue your learning journey?
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="animate-slide-up hover:scale-[1.02] transition-all duration-300">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Courses</CardTitle>
              <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                <BookOpen className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">0</div>
              <p className="text-xs text-muted-foreground">Start learning today</p>
            </CardContent>
          </Card>

          <Card className="animate-slide-up hover:scale-[1.02] transition-all duration-300" style={{ animationDelay: '100ms' }}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Overall Progress</CardTitle>
              <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                <Target className="w-4 h-4 text-green-600 dark:text-green-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">0%</div>
              <p className="text-xs text-muted-foreground">Track your journey</p>
            </CardContent>
          </Card>

          <Card className="animate-slide-up hover:scale-[1.02] transition-all duration-300" style={{ animationDelay: '200ms' }}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Completed</CardTitle>
              <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                <TrendingUp className="w-4 h-4 text-purple-600 dark:text-purple-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">0</div>
              <p className="text-xs text-muted-foreground">Exercises finished</p>
            </CardContent>
          </Card>

          <Card className="animate-slide-up hover:scale-[1.02] transition-all duration-300" style={{ animationDelay: '300ms' }}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Time Spent</CardTitle>
              <div className="p-2 bg-orange-100 dark:bg-orange-900/30 rounded-lg">
                <Clock className="w-4 h-4 text-orange-600 dark:text-orange-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">0h</div>
              <p className="text-xs text-muted-foreground">Learning time</p>
            </CardContent>
          </Card>
        </div>

        {/* AI Assistant Card */}
        <Card className="mb-8 bg-gradient-to-br from-primary/10 to-transparent animate-slide-up border-primary/20" style={{ animationDelay: '400ms' }}>
          <CardHeader>
            <div className="flex items-start gap-4">
              <div className="p-3 bg-primary/10 rounded-lg flex-shrink-0 animate-float">
                <Sparkles className="w-6 h-6 text-primary" />
              </div>
              <div className="flex-1">
                <CardTitle className="text-2xl mb-2">AI Learning Assistant</CardTitle>
                <CardDescription className="text-base">
                  Tell me what you want to learn, and I'll create a personalized learning path just for you. I can adapt to your pace, track your progress, and provide real-time feedback.
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="bg-card rounded-lg p-4 border shadow-sm">
              <p className="text-sm font-medium mb-3">Try asking:</p>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2 group cursor-pointer">
                  <div className="w-1.5 h-1.5 rounded-full bg-primary transition-transform duration-300 group-hover:scale-150"></div>
                  <span className="group-hover:text-primary transition-colors">"I want to learn Docker from scratch"</span>
                </li>
                <li className="flex items-center gap-2 group cursor-pointer">
                  <div className="w-1.5 h-1.5 rounded-full bg-primary transition-transform duration-300 group-hover:scale-150"></div>
                  <span className="group-hover:text-primary transition-colors">"Create a Kubernetes learning path for me"</span>
                </li>
                <li className="flex items-center gap-2 group cursor-pointer">
                  <div className="w-1.5 h-1.5 rounded-full bg-primary transition-transform duration-300 group-hover:scale-150"></div>
                  <span className="group-hover:text-primary transition-colors">"Help me master CI/CD pipelines"</span>
                </li>
              </ul>
            </div>
            <p className="text-sm text-primary font-medium mt-4 flex items-center gap-2 animate-pulse">
              <ArrowRight className="w-4 h-4" />
              Use the chat panel on the right to start →
            </p>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card
            className="cursor-pointer group animate-slide-up hover:border-primary transition-all duration-300 hover:shadow-lg"
            style={{ animationDelay: '500ms' }}
            onClick={() => router.push('/learning-paths')}
          >
            <CardHeader>
              <CardTitle className="group-hover:text-primary transition-colors">
                Browse Learning Paths
              </CardTitle>
              <CardDescription>
                Explore pre-built learning paths for popular DevOps tools and technologies
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-sm font-medium text-primary flex items-center gap-2 group-hover:gap-3 transition-all">
                Explore
                <ArrowRight className="w-4 h-4" />
              </div>
            </CardContent>
          </Card>

          <Card
            className="cursor-pointer group animate-slide-up hover:border-primary transition-all duration-300 hover:shadow-lg"
            style={{ animationDelay: '600ms' }}
            onClick={() => router.push('/progress')}
          >
            <CardHeader>
              <CardTitle className="group-hover:text-primary transition-colors">
                View Progress
              </CardTitle>
              <CardDescription>
                Track your learning journey, achievements, and areas for improvement
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-sm font-medium text-primary flex items-center gap-2 group-hover:gap-3 transition-all">
                View Stats
                <ArrowRight className="w-4 h-4" />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}
