'use client';

import { createContext, useContext, ReactNode, useState } from 'react';

interface ChatContextType {
  contextType: string;
  contextId?: string;
  sessionId?: string;
  setContext: (contextType: string, contextId?: string, sessionId?: string) => void;
}

const ChatContext = createContext<ChatContextType>({
  contextType: 'general',
  setContext: () => {},
});

export function ChatContextProvider({ children }: { children: ReactNode }) {
  const [contextType, setContextType] = useState('general');
  const [contextId, setContextId] = useState<string | undefined>();
  const [sessionId, setSessionId] = useState<string | undefined>();

  const setContext = (newContextType: string, newContextId?: string, newSessionId?: string) => {
    console.log("ChatContext.setContext called:", { newContextType, newContextId, newSessionId });
    setContextType(newContextType);
    setContextId(newContextId);
    setSessionId(newSessionId);
  };

  return (
    <ChatContext.Provider value={{ contextType, contextId, sessionId, setContext }}>
      {children}
    </ChatContext.Provider>
  );
}

export function useChatContext() {
  return useContext(ChatContext);
}
