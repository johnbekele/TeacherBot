'use client';

import { createContext, useContext, ReactNode, useState, useMemo, useCallback } from 'react';

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

  // Memoize setContext to prevent unnecessary re-renders
  const setContext = useCallback((newContextType: string, newContextId?: string, newSessionId?: string) => {
    console.log("ChatContext.setContext called:", { newContextType, newContextId, newSessionId });
    setContextType(newContextType);
    setContextId(newContextId);
    setSessionId(newSessionId);
  }, []);

  // Memoize context value to prevent re-renders when values haven't changed
  const contextValue = useMemo(() => ({
    contextType,
    contextId,
    sessionId,
    setContext
  }), [contextType, contextId, sessionId, setContext]);

  return (
    <ChatContext.Provider value={contextValue}>
      {children}
    </ChatContext.Provider>
  );
}

export function useChatContext() {
  return useContext(ChatContext);
}
