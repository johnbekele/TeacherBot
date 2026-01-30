'use client';

import { ReactNode } from 'react';

interface LeftPanelProps {
  children?: ReactNode;
}

export default function LeftPanel({ children }: LeftPanelProps) {
  return (
    <div className="flex w-full lg:w-1/2 xl:w-3/5 flex-col h-full overflow-hidden">
      {/* Content area scrolls independently - right panel is fixed so content stays in left portion */}
      <div className="flex-1 overflow-y-auto bg-white dark:bg-gray-950 scroll-smooth">
        {children || (
          <div className="flex h-full items-center justify-center text-gray-400 p-4">
            <p>Select a learning module to begin</p>
          </div>
        )}
      </div>
    </div>
  );
}
