'use client';

import { ExerciseResult } from '@/types/exercise';

interface ExerciseResultsProps {
  results: ExerciseResult;
}

export default function ExerciseResults({ results }: ExerciseResultsProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6">
      {/* Score Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-semibold text-gray-800">Results</h3>
        <div
          className={`rounded-full px-4 py-2 text-lg font-bold ${
            results.passed
              ? 'bg-green-100 text-green-700'
              : 'bg-red-100 text-red-700'
          }`}
        >
          {results.score}%
        </div>
      </div>

      {/* Overall Feedback */}
      <div className="mt-4">
        <p className="whitespace-pre-wrap text-gray-700">{results.feedback}</p>
      </div>

      {/* Test Results */}
      <div className="mt-6">
        <h4 className="font-medium text-gray-800">Test Cases</h4>
        <div className="mt-3 space-y-2">
          {results.test_results.map((test, idx) => (
            <div
              key={idx}
              className={`flex items-center justify-between rounded-lg border p-3 ${
                test.passed
                  ? 'border-green-200 bg-green-50'
                  : 'border-red-200 bg-red-50'
              }`}
            >
              <div className="flex items-center space-x-3">
                <span className="text-xl">
                  {test.passed ? '✅' : '❌'}
                </span>
                <div>
                  <p className="font-medium text-gray-800">
                    Test {idx + 1}: {test.test_id}
                  </p>
                  {!test.passed && test.error_message && (
                    <p className="mt-1 text-sm text-red-600">
                      {test.error_message}
                    </p>
                  )}
                </div>
              </div>
              <span
                className={`text-sm font-medium ${
                  test.passed ? 'text-green-700' : 'text-red-700'
                }`}
              >
                {test.passed ? 'Passed' : 'Failed'}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Next Step */}
      <div className="mt-6 rounded-lg bg-blue-50 p-4">
        <p className="text-sm font-medium text-blue-900">Next Step:</p>
        <p className="mt-1 text-blue-800">{results.next_step}</p>
      </div>
    </div>
  );
}
