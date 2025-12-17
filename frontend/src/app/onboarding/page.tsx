'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import { api } from '@/lib/api';

interface Question {
  question: string;
  options: string[];
  category: string;
}

interface Answer {
  question_index: number;
  answer: string;
}

export default function OnboardingPage() {
  const router = useRouter();
  const { user, loadUser } = useAuthStore();
  const [step, setStep] = useState(0);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [freeTextGoals, setFreeTextGoals] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    loadUser();
    loadQuestions();
  }, []);

  useEffect(() => {
    if (user?.onboarding_completed) {
      router.push('/dashboard');
    }
  }, [user, router]);

  const loadQuestions = async () => {
    try {
      const data = await api.getOnboardingQuestions();
      setQuestions(data.questions);
    } catch (error) {
      console.error('Failed to load questions:', error);
    }
  };

  const handleAnswer = (questionIndex: number, answer: string) => {
    setAnswers((prev) => {
      const existing = prev.findIndex((a) => a.question_index === questionIndex);
      if (existing >= 0) {
        const updated = [...prev];
        updated[existing] = { question_index: questionIndex, answer };
        return updated;
      }
      return [...prev, { question_index: questionIndex, answer }];
    });
  };

  const handleNext = () => {
    if (step < questions.length) {
      setStep(step + 1);
    }
  };

  const handleBack = () => {
    if (step > 0) {
      setStep(step - 1);
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      const response = await api.submitAssessment({
        answers,
        free_text_goals: freeTextGoals || null,
      });
      setResult(response);
      setStep(questions.length + 1);
    } catch (error) {
      console.error('Failed to submit assessment:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFinish = async () => {
    await loadUser(); // Reload user to get updated onboarding_completed flag
    router.push('/dashboard');
  };

  if (questions.length === 0) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p>Loading...</p>
      </div>
    );
  }

  // Welcome screen
  if (step === 0) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-950 dark:to-primary-900">
        <div className="w-full max-w-2xl rounded-lg bg-white dark:bg-gray-900 p-8 shadow-lg">
          <h1 className="text-4xl font-bold text-primary-600 dark:text-primary-400">
            Welcome to MyTeacher!
          </h1>
          <p className="mt-4 text-lg text-gray-700 dark:text-gray-300">
            Let's personalize your learning journey. We'll ask you a few questions
            to understand your experience and goals.
          </p>
          <div className="mt-6 space-y-3 text-gray-600 dark:text-gray-400">
            <p>✨ Get a personalized learning path</p>
            <p>🎯 Start at the right difficulty level</p>
            <p>🚀 Learn at your own pace</p>
            <p>🧠 ADHD-friendly step-by-step approach</p>
          </div>
          <button
            onClick={() => setStep(1)}
            className="mt-8 w-full rounded-lg bg-primary-600 py-3 font-medium text-white hover:bg-primary-700"
          >
            Let's Get Started
          </button>
        </div>
      </div>
    );
  }

  // Questions
  if (step <= questions.length) {
    const currentQuestion = questions[step - 1];
    const currentAnswer = answers.find((a) => a.question_index === step - 1);

    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-950 dark:to-primary-900 p-4">
        <div className="w-full max-w-2xl rounded-lg bg-white dark:bg-gray-900 p-8 shadow-lg">
          {/* Progress */}
          <div className="mb-6">
            <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
              <span>
                Question {step} of {questions.length}
              </span>
              <span>{Math.round((step / questions.length) * 100)}%</span>
            </div>
            <div className="mt-2 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
              <div
                className="h-2 rounded-full bg-primary-600 dark:bg-primary-500 transition-all"
                style={{ width: `${(step / questions.length) * 100}%` }}
              />
            </div>
          </div>

          {/* Question */}
          <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
            {currentQuestion.question}
          </h2>

          {/* Options */}
          <div className="mt-6 space-y-3">
            {currentQuestion.options.map((option, idx) => (
              <button
                key={idx}
                onClick={() => handleAnswer(step - 1, option)}
                className={`w-full rounded-lg border-2 p-4 text-left text-gray-900 dark:text-gray-100 transition-all ${
                  currentAnswer?.answer === option
                    ? 'border-primary-600 dark:border-primary-500 bg-primary-50 dark:bg-primary-950'
                    : 'border-gray-300 dark:border-gray-600 hover:border-primary-300 dark:hover:border-primary-600'
                }`}
              >
                {option}
              </button>
            ))}
          </div>

          {/* Goals text (last question) */}
          {step === questions.length && (
            <div className="mt-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Tell us more about your goals (optional):
              </label>
              <textarea
                value={freeTextGoals}
                onChange={(e) => setFreeTextGoals(e.target.value)}
                placeholder="e.g., I want to become a DevOps engineer, learn automation, deploy apps..."
                className="mt-2 w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 p-3 text-gray-900 dark:text-gray-100 placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:border-primary-500 dark:focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-200 dark:focus:ring-primary-800"
                rows={3}
              />
            </div>
          )}

          {/* Navigation */}
          <div className="mt-8 flex justify-between">
            <button
              onClick={handleBack}
              disabled={step === 1}
              className="rounded-lg border border-gray-300 dark:border-gray-600 px-6 py-2 font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 disabled:opacity-50"
            >
              Back
            </button>
            {step < questions.length ? (
              <button
                onClick={handleNext}
                disabled={!currentAnswer}
                className="rounded-lg bg-primary-600 px-6 py-2 font-medium text-white hover:bg-primary-700 disabled:bg-gray-400"
              >
                Next
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={!currentAnswer || isSubmitting}
                className="rounded-lg bg-primary-600 px-6 py-2 font-medium text-white hover:bg-primary-700 disabled:bg-gray-400"
              >
                {isSubmitting ? 'Analyzing...' : 'Finish'}
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Results
  if (result) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-950 dark:to-primary-900 p-4">
        <div className="w-full max-w-2xl rounded-lg bg-white dark:bg-gray-900 p-8 shadow-lg">
          <div className="text-center">
            <div className="text-6xl">🎉</div>
            <h1 className="mt-4 text-3xl font-bold text-primary-600 dark:text-primary-400">
              Your Learning Path is Ready!
            </h1>
          </div>

          <div className="mt-6 space-y-4">
            <div className="rounded-lg bg-primary-50 dark:bg-primary-950 p-4">
              <p className="text-gray-800 dark:text-gray-200">{result.personalized_message}</p>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-lg border border-gray-200 dark:border-gray-700 p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Your Level</p>
                <p className="mt-1 text-xl font-semibold capitalize text-gray-800 dark:text-gray-100">
                  {result.recommended_level}
                </p>
              </div>
              <div className="rounded-lg border border-gray-200 dark:border-gray-700 p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Estimated Duration</p>
                <p className="mt-1 text-xl font-semibold text-gray-800 dark:text-gray-100">
                  {result.estimated_duration_weeks} weeks
                </p>
              </div>
            </div>

            <div className="rounded-lg border border-gray-200 dark:border-gray-700 p-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Starting Topics ({result.starting_nodes.length})
              </p>
              <p className="mt-1 text-gray-700 dark:text-gray-300">
                We've curated a personalized curriculum just for you!
              </p>
            </div>
          </div>

          <button
            onClick={handleFinish}
            className="mt-8 w-full rounded-lg bg-primary-600 py-3 font-medium text-white hover:bg-primary-700"
          >
            Start Learning
          </button>
        </div>
      </div>
    );
  }

  return null;
}
