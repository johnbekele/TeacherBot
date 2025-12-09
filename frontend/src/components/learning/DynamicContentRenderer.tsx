'use client';

import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface ContentSection {
  heading: string;
  body: string;
  code_example?: string;
  language?: string;
}

interface DynamicContent {
  content_id: string;
  title: string;
  content_type: string;
  sections: ContentSection[];
  created_at: string;
}

interface DynamicContentRendererProps {
  content: DynamicContent;
}

export default function DynamicContentRenderer({ content }: DynamicContentRendererProps) {
  // Ensure sections is an array
  const sections = Array.isArray(content.sections) ? content.sections : [];

  return (
    <div className="rounded-lg bg-white dark:bg-gray-900 p-6 shadow-sm">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-700 pb-4 mb-6">
        <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">{content.title}</h2>
        <div className="mt-2 flex items-center space-x-2">
          <span className="inline-block rounded-full bg-purple-100 dark:bg-purple-900 px-3 py-1 text-sm text-purple-700 dark:text-purple-300">
            {content.content_type}
          </span>
          <span className="text-sm text-gray-500 dark:text-gray-400">AI-generated content</span>
        </div>
      </div>

      {/* Content Sections */}
      {sections.length === 0 ? (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          <p>No content sections available yet.</p>
          <p className="text-sm mt-2">The AI teacher will add content shortly.</p>
        </div>
      ) : (
        <div className="space-y-8">
          {sections.map((section, idx) => (
          <section key={idx} className="space-y-4">
            {/* Section Heading */}
            <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-100 flex items-center">
              <span className="inline-block w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 text-sm font-bold flex items-center justify-center mr-3">
                {idx + 1}
              </span>
              {section.heading}
            </h3>

            {/* Section Body - Render Markdown */}
            <div className="prose dark:prose-invert prose-sm max-w-none ml-11">
              <ReactMarkdown
                components={{
                  // Custom code block rendering
                  code({ node, inline, className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || '');
                    const language = match ? match[1] : 'text';

                    return !inline ? (
                      <SyntaxHighlighter
                        style={vscDarkPlus}
                        language={language}
                        PreTag="div"
                        className="rounded-lg"
                        {...props}
                      >
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    ) : (
                      <code className="bg-gray-100 dark:bg-gray-800 rounded px-1 py-0.5 text-sm font-mono text-gray-800 dark:text-gray-200" {...props}>
                        {children}
                      </code>
                    );
                  },
                  // Style other elements
                  p: ({ children }) => (
                    <p className="text-gray-700 dark:text-gray-300 leading-relaxed mb-4">{children}</p>
                  ),
                  ul: ({ children }) => (
                    <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300">{children}</ul>
                  ),
                  ol: ({ children }) => (
                    <ol className="list-decimal list-inside space-y-2 text-gray-700 dark:text-gray-300">{children}</ol>
                  ),
                  li: ({ children }) => (
                    <li className="ml-4">{children}</li>
                  ),
                  strong: ({ children }) => (
                    <strong className="font-semibold text-gray-900 dark:text-gray-100">{children}</strong>
                  ),
                  em: ({ children }) => (
                    <em className="italic text-gray-800 dark:text-gray-200">{children}</em>
                  ),
                }}
              >
                {section.body}
              </ReactMarkdown>
            </div>

            {/* Code Example (if provided separately) */}
            {section.code_example && (
              <div className="ml-11">
                <div className="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Example:</div>
                <SyntaxHighlighter
                  language={section.language || 'python'}
                  style={vscDarkPlus}
                  className="rounded-lg"
                  showLineNumbers
                >
                  {section.code_example}
                </SyntaxHighlighter>
              </div>
            )}
          </section>
        ))}
        </div>
      )}

      {/* Footer */}
      <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <span>
            This content was dynamically generated by your AI teacher based on your learning needs.
          </span>
        </div>
      </div>
    </div>
  );
}
