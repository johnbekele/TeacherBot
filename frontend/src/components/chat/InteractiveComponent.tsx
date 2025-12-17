'use client';

import React from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface InteractiveComponentProps {
  component: any;
}

export default function InteractiveComponent({ component }: InteractiveComponentProps) {
  if (!component || !component.type) {
    return null;
  }

  // Code Execution Result
  if (component.type === 'code_execution') {
    return (
      <div className="mt-3 rounded-lg border border-green-200 bg-green-50 overflow-hidden">
        <div className="bg-green-100 px-4 py-2 border-b border-green-200">
          <span className="text-sm font-medium text-green-800">
            ▶️ Code Executed ({component.language})
          </span>
        </div>

        {/* Code */}
        <div className="px-4 py-2 bg-gray-900">
          <SyntaxHighlighter
            language={component.language}
            style={vscDarkPlus}
            customStyle={{ margin: 0, padding: 0, background: 'transparent' }}
          >
            {component.code}
          </SyntaxHighlighter>
        </div>

        {/* Output */}
        <div className="px-4 py-3 bg-white dark:bg-gray-900">
          <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1">Output:</div>
          <pre className="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap font-mono">
            {component.output || '(no output)'}
          </pre>
        </div>
      </div>
    );
  }

  // Quiz Component
  if (component.type === 'quiz') {
    const { question, options, correct_answer } = component.data || {};

    return (
      <div className="mt-3 rounded-lg border border-blue-200 bg-blue-50 p-4">
        <div className="flex items-center mb-3">
          <span className="text-2xl mr-2">❓</span>
          <h4 className="font-semibold text-blue-900">Quick Quiz</h4>
        </div>
        <p className="text-blue-800 mb-3">{question}</p>
        <div className="space-y-2">
          {options?.map((option: string, idx: number) => (
            <button
              key={idx}
              className="w-full text-left px-4 py-2 rounded bg-white dark:bg-gray-900 border border-blue-200 dark:border-blue-800 hover:bg-blue-100 dark:hover:bg-blue-950 hover:border-blue-300 dark:hover:border-blue-700 transition-colors text-gray-900 dark:text-gray-100"
            >
              {option}
            </button>
          ))}
        </div>
      </div>
    );
  }

  // Button Component
  if (component.type === 'button') {
    const { label, action } = component.data || {};

    return (
      <div className="mt-3">
        <button className="px-6 py-3 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 shadow-sm">
          {label || 'Click Me'}
        </button>
      </div>
    );
  }

  // Info Box Component
  if (component.type === 'info_box') {
    const { title, content, icon } = component.data || {};

    return (
      <div className="mt-3 rounded-lg border border-purple-200 bg-purple-50 p-4">
        <div className="flex items-start">
          {icon && <span className="text-2xl mr-3">{icon}</span>}
          <div className="flex-1">
            {title && <h4 className="font-semibold text-purple-900 mb-2">{title}</h4>}
            <p className="text-purple-800">{content}</p>
          </div>
        </div>
      </div>
    );
  }

  // Progress Bar Component
  if (component.type === 'progress_bar') {
    const { percentage, label } = component.data || {};
    const progress = Math.min(100, Math.max(0, percentage || 0));

    return (
      <div className="mt-3 rounded-lg border border-gray-200 bg-gray-50 p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">{label || 'Progress'}</span>
          <span className="text-sm font-semibold text-gray-900">{progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className="bg-gradient-to-r from-primary-500 to-purple-500 h-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    );
  }

  // Error Component
  if (component.type === 'error') {
    return (
      <div className="mt-3 rounded-lg border border-red-200 bg-red-50 p-4">
        <div className="flex items-center">
          <span className="text-2xl mr-2">⚠️</span>
          <p className="text-red-800">{component.message}</p>
        </div>
      </div>
    );
  }

  // Navigation Action (visual feedback)
  if (component.type === 'navigate') {
    const { action, message, target_id } = component.data || {};

    return (
      <div className="mt-3 rounded-lg border border-indigo-200 bg-indigo-50 p-4">
        <div className="flex items-center">
          <span className="text-2xl mr-3">🎯</span>
          <div>
            <div className="font-semibold text-indigo-900">Navigation</div>
            <p className="text-sm text-indigo-700">{message}</p>
            <div className="text-xs text-indigo-600 mt-1">Action: {action}</div>
          </div>
        </div>
      </div>
    );
  }

  // Default: just show the component type
  return (
    <div className="mt-3 rounded-lg border border-gray-200 bg-gray-50 p-3">
      <span className="text-sm text-gray-600">
        Interactive component: {component.type}
      </span>
    </div>
  );
}
