'use client';

import { ExerciseResult } from '@/types/exercise';

interface ExerciseResultsProps {
  results: ExerciseResult;
}

export default function ExerciseResults({ results }: ExerciseResultsProps) {
  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 p-6">
      {/* Score Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-100">Results</h3>
        <div
          className={`rounded-full px-4 py-2 text-lg font-bold ${
            results.passed
              ? 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300'
              : 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300'
          }`}
        >
          {results.score}%
        </div>
      </div>

      {/* Overall Feedback */}
      <div className="mt-4">
        <p className="whitespace-pre-wrap text-gray-700 dark:text-gray-300">{results.feedback}</p>
      </div>

      {/* Test Results */}
      <div className="mt-6">
        <h4 className="font-medium text-gray-800 dark:text-gray-100">Test Cases</h4>
        <div className="mt-3 space-y-2">
          {results.test_results.map((test, idx) => (
            <div
              key={idx}
              className={`flex items-center justify-between rounded-lg border p-3 ${
                test.passed
                  ? 'border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-950'
                  : 'border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950'
              }`}
            >
              <div className="flex items-center space-x-3">
                <span className="text-xl">
                  {test.passed ? '✅' : '❌'}
                </span>
                <div>
                  <p className="font-medium text-gray-800 dark:text-gray-100">
                    Test {idx + 1}: {test.test_id}
                  </p>
                  {!test.passed && test.error_message && (
                    <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                      {test.error_message}
                    </p>
                  )}
                </div>
              </div>
              <span
                className={`text-sm font-medium ${
                  test.passed ? 'text-green-700 dark:text-green-300' : 'text-red-700 dark:text-red-300'
                }`}
              >
                {test.passed ? 'Passed' : 'Failed'}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Next Step */}
      <div className="mt-6 rounded-lg bg-blue-50 dark:bg-blue-950 p-4">
        <p className="text-sm font-medium text-blue-900 dark:text-blue-100">Next Step:</p>
        <p className="mt-1 text-blue-800 dark:text-blue-200">{results.next_step}</p>
      </div>
    </div>
  );
}
