'use client';

import { ReactNode } from 'react';

interface LeftPanelProps {
  children?: ReactNode;
}

export default function LeftPanel({ children }: LeftPanelProps) {
  return (
    <div className="flex w-full lg:w-1/2 xl:w-3/5 flex-col overflow-hidden">
      <div className="flex-1 overflow-y-auto bg-white dark:bg-gray-950 p-4 lg:p-6">
        {children || (
          <div className="flex h-full items-center justify-center text-gray-400">
            <p>Select a learning module to begin</p>
          </div>
        )}
      </div>
    </div>
  );
}
