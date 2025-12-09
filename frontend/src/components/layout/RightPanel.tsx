'use client';

import ChatPanel from '@/components/chat/ChatPanel';

interface RightPanelProps {
  sessionId?: string;
  contextType?: string;
  contextId?: string;
  userCode?: string;
  onActionReceived?: (action: any) => void;
}

export default function RightPanel({
  sessionId,
  contextType,
  contextId,
  userCode,
  onActionReceived,
}: RightPanelProps) {
  // Debug logging
  console.log("RightPanel received:", `contextType="${contextType}", contextId="${contextId}", sessionId="${sessionId}"`);

  return (
    <div className="flex w-full lg:w-1/2 xl:w-2/5 flex-col bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-950 border-l">
      <ChatPanel
        sessionId={sessionId}
        contextType={contextType}
        contextId={contextId}
        userCode={userCode}
        onActionReceived={onActionReceived}
      />
    </div>
  );
}
