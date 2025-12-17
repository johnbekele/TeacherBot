'use client';

import { useEffect, useState } from 'react';
import { useExerciseStore } from '@/stores/exerciseStore';
import { useChatStore } from '@/stores/chatStore';
import CodeEditor from './CodeEditor';
// import ExerciseResults from './ExerciseResults'; // Moved to chat - Phase 2.1

interface ExerciseViewProps {
  exerciseId: string;
  sessionId?: string;
}

export default function ExerciseView({ exerciseId, sessionId }: ExerciseViewProps) {
  const {
    currentExercise,
    editorCode,
    submissionStatus,
    results,
    loadExercise,
    setEditorCode,
    submitCode,
    error,
  } = useExerciseStore();

  const [aiProcessing, setAiProcessing] = useState(false);

  useEffect(() => {
    loadExercise(exerciseId);
  }, [exerciseId, loadExercise]);

  const handleSubmit = async () => {
    if (!currentExercise) return;

    try {
      // First submit to get grading results
      await submitCode(exerciseId, editorCode, currentExercise.type);

      // Then send to chat for AI feedback and interaction
      const { sendMessage } = useChatStore.getState();
      await sendMessage(
        `I've submitted my code for this exercise. Here's my solution:\n\n\`\`\`${currentExercise.type}\n${editorCode}\n\`\`\`\n\nCan you review it and let me know how I did?`,
        'exercise',
        exerciseId,
        editorCode
      );
      console.log('💻 Code submission sent to AI via chat');
    } catch (err) {
      console.error('Failed to submit code:', err);
    }
  };

  // AI feedback now happens through chat during handleSubmit

  const handleHint = async () => {
    try {
      // Send hint request as natural conversation through chat (Phase 2.4)
      const { sendMessage } = useChatStore.getState();
      await sendMessage(
        'Can you give me a hint for this exercise?',
        'exercise',
        exerciseId,
        editorCode
      );
      console.log('💡 Hint request sent to AI via chat');
    } catch (err) {
      console.error('Failed to get hint:', err);
    }
  };

  if (!currentExercise) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-gray-500 dark:text-gray-400">Loading exercise...</p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col space-y-4">
      {/* Exercise Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
          {currentExercise.title}
        </h2>
        <p className="mt-2 text-gray-600 dark:text-gray-300">{currentExercise.description}</p>
        <div className="mt-4 rounded-lg bg-blue-50 dark:bg-blue-950 p-4">
          <p className="text-sm font-medium text-blue-900 dark:text-blue-200">Task:</p>
          <p className="mt-1 whitespace-pre-wrap text-blue-800 dark:text-blue-300">
            {currentExercise.prompt}
          </p>
        </div>

        {error && (
          <div className="mt-3 rounded-lg bg-red-50 dark:bg-red-950 p-4">
            <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
          </div>
        )}
      </div>

      {/* Code Editor */}
      <div className="flex-1 min-h-[300px]">
        <CodeEditor
          value={editorCode}
          onChange={(value) => setEditorCode(value || '')}
          language={currentExercise.type}
        />
      </div>

      {/* Action Buttons */}
      <div className="flex items-center space-x-3">
        <button
          onClick={handleSubmit}
          disabled={submissionStatus === 'submitting' || submissionStatus === 'grading'}
          className="rounded-lg bg-primary-600 px-6 py-2 font-medium text-white hover:bg-primary-700 disabled:bg-gray-400"
        >
          {submissionStatus === 'submitting'
            ? 'Submitting...'
            : submissionStatus === 'grading'
            ? 'Grading...'
            : 'Submit Code'}
        </button>

        <button
          onClick={handleHint}
          className="rounded-lg border border-gray-300 dark:border-gray-600 px-6 py-2 font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800"
        >
          💡 Get Hint
        </button>

        <div className="flex-1" />

        <span className="text-sm text-gray-500 dark:text-gray-400">
          Attempts: {currentExercise.user_progress?.attempts || 0} | Best:{' '}
          {currentExercise.user_progress?.best_score || 0}%
        </span>
      </div>

      {/* Results - Now shown in chat panel only (Phase 2.1) */}
      {submissionStatus === 'completed' && results && (
        <div className="space-y-4">
          {/* <ExerciseResults results={results} /> */}

          {/* AI Processing Indicator */}
          {aiProcessing && sessionId && (
            <div className="rounded-lg bg-purple-50 dark:bg-purple-950 border border-purple-200 dark:border-purple-800 p-4">
              <div className="flex items-center space-x-3">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-purple-600 dark:bg-purple-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-purple-600 dark:bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 bg-purple-600 dark:bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
                <p className="text-sm text-purple-700 dark:text-purple-300 font-medium">
                  AI Teacher is analyzing your solution...
                </p>
              </div>
              <p className="text-xs text-purple-600 dark:text-purple-400 mt-2">
                Check the chat panel on the right for personalized feedback and next steps! 👉
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
