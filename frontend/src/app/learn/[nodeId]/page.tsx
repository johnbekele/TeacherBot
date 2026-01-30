'use client';

import { Suspense, useEffect, useState, useCallback, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import { useNodeStore } from '@/stores/nodeStore';
import AppLayout from '@/components/layout/AppLayout';
import { api } from '@/lib/api';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

// ============================================================================
// LOCAL STORAGE CACHING UTILITIES
// ============================================================================

const CACHE_PREFIX = 'myteacher_content_';
const CACHE_EXPIRY_HOURS = 24; // Cache expires after 24 hours

interface CachedContent {
  nodeTitle: string;
  totalSteps: number;
  steps: StepMetadata[];
  stepDataCache: Record<number, Step>;
  cachedAt: number;
}

// Get user ID from localStorage for user-specific caching
function getUserId(): string {
  if (typeof window === 'undefined') return 'anon';
  try {
    const authStorage = localStorage.getItem('auth-storage');
    if (authStorage) {
      const parsed = JSON.parse(authStorage);
      return parsed?.state?.user?.id || parsed?.state?.user?._id || 'anon';
    }
  } catch {
    // ignore
  }
  return 'anon';
}

function getCacheKey(nodeId: string): string {
  const userId = getUserId();
  return `${CACHE_PREFIX}${userId}_${nodeId}`;
}

function getFromCache(nodeId: string): CachedContent | null {
  if (typeof window === 'undefined') return null;

  try {
    const key = getCacheKey(nodeId);
    const cached = localStorage.getItem(key);
    if (!cached) {
      console.log('📭 No cache found for:', key);
      return null;
    }

    const data: CachedContent = JSON.parse(cached);

    // Check if cache is expired
    const hoursSinceCached = (Date.now() - data.cachedAt) / (1000 * 60 * 60);
    if (hoursSinceCached > CACHE_EXPIRY_HOURS) {
      console.log('⏰ Cache expired for:', key);
      localStorage.removeItem(key);
      return null;
    }

    console.log('✅ Cache hit for:', key, 'steps cached:', Object.keys(data.stepDataCache).length);
    return data;
  } catch (e) {
    console.warn('Failed to read cache:', e);
    return null;
  }
}

function saveToCache(nodeId: string, data: Partial<CachedContent>): void {
  if (typeof window === 'undefined') return;

  try {
    const key = getCacheKey(nodeId);
    const existing = getFromCache(nodeId) || {
      nodeTitle: '',
      totalSteps: 0,
      steps: [],
      stepDataCache: {},
      cachedAt: Date.now()
    };

    const updated: CachedContent = {
      ...existing,
      ...data,
      cachedAt: existing.cachedAt || Date.now() // Keep original cache time
    };

    localStorage.setItem(key, JSON.stringify(updated));
    console.log('💾 Saved to cache:', key);
  } catch (e) {
    console.warn('Failed to cache content:', e);
  }
}

function cacheStepData(nodeId: string, stepNumber: number, stepData: Step): void {
  if (typeof window === 'undefined') return;

  try {
    const key = getCacheKey(nodeId);
    const cached = getFromCache(nodeId);
    if (cached) {
      cached.stepDataCache[stepNumber] = stepData;
      localStorage.setItem(key, JSON.stringify(cached));
      console.log('💾 Cached step', stepNumber, 'for:', key);
    }
  } catch (e) {
    console.warn('Failed to cache step:', e);
  }
}

// Step types from backend
interface LectureStep {
  step_type: 'lecture_section';
  section_name: string;
  title: string;
  content: {
    heading: string;
    body: string;
    code_examples: Array<{
      language: string;
      code: string;
      explanation: string;
    }>;
    next_steps?: string;
  };
}

interface ExerciseStep {
  step_type: 'exercise';
  section_name: string;
  title: string;
  content: {
    exercise_id: string;
    title: string;
    description: string;
    prompt: string;
    difficulty: string;
    starter_code: string;
    hints: Array<{ level: number; hint: string }>;
  };
}

type Step = LectureStep | ExerciseStep;

interface StepMetadata {
  step_number: number;
  step_type: string;
  title: string;
  section_name: string;
}

function LearningSessionContent({ nodeId }: { nodeId: string }) {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading, loadUser } = useAuthStore();
  const { currentNode, selectNode } = useNodeStore();

  // State
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [stepData, setStepData] = useState<Step | null>(null);
  const [stepsMeta, setStepsMeta] = useState<StepMetadata[]>([]);
  const [totalSteps, setTotalSteps] = useState<number>(0);
  const [nodeTitle, setNodeTitle] = useState<string>('');
  const [isLoadingStep, setIsLoadingStep] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showHint, setShowHint] = useState<number>(0);
  const [showTOC, setShowTOC] = useState(false);

  // Load user on mount - only once
  useEffect(() => {
    loadUser();
  }, []); // Empty deps - only run once on mount

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, authLoading, router]);

  // Select node - only when nodeId changes
  useEffect(() => {
    if (isAuthenticated && nodeId) {
      selectNode(nodeId);
    }
  }, [isAuthenticated, nodeId]); // Removed selectNode from deps to prevent infinite loops

  // Initialize learning session - check cache first
  useEffect(() => {
    const initLearning = async () => {
      if (!isAuthenticated) return;

      try {
        setIsLoadingStep(true);
        setError(null);

        // Check localStorage cache first
        const cached = getFromCache(nodeId);

        if (cached && cached.totalSteps > 0 && cached.stepDataCache[1]) {
          console.log('📦 Loading from cache:', nodeId);

          // Load from cache - instant!
          setNodeTitle(cached.nodeTitle);
          setTotalSteps(cached.totalSteps);
          setStepsMeta(cached.steps);
          setStepData(cached.stepDataCache[1]);
          setCurrentStep(1);
          setIsLoadingStep(false);
          return;
        }

        // No cache - fetch from API
        console.log('🌐 Fetching from API:', nodeId);
        const response = await api.startLearningInstant(nodeId);

        setNodeTitle(response.node_title);
        setTotalSteps(response.total_steps);
        setStepData(response.step);
        setCurrentStep(1);

        const allSteps = await api.getAllSteps(nodeId);
        setStepsMeta(allSteps.steps);

        // Save to cache for next time
        saveToCache(nodeId, {
          nodeTitle: response.node_title,
          totalSteps: response.total_steps,
          steps: allSteps.steps,
          stepDataCache: { 1: response.step },
          cachedAt: Date.now()
        });

      } catch (err: any) {
        console.error('Failed to start learning:', err);
        setError(err.response?.data?.detail || 'Failed to load learning content');
      } finally {
        setIsLoadingStep(false);
      }
    };

    initLearning();
  }, [isAuthenticated, nodeId]);

  // Navigate to a specific step - check cache first
  const goToStep = useCallback(async (stepNumber: number) => {
    if (stepNumber < 1 || stepNumber > totalSteps) return;

    try {
      setShowHint(0);
      setShowTOC(false);

      // Check cache first
      const cached = getFromCache(nodeId);
      if (cached?.stepDataCache[stepNumber]) {
        console.log('📦 Loading step from cache:', stepNumber);
        setStepData(cached.stepDataCache[stepNumber]);
        setCurrentStep(stepNumber);
        return;
      }

      // Not in cache - fetch from API
      setIsLoadingStep(true);
      console.log('🌐 Fetching step from API:', stepNumber);

      const response = await api.getLearningStep(nodeId, stepNumber);
      setStepData(response.step);
      setCurrentStep(stepNumber);

      // Cache this step for next time
      cacheStepData(nodeId, stepNumber, response.step);

    } catch (err: any) {
      console.error('Failed to load step:', err);
      setError(err.response?.data?.detail || 'Failed to load step');
    } finally {
      setIsLoadingStep(false);
    }
  }, [nodeId, totalSteps]);

  const goNext = useCallback(() => {
    if (currentStep < totalSteps) {
      goToStep(currentStep + 1);
    }
  }, [currentStep, totalSteps, goToStep]);

  const goPrevious = useCallback(() => {
    if (currentStep > 1) {
      goToStep(currentStep - 1);
    }
  }, [currentStep, goToStep]);

  const startExercise = useCallback((exerciseId: string) => {
    router.push(`/exercise/${exerciseId}?node=${nodeId}&step=${currentStep}`);
  }, [router, nodeId, currentStep]);

  const progressPercent = useMemo(() => {
    return totalSteps > 0 ? Math.round((currentStep / totalSteps) * 100) : 0;
  }, [currentStep, totalSteps]);

  // Count lecture vs exercise steps
  const lectureCount = useMemo(() =>
    stepsMeta.filter(s => s.step_type === 'lecture_section').length, [stepsMeta]);
  const exerciseCount = useMemo(() =>
    stepsMeta.filter(s => s.step_type === 'exercise').length, [stepsMeta]);

  if (authLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <AppLayout>
        <div className="max-w-2xl mx-auto mt-8 px-4">
          <div className="rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-6 shadow-lg">
            <h2 className="text-xl font-semibold text-red-900 dark:text-red-100 mb-2">⚠️ Error</h2>
            <p className="text-red-700 dark:text-red-300">{error}</p>
            <button
              onClick={() => router.back()}
              className="mt-4 rounded-lg bg-red-600 px-4 py-2 text-white hover:bg-red-700 transition-colors"
            >
              ← Go Back
            </button>
          </div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout
      contextType="learning_qa"
      contextId={nodeId}
    >
      <div className="max-w-4xl mx-auto py-4 px-4">
        {/* Compact Header */}
        <div className="mb-4 bg-gradient-to-r from-primary/10 via-purple-500/10 to-pink-500/10 dark:from-primary/20 dark:via-purple-900/20 dark:to-pink-900/20 rounded-xl p-4 border border-primary/20">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div>
              <h1 className="text-xl font-bold text-foreground">
                {nodeTitle || currentNode?.title || 'Learning Session'}
              </h1>
              <p className="text-sm text-muted-foreground mt-0.5">
                📖 {lectureCount} sections • 📝 {exerciseCount} exercises
              </p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setShowTOC(!showTOC)}
                className="px-3 py-1.5 rounded-lg bg-background/80 border text-sm font-medium hover:bg-background transition-colors"
              >
                📑 Contents
              </button>
              <div className="text-sm font-medium bg-primary/10 px-3 py-1.5 rounded-lg">
                {currentStep}/{totalSteps}
              </div>
            </div>
          </div>

          {/* Progress bar */}
          <div className="mt-3 w-full bg-background/50 rounded-full h-2 overflow-hidden">
            <div
              className="bg-gradient-to-r from-primary to-purple-500 h-2 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>

        {/* Table of Contents Dropdown */}
        {showTOC && (
          <div className="mb-4 bg-card rounded-xl border shadow-lg p-4 animate-in slide-in-from-top-2 duration-200">
            <h3 className="font-semibold mb-3 text-sm uppercase tracking-wide text-muted-foreground">
              Table of Contents
            </h3>
            <div className="grid gap-1.5 max-h-64 overflow-y-auto">
              {stepsMeta.map((step) => (
                <button
                  key={step.step_number}
                  onClick={() => goToStep(step.step_number)}
                  className={`text-left px-3 py-2 rounded-lg text-sm transition-all flex items-center gap-2 ${
                    step.step_number === currentStep
                      ? 'bg-primary text-primary-foreground font-medium'
                      : step.step_number < currentStep
                      ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300 hover:bg-green-100 dark:hover:bg-green-900/30'
                      : 'hover:bg-muted'
                  }`}
                >
                  <span className="w-6 h-6 flex items-center justify-center rounded-full bg-background/50 text-xs font-medium">
                    {step.step_type === 'exercise' ? '📝' : step.step_number}
                  </span>
                  <span className="truncate">{step.title}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Main Content Card */}
        <div className="bg-card rounded-xl shadow-lg border overflow-hidden min-h-[500px]">
          {isLoadingStep ? (
            <div className="flex items-center justify-center h-96">
              <div className="text-center">
                <div className="animate-spin rounded-full h-10 w-10 border-4 border-primary border-t-transparent mx-auto mb-3"></div>
                <p className="text-muted-foreground">Loading content...</p>
              </div>
            </div>
          ) : stepData ? (
            <div className="p-6">
              {/* Lecture Section Content */}
              {stepData.step_type === 'lecture_section' && (
                <div className="prose prose-slate dark:prose-invert max-w-none prose-headings:font-semibold prose-code:before:content-none prose-code:after:content-none">
                  <h2 className="text-2xl font-bold mb-4 text-foreground flex items-center gap-2">
                    <span className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center text-primary text-sm">
                      {currentStep}
                    </span>
                    {stepData.content.heading}
                  </h2>

                  <div className="text-base leading-relaxed">
                    <ReactMarkdown
                      components={{
                        code({ node, inline, className, children, ...props }: any) {
                          const match = /language-(\w+)/.exec(className || '');
                          return !inline && match ? (
                            <SyntaxHighlighter
                              style={oneDark}
                              language={match[1]}
                              PreTag="div"
                              className="rounded-xl !bg-gray-900 !my-4"
                              showLineNumbers={true}
                              {...props}
                            >
                              {String(children).replace(/\n$/, '')}
                            </SyntaxHighlighter>
                          ) : (
                            <code className="bg-primary/10 text-primary px-1.5 py-0.5 rounded font-mono text-sm" {...props}>
                              {children}
                            </code>
                          );
                        },
                        p({ children }) {
                          return <p className="mb-4 text-foreground/90">{children}</p>;
                        },
                        ul({ children }) {
                          return <ul className="mb-4 space-y-2">{children}</ul>;
                        },
                        li({ children }) {
                          return <li className="text-foreground/90">{children}</li>;
                        },
                        h3({ children }) {
                          return <h3 className="text-lg font-semibold mt-6 mb-3 text-foreground">{children}</h3>;
                        },
                      }}
                    >
                      {stepData.content.body}
                    </ReactMarkdown>
                  </div>

                  {/* Code Examples */}
                  {stepData.content.code_examples && stepData.content.code_examples.length > 0 && (
                    <div className="mt-6 space-y-4">
                      {stepData.content.code_examples.map((example, idx) => (
                        <div key={idx} className="rounded-xl overflow-hidden border border-gray-200 dark:border-gray-700">
                          <div className="bg-gray-100 dark:bg-gray-800 px-4 py-2 text-sm font-medium flex items-center gap-2">
                            <span className="text-primary">▶</span>
                            Example: {example.language}
                          </div>
                          <SyntaxHighlighter
                            style={oneDark}
                            language={example.language || 'python'}
                            customStyle={{ margin: 0, borderRadius: 0 }}
                            showLineNumbers={true}
                          >
                            {example.code}
                          </SyntaxHighlighter>
                          {example.explanation && (
                            <div className="px-4 py-3 bg-blue-50 dark:bg-blue-950/50 text-sm border-t border-gray-200 dark:border-gray-700">
                              <span className="font-medium text-blue-700 dark:text-blue-300">💡 Explanation:</span>{' '}
                              <span className="text-blue-600 dark:text-blue-200">{example.explanation}</span>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Next Steps hint */}
                  {stepData.content.next_steps && (
                    <div className="mt-6 p-4 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-950/30 dark:to-emerald-950/30 rounded-xl border border-green-200 dark:border-green-800">
                      <p className="text-green-800 dark:text-green-200 font-medium flex items-center gap-2">
                        <span className="text-xl">🚀</span>
                        {stepData.content.next_steps}
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Exercise Content */}
              {stepData.step_type === 'exercise' && (
                <div>
                  <div className="flex items-center gap-3 mb-4 flex-wrap">
                    <h2 className="text-2xl font-bold">{stepData.content.title}</h2>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wide ${
                      stepData.content.difficulty === 'beginner'
                        ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300'
                        : stepData.content.difficulty === 'intermediate'
                        ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300'
                        : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300'
                    }`}>
                      {stepData.content.difficulty}
                    </span>
                  </div>

                  <p className="text-muted-foreground mb-4 text-lg">{stepData.content.description}</p>

                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30 rounded-xl p-5 mb-5 border border-blue-200 dark:border-blue-800">
                    <h3 className="font-semibold mb-3 text-blue-900 dark:text-blue-100 flex items-center gap-2">
                      <span>📋</span> Your Task
                    </h3>
                    <div className="whitespace-pre-wrap text-blue-800 dark:text-blue-200">{stepData.content.prompt}</div>
                  </div>

                  {/* Starter Code Preview */}
                  {stepData.content.starter_code && (
                    <div className="mb-5">
                      <h3 className="font-semibold mb-2 flex items-center gap-2">
                        <span>💻</span> Starter Code
                      </h3>
                      <SyntaxHighlighter
                        style={oneDark}
                        language="python"
                        className="rounded-xl"
                        showLineNumbers={true}
                      >
                        {stepData.content.starter_code}
                      </SyntaxHighlighter>
                    </div>
                  )}

                  {/* Hints */}
                  {stepData.content.hints && stepData.content.hints.length > 0 && (
                    <div className="mb-5">
                      <button
                        onClick={() => setShowHint(showHint < 3 ? showHint + 1 : 0)}
                        className="text-sm text-primary hover:underline font-medium flex items-center gap-1"
                      >
                        <span>💡</span>
                        {showHint === 0 ? 'Need a hint?' : `Show ${showHint < 3 ? 'more hints' : 'less'}`}
                      </button>

                      {showHint > 0 && (
                        <div className="mt-3 space-y-2">
                          {stepData.content.hints
                            .filter((h) => h.level <= showHint)
                            .map((hint) => (
                              <div
                                key={hint.level}
                                className="p-4 bg-amber-50 dark:bg-amber-950/30 rounded-xl border border-amber-200 dark:border-amber-800"
                              >
                                <span className="font-medium text-amber-800 dark:text-amber-200">
                                  Hint {hint.level}:
                                </span>{' '}
                                <span className="text-amber-700 dark:text-amber-300">{hint.hint}</span>
                              </div>
                            ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Start Exercise Button */}
                  <button
                    onClick={() => startExercise(stepData.content.exercise_id)}
                    className="w-full py-4 bg-gradient-to-r from-primary to-purple-600 text-white rounded-xl font-semibold text-lg hover:opacity-90 transition-all shadow-lg hover:shadow-xl hover:scale-[1.01] active:scale-[0.99]"
                  >
                    🚀 Start Coding Exercise
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center justify-center h-96 text-muted-foreground">
              No content available
            </div>
          )}
        </div>

        {/* Navigation Buttons */}
        <div className="mt-4 flex items-center justify-between gap-4">
          <button
            onClick={goPrevious}
            disabled={currentStep <= 1}
            className={`flex-1 py-3 rounded-xl font-medium transition-all flex items-center justify-center gap-2 ${
              currentStep <= 1
                ? 'bg-muted text-muted-foreground cursor-not-allowed'
                : 'bg-card border hover:bg-muted text-foreground hover:shadow-md'
            }`}
          >
            <span>←</span> Previous
          </button>

          <button
            onClick={goNext}
            disabled={currentStep >= totalSteps}
            className={`flex-1 py-3 rounded-xl font-medium transition-all flex items-center justify-center gap-2 ${
              currentStep >= totalSteps
                ? 'bg-muted text-muted-foreground cursor-not-allowed'
                : 'bg-primary text-primary-foreground hover:opacity-90 hover:shadow-md'
            }`}
          >
            Next <span>→</span>
          </button>
        </div>

        {/* AI Help Note */}
        <div className="mt-4 p-3 bg-gradient-to-r from-blue-50/50 to-purple-50/50 dark:from-blue-950/20 dark:to-purple-950/20 rounded-xl border border-blue-200/50 dark:border-blue-800/50">
          <p className="text-sm text-center text-blue-700 dark:text-blue-300">
            💬 <strong>Need help?</strong> Ask the AI assistant on the right for explanations and guidance.
          </p>
        </div>
      </div>
    </AppLayout>
  );
}

export default function LearningSessionPage({
  params,
}: {
  params: { nodeId: string };
}) {
  const { nodeId } = params;

  return (
    <Suspense
      fallback={
        <div className="flex h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading learning session...</p>
          </div>
        </div>
      }
    >
      <LearningSessionContent nodeId={nodeId} />
    </Suspense>
  );
}
