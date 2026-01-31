'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import { useChatStore } from '@/stores/chatStore';
import { useChatContext } from '@/contexts/ChatContext';
import AppLayout from '@/components/layout/AppLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import { BookOpen, TrendingUp, Target, Clock, Sparkles, ArrowRight } from 'lucide-react';

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading, user, loadUser } = useAuthStore();
  const { clearChat } = useChatStore();
  const { setContext } = useChatContext();
  const [greeting, setGreeting] = useState('');

  // Load user once on mount
  useEffect(() => {
    loadUser();
  }, []);

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
  }, [isAuthenticated]);

  if (authLoading) {
    return (
      <AppLayout contextType="planning" contextId="dashboard">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8 space-y-3">
            <Skeleton className="h-9 w-64" />
            <Skeleton className="h-5 w-96" />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-8">
            {[1, 2, 3, 4].map((i) => (
              <Card key={i} className="overflow-hidden">
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
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8 animate-fade-in-up">
          <h1 className="text-2xl sm:text-3xl font-bold text-foreground mb-2">
            {greeting}, {user?.full_name?.split(' ')[0] || 'there'}!
          </h1>
          <p className="text-muted-foreground">
            Ready to continue your learning journey?
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-8">
          <Card className="animate-fade-in-up group cursor-default">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Active Courses</CardTitle>
              <div className="p-2.5 bg-primary/10 rounded-lg transition-colors group-hover:bg-primary/15">
                <BookOpen className="w-4 h-4 text-primary" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">0</div>
              <p className="text-xs text-muted-foreground mt-1">Start learning today</p>
            </CardContent>
          </Card>

          <Card className="animate-fade-in-up group cursor-default" style={{ animationDelay: '50ms' }}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Overall Progress</CardTitle>
              <div className="p-2.5 bg-success/10 rounded-lg transition-colors group-hover:bg-success/15">
                <Target className="w-4 h-4 text-success" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">0%</div>
              <p className="text-xs text-muted-foreground mt-1">Track your journey</p>
            </CardContent>
          </Card>

          <Card className="animate-fade-in-up group cursor-default" style={{ animationDelay: '100ms' }}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Completed</CardTitle>
              <div className="p-2.5 bg-info/10 rounded-lg transition-colors group-hover:bg-info/15">
                <TrendingUp className="w-4 h-4 text-info" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">0</div>
              <p className="text-xs text-muted-foreground mt-1">Exercises finished</p>
            </CardContent>
          </Card>

          <Card className="animate-fade-in-up group cursor-default" style={{ animationDelay: '150ms' }}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Time Spent</CardTitle>
              <div className="p-2.5 bg-warning/10 rounded-lg transition-colors group-hover:bg-warning/15">
                <Clock className="w-4 h-4 text-warning" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">0h</div>
              <p className="text-xs text-muted-foreground mt-1">Learning time</p>
            </CardContent>
          </Card>
        </div>

        {/* AI Assistant Card */}
        <Card className="mb-8 animate-fade-in-up overflow-hidden border-primary/20 bg-gradient-to-br from-primary/5 via-transparent to-transparent" style={{ animationDelay: '200ms' }}>
          <CardHeader className="pb-4">
            <div className="flex items-start gap-4">
              <div className="p-3 bg-primary/10 rounded-xl flex-shrink-0 animate-bounce-gentle">
                <Sparkles className="w-6 h-6 text-primary" />
              </div>
              <div className="flex-1 space-y-1">
                <CardTitle className="text-xl sm:text-2xl">AI Learning Assistant</CardTitle>
                <CardDescription className="text-sm sm:text-base leading-relaxed">
                  Tell me what you want to learn, and I'll create a personalized learning path just for you. I can adapt to your pace, track your progress, and provide real-time feedback.
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="bg-muted/50 rounded-xl p-4 border border-border/50">
              <p className="text-sm font-medium text-foreground mb-3">Try asking:</p>
              <ul className="space-y-2.5 text-sm">
                <li className="flex items-center gap-3 group cursor-pointer transition-colors hover:text-primary">
                  <div className="w-1.5 h-1.5 rounded-full bg-primary transition-transform duration-200 group-hover:scale-150"></div>
                  <span>"I want to learn Docker from scratch"</span>
                </li>
                <li className="flex items-center gap-3 group cursor-pointer transition-colors hover:text-primary">
                  <div className="w-1.5 h-1.5 rounded-full bg-primary transition-transform duration-200 group-hover:scale-150"></div>
                  <span>"Create a Kubernetes learning path for me"</span>
                </li>
                <li className="flex items-center gap-3 group cursor-pointer transition-colors hover:text-primary">
                  <div className="w-1.5 h-1.5 rounded-full bg-primary transition-transform duration-200 group-hover:scale-150"></div>
                  <span>"Help me master CI/CD pipelines"</span>
                </li>
              </ul>
            </div>
            <p className="text-sm text-primary font-medium mt-4 flex items-center gap-2 animate-pulse-soft">
              <ArrowRight className="w-4 h-4" />
              Use the chat panel on the right to start
            </p>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
          <Card
            className="cursor-pointer group animate-fade-in-up hover:border-primary/50 transition-all duration-200"
            style={{ animationDelay: '250ms' }}
            onClick={() => router.push('/learning-paths')}
          >
            <CardHeader>
              <CardTitle className="text-lg group-hover:text-primary transition-colors">
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
            className="cursor-pointer group animate-fade-in-up hover:border-primary/50 transition-all duration-200"
            style={{ animationDelay: '300ms' }}
            onClick={() => router.push('/progress')}
          >
            <CardHeader>
              <CardTitle className="text-lg group-hover:text-primary transition-colors">
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
