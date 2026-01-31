"use client";

import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { useChatStore } from "@/stores/chatStore";
import { useChatContext } from "@/contexts/ChatContext";
import MessageBubble from "./MessageBubble";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/badge";
import { Send, Loader2, AlertCircle, GraduationCap } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatPanelProps {
  sessionId?: string;
  contextType?: string;
  contextId?: string;
  userCode?: string;
  onActionReceived?: (action: any) => void;
}

export default function ChatPanel({
  sessionId: sessionIdProp,
  contextType: contextTypeProp,
  contextId: contextIdProp,
  userCode,
  onActionReceived,
}: ChatPanelProps) {
  // Use context values, fallback to props
  const chatContext = useChatContext();
  const contextType = contextTypeProp || chatContext.contextType || "teacher";
  const contextId = contextIdProp || chatContext.contextId;
  const sessionId = sessionIdProp || chatContext.sessionId;
  const router = useRouter();
  const {
    messages,
    isLoading,
    error,
    pendingActions,
    sendMessage,
    continueLearningSession,
    clearPendingActions,
    clearError,
  } = useChatStore();

  const [inputValue, setInputValue] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Debug logging on mount and prop changes
  useEffect(() => {
    console.log("ChatPanel received:", `contextType="${contextType}", contextId="${contextId}", sessionId="${sessionId}"`);
  }, [contextType, contextId, sessionId]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Handle pending AI actions with automatic navigation
  useEffect(() => {
    if (pendingActions.length > 0) {
      pendingActions.forEach((action) => {
        // Handle navigation actions from AI automatically
        const actionType = action.type as string;
        if (actionType === 'navigate_to_exercise' && (action as any).exercise_id) {
          console.log(`Auto-navigating to exercise: ${(action as any).exercise_id}`);
          router.push(`/exercise/${(action as any).exercise_id}?session=${sessionId}`);
        } else if (actionType === 'navigate_to_node' && (action as any).node_id) {
          console.log(`Auto-navigating to node: ${(action as any).node_id}`);
          router.push(`/learn/${(action as any).node_id}`);
        } else if (onActionReceived) {
          // Pass other actions to parent handler
          onActionReceived(action);
        }
      });
      clearPendingActions();
    }
  }, [pendingActions, router, sessionId, onActionReceived, clearPendingActions]);

  // Memoize handlers for performance
  const handleSendMessage = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim() || isLoading) return;

    const message = inputValue.trim();
    setInputValue("");

    // Debug logging
    console.log("ChatPanel sending message:", {
      message: message.substring(0, 50),
      contextType,
      contextId,
      sessionId
    });

    try {
      if (sessionId) {
        await continueLearningSession(sessionId, message);
      } else {
        // Always use teacher context in learning nodes
        await sendMessage(message, contextType, contextId);
      }
    } catch (err) {
      console.error("Failed to send message:", err);
    }
  }, [inputValue, isLoading, sessionId, contextType, contextId, sendMessage, continueLearningSession]);

  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e as any);
    }
  }, [handleSendMessage]);

  return (
    <Card className="flex flex-col h-full border-0 rounded-none shadow-none">
      <CardHeader className="flex-shrink-0 bg-gradient-to-r from-green-50 to-emerald-100/50 dark:from-green-900/20 dark:to-emerald-900/30 border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <GraduationCap className="h-5 w-5 text-green-600 dark:text-green-400" />
            <CardTitle className="text-lg">AI Teacher</CardTitle>
          </div>
          <Badge variant="secondary" className="gap-1 text-xs">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            Online
          </Badge>
        </div>
        <CardDescription className="text-xs mt-1">
          Get help with exercises, concepts, and learning materials
        </CardDescription>
      </CardHeader>

      <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
            <GraduationCap className="h-12 w-12 mb-4 text-green-500/50" />
            <p className="text-lg font-medium mb-2">Start Learning!</p>
            <p className="text-sm">Ask questions about concepts and exercises</p>
          </div>
        )}

        <AnimatePresence mode="sync">
          {messages.map((msg, idx) => (
            <MessageBubble key={`msg-${idx}-${msg.timestamp}`} message={msg as any} index={idx} />
          ))}
        </AnimatePresence>

        {isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="flex justify-start"
          >
            <div className="bg-muted rounded-lg px-4 py-2">
              <div className="flex space-x-2">
                {[0, 1, 2].map((i) => (
                  <motion.div
                    key={i}
                    className="w-2 h-2 bg-muted-foreground/50 rounded-full"
                    animate={{
                      y: [0, -8, 0],
                      opacity: [0.5, 1, 0.5],
                    }}
                    transition={{
                      duration: 0.6,
                      repeat: Infinity,
                      delay: i * 0.15,
                      ease: "easeInOut",
                    }}
                  />
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {error && (
          <div className="bg-destructive/10 border border-destructive/30 rounded-lg p-3">
            <div className="flex items-start gap-2">
              <AlertCircle className="h-4 w-4 text-destructive mt-0.5" />
              <div className="flex-1">
                <p className="text-sm text-destructive">{error}</p>
                <Button
                  variant="link"
                  size="sm"
                  onClick={clearError}
                  className="h-auto p-0 text-xs text-destructive hover:text-destructive/80"
                >
                  Dismiss
                </Button>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </CardContent>

      <div className="flex-shrink-0 p-4 border-t bg-background">
        <form onSubmit={handleSendMessage} className="flex gap-2">
          <Input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask Teacher..."
            disabled={isLoading}
            className="flex-1"
          />
          <Button
            type="submit"
            disabled={!inputValue.trim() || isLoading}
            size="icon"
            className="shrink-0"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </form>
      </div>
    </Card>
  );
}
