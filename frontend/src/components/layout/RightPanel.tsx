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
  return (
    <div className="flex flex-col h-full">
      {/* Chat panel fills the fixed container, has its own internal scroll */}
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
