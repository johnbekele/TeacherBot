'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/stores/authStore';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Label } from '@/components/ui/label';
import { Card } from '@/components/ui/Card';
import { Mail, Lock, GraduationCap, ArrowRight, Loader2, Sparkles, Target, Zap } from 'lucide-react';
import { toast } from 'sonner';

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading } = useAuthStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login({ email, password });
      toast.success('Welcome back!');
      router.push('/dashboard');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    }
  };

  return (
    <div className="min-h-screen bg-background flex">
      {/* Left side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-card p-12 flex-col justify-between border-r border-border animate-fade-in">
        <div>
          <div className="flex items-center gap-3 mb-12 group cursor-pointer" onClick={() => router.push('/')}>
            <div className="flex items-center justify-center w-10 h-10 bg-primary rounded-xl transition-all duration-300 group-hover:shadow-primary group-hover:scale-105">
              <GraduationCap className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="text-2xl font-semibold text-foreground">
              Teacherbot
            </span>
          </div>

          <div className="max-w-md">
            <h1 className="text-3xl lg:text-4xl font-bold text-foreground mb-6 animate-fade-in-up">
              Master DevOps with AI-Powered Learning
            </h1>
            <p className="text-lg text-muted-foreground mb-8 animate-fade-in-up" style={{ animationDelay: '50ms' }}>
              Personalized learning paths, intelligent feedback, and adaptive exercises designed just for you.
            </p>

            <div className="space-y-5">
              <div className="flex items-start gap-4 animate-fade-in-up group" style={{ animationDelay: '100ms' }}>
                <div className="p-2 bg-primary/10 rounded-lg transition-colors group-hover:bg-primary/15">
                  <Sparkles className="w-4 h-4 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground">AI-Powered Path Creation</h3>
                  <p className="text-sm text-muted-foreground">Custom learning paths based on your goals and skill level</p>
                </div>
              </div>
              <div className="flex items-start gap-4 animate-fade-in-up group" style={{ animationDelay: '150ms' }}>
                <div className="p-2 bg-primary/10 rounded-lg transition-colors group-hover:bg-primary/15">
                  <Target className="w-4 h-4 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground">Interactive Exercises</h3>
                  <p className="text-sm text-muted-foreground">Hands-on practice with real-time feedback</p>
                </div>
              </div>
              <div className="flex items-start gap-4 animate-fade-in-up group" style={{ animationDelay: '200ms' }}>
                <div className="p-2 bg-primary/10 rounded-lg transition-colors group-hover:bg-primary/15">
                  <Zap className="w-4 h-4 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground">Adaptive Learning</h3>
                  <p className="text-sm text-muted-foreground">System learns from your performance and adapts accordingly</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        <p className="text-sm text-muted-foreground">
          developed by <a href="https://github.com/johnbekele/myteacher/tree/main" className="text-primary hover:text-primary/80 transition-colors hover:underline decoration-2 underline-offset-2">Yohans Bekele</a>
        </p>
        <p className="text-sm text-muted-foreground">
          © 2025 Teacherbot. All rights reserved.
        </p>
      </div>

      {/* Right side - Login form */}
      <div className="flex-1 flex items-center justify-center p-6 sm:p-8 animate-fade-in" style={{ animationDelay: '100ms' }}>
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="lg:hidden flex items-center gap-3 mb-8">
            <div className="flex items-center justify-center w-10 h-10 bg-primary rounded-xl">
              <GraduationCap className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="text-2xl font-semibold text-foreground">
              Teacherbot
            </span>
          </div>

          {/* Theme toggle */}
          <div className="flex justify-end mb-8">
            <ThemeToggle />
          </div>

          {/* Header */}
          <div className="mb-8 animate-fade-in-up">
            <h2 className="text-2xl sm:text-3xl font-bold text-foreground mb-2">
              Welcome back
            </h2>
            <p className="text-muted-foreground">
              Sign in to continue your learning journey
            </p>
          </div>

          {/* Login form */}
          <form onSubmit={handleSubmit} className="space-y-5 animate-fade-in-up" style={{ animationDelay: '50ms' }}>
            <div className="space-y-2">
              <Label htmlFor="email">Email address</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="pl-10"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  id="password"
                  type="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="pl-10"
                />
              </div>
            </div>

            <Button
              type="submit"
              disabled={isLoading}
              className="w-full group"
              size="lg"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                <>
                  Sign in
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </Button>
          </form>

          {/* Divider */}
          <div className="my-8 flex items-center gap-4 animate-fade-in" style={{ animationDelay: '150ms' }}>
            <div className="flex-1 h-px bg-border"></div>
            <span className="text-sm text-muted-foreground">OR</span>
            <div className="flex-1 h-px bg-border"></div>
          </div>

          {/* Register link */}
          <p className="text-center text-sm text-muted-foreground animate-fade-in" style={{ animationDelay: '200ms' }}>
            Don't have an account?{' '}
            <Link
              href="/register"
              className="font-semibold text-primary hover:text-primary/80 transition-colors hover:underline decoration-2 underline-offset-2"
            >
              Create account
            </Link>
          </p>

          {/* Demo credentials */}
          <Card className="mt-8 p-4 bg-muted/50 border-border animate-fade-in-up" style={{ animationDelay: '250ms' }}>
            <p className="text-xs text-muted-foreground text-center">
              <span className="font-semibold">Demo:</span> testuser123@example.com / TestPass123
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
}
