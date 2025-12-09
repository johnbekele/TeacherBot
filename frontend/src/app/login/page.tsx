'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/stores/authStore';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Mail, Lock, GraduationCap, ArrowRight, Loader2 } from 'lucide-react';
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
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex">
      {/* Left side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-white dark:bg-gray-900 p-12 flex-col justify-between border-r border-gray-200 dark:border-gray-800 animate-fade-in">
        <div>
          <div className="flex items-center gap-3 mb-12 group cursor-pointer">
            <div className="flex items-center justify-center w-10 h-10 bg-accent-600 rounded-lg transition-all duration-300 group-hover:shadow-glow group-hover:scale-110">
              <GraduationCap className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-semibold text-gray-900 dark:text-white transition-colors">
              MyTeacher
            </span>
          </div>

          <div className="max-w-md">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-6 animate-slide-up">
              Master DevOps with AI-Powered Learning
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-400 mb-8 animate-slide-up" style={{ animationDelay: '100ms' }}>
              Personalized learning paths, intelligent feedback, and adaptive exercises designed just for you.
            </p>

            <div className="space-y-4">
              <div className="flex items-start gap-3 animate-slide-up group" style={{ animationDelay: '200ms' }}>
                <div className="w-2 h-2 rounded-full bg-accent-600 mt-2 transition-transform duration-300 group-hover:scale-150"></div>
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white">AI-Powered Path Creation</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Custom learning paths based on your goals and skill level</p>
                </div>
              </div>
              <div className="flex items-start gap-3 animate-slide-up group" style={{ animationDelay: '300ms' }}>
                <div className="w-2 h-2 rounded-full bg-accent-600 mt-2 transition-transform duration-300 group-hover:scale-150"></div>
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white">Interactive Exercises</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Hands-on practice with real-time feedback</p>
                </div>
              </div>
              <div className="flex items-start gap-3 animate-slide-up group" style={{ animationDelay: '400ms' }}>
                <div className="w-2 h-2 rounded-full bg-accent-600 mt-2 transition-transform duration-300 group-hover:scale-150"></div>
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white">Adaptive Learning</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">System learns from your performance and adapts accordingly</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <p className="text-sm text-gray-500 dark:text-gray-500">
          © 2025 MyTeacher. All rights reserved.
        </p>
      </div>

      {/* Right side - Login form */}
      <div className="flex-1 flex items-center justify-center p-8 animate-fade-in" style={{ animationDelay: '200ms' }}>
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="lg:hidden flex items-center gap-3 mb-8">
            <div className="flex items-center justify-center w-10 h-10 bg-accent-600 rounded-lg">
              <GraduationCap className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-semibold text-gray-900 dark:text-white">
              MyTeacher
            </span>
          </div>

          {/* Theme toggle */}
          <div className="flex justify-end mb-8">
            <ThemeToggle />
          </div>

          {/* Header */}
          <div className="mb-8 animate-slide-up">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Welcome back
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              Sign in to continue your learning journey
            </p>
          </div>

          {/* Login form */}
          <form onSubmit={handleSubmit} className="space-y-6 animate-slide-up" style={{ animationDelay: '100ms' }}>
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
                  placeholder="••••••••"
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
          <div className="my-8 flex items-center gap-4 animate-fade-in" style={{ animationDelay: '300ms' }}>
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-300 dark:via-gray-700 to-transparent"></div>
            <span className="text-sm text-gray-500 dark:text-gray-500">OR</span>
            <div className="flex-1 h-px bg-gradient-to-l from-transparent via-gray-300 dark:via-gray-700 to-transparent"></div>
          </div>

          {/* Register link */}
          <p className="text-center text-sm text-gray-600 dark:text-gray-400 animate-fade-in" style={{ animationDelay: '400ms' }}>
            Don't have an account?{' '}
            <Link
              href="/register"
              className="font-semibold text-accent-600 hover:text-accent-700 dark:text-accent-500 dark:hover:text-accent-400 transition-all hover:underline decoration-2 underline-offset-2"
            >
              Create account
            </Link>
          </p>

          {/* Demo credentials */}
          <div className="mt-8 p-4 bg-accent-50 dark:bg-accent-900/10 rounded-lg border border-accent-200 dark:border-accent-800 animate-slide-up" style={{ animationDelay: '500ms' }}>
            <p className="text-xs text-accent-800 dark:text-accent-300 text-center">
              <span className="font-semibold">Demo:</span> testuser123@example.com / TestPass123
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
