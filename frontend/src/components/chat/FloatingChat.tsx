"use client";

import { useState, useEffect, useRef } from "react";
import { useChatStore } from "@/stores/chatStore";
import ReactMarkdown from "react-markdown";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Send,
  Loader2,
  MessageSquare,
  X,
  Minimize2,
  Maximize2,
  Sparkles,
  Calendar,
  Info,
  AlertCircle
} from "lucide-react";
import { cn } from "@/lib/utils";

type AssistantType = "planning" | "about";

export default function FloatingChat() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [activeAssistant, setActiveAssistant] = useState<AssistantType>("planning");
  const [inputValue, setInputValue] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    messages,
    isLoading,
    error,
    sendMessage,
    clearError,
  } = useChatStore();

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim() || isLoading) return;

    const message = inputValue.trim();
    setInputValue("");

    try {
      // Send message with context based on active assistant
      await sendMessage(message, activeAssistant, "general");
    } catch (err) {
      console.error("Failed to send message:", err);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  // Floating button when closed
  if (!isOpen) {
    return (
      <Button
        size="lg"
        className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg hover:scale-110 transition-transform z-50"
        onClick={() => setIsOpen(true)}
      >
        <MessageSquare className="h-6 w-6" />
      </Button>
    );
  }

  // Minimized state
  if (isMinimized) {
    return (
      <div className="fixed bottom-6 right-6 z-50">
        <Card className="w-80 shadow-xl">
          <CardHeader className="cursor-pointer p-4" onClick={() => setIsMinimized(false)}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5 text-primary" />
                <CardTitle className="text-sm">AI Assistant</CardTitle>
              </div>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="ghost"
                  className="h-6 w-6 p-0"
                  onClick={(e) => {
                    e.stopPropagation();
                    setIsMinimized(false);
                  }}
                >
                  <Maximize2 className="h-3 w-3" />
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  className="h-6 w-6 p-0"
                  onClick={(e) => {
                    e.stopPropagation();
                    setIsOpen(false);
                  }}
                >
                  <X className="h-3 w-3" />
                </Button>
              </div>
            </div>
          </CardHeader>
        </Card>
      </div>
    );
  }

  // Full chat window
  return (
    <div className="fixed bottom-6 right-6 z-50 w-96 max-h-[600px]">
      <Card className="flex flex-col h-full shadow-2xl">
        <CardHeader className="bg-gradient-to-r from-primary/10 to-purple-100/50 dark:from-primary/20 dark:to-purple-900/30 pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5 text-primary" />
              <CardTitle className="text-base">AI Assistant</CardTitle>
            </div>
            <div className="flex gap-1">
              <Button
                size="sm"
                variant="ghost"
                className="h-7 w-7 p-0"
                onClick={() => setIsMinimized(true)}
              >
                <Minimize2 className="h-3 w-3" />
              </Button>
              <Button
                size="sm"
                variant="ghost"
                className="h-7 w-7 p-0"
                onClick={() => setIsOpen(false)}
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
          </div>
          <CardDescription className="text-xs">
            Choose your assistant below
          </CardDescription>
        </CardHeader>

        <Tabs
          value={activeAssistant}
          onValueChange={(value) => setActiveAssistant(value as AssistantType)}
          className="flex flex-col flex-1 overflow-hidden"
        >
          <div className="px-4 pt-3">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="planning" className="text-xs">
                <Calendar className="h-3 w-3 mr-1" />
                Planner
              </TabsTrigger>
              <TabsTrigger value="about" className="text-xs">
                <Info className="h-3 w-3 mr-1" />
                About
              </TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="planning" className="flex-1 overflow-hidden m-0">
            <div className="px-4 py-2 bg-blue-50 dark:bg-blue-900/20 border-b">
              <div className="flex items-start gap-2">
                <Calendar className="h-4 w-4 text-blue-600 dark:text-blue-400 mt-0.5" />
                <div>
                  <p className="text-xs font-medium text-blue-900 dark:text-blue-100">
                    Planning Assistant
                  </p>
                  <p className="text-xs text-blue-700 dark:text-blue-300">
                    Creates learning plans and nodes. Asks questions, then builds your plan.
                  </p>
                </div>
              </div>
            </div>
            <ChatMessages
              messages={messages.filter(m => !m.context_type || m.context_type === 'planning')}
              isLoading={isLoading}
              error={error}
              clearError={clearError}
              messagesEndRef={messagesEndRef}
            />
          </TabsContent>

          <TabsContent value="about" className="flex-1 overflow-hidden m-0">
            <div className="px-4 py-2 bg-purple-50 dark:bg-purple-900/20 border-b">
              <div className="flex items-start gap-2">
                <Info className="h-4 w-4 text-purple-600 dark:text-purple-400 mt-0.5" />
                <div>
                  <p className="text-xs font-medium text-purple-900 dark:text-purple-100">
                    About & Help
                  </p>
                  <p className="text-xs text-purple-700 dark:text-purple-300">
                    Learn about the app features and how to use them
                  </p>
                </div>
              </div>
            </div>
            <ChatMessages
              messages={messages.filter(m => m.context_type === 'about')}
              isLoading={isLoading}
              error={error}
              clearError={clearError}
              messagesEndRef={messagesEndRef}
            />
          </TabsContent>

          <div className="p-3 border-t bg-background">
            <form onSubmit={handleSendMessage} className="flex gap-2">
              <Input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={`Ask ${activeAssistant === 'planning' ? 'Planner' : 'About'}...`}
                disabled={isLoading}
                className="flex-1 text-sm"
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
        </Tabs>
      </Card>
    </div>
  );
}

// Separate component for chat messages
function ChatMessages({
  messages,
  isLoading,
  error,
  clearError,
  messagesEndRef
}: {
  messages: any[];
  isLoading: boolean;
  error: string | null;
  clearError: () => void;
  messagesEndRef: React.RefObject<HTMLDivElement>;
}) {
  return (
    <CardContent className="flex-1 overflow-y-auto p-3 space-y-3" style={{ maxHeight: "350px" }}>
      {messages.length === 0 && (
        <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground py-8">
          <Sparkles className="h-10 w-10 mb-3 text-primary/50" />
          <p className="text-sm font-medium mb-1">Start a conversation!</p>
          <p className="text-xs">I'm here to help you</p>
        </div>
      )}

      {messages.map((msg, idx) => (
        <div
          key={idx}
          className={cn(
            "flex",
            msg.role === "user" ? "justify-end" : "justify-start"
          )}
        >
          <div
            className={cn(
              "max-w-[85%] rounded-lg px-3 py-2 text-sm",
              msg.role === "user"
                ? "bg-primary text-primary-foreground"
                : "bg-muted"
            )}
          >
            <ReactMarkdown className="prose prose-sm dark:prose-invert max-w-none">
              {msg.content}
            </ReactMarkdown>
            <div
              className={cn(
                "text-xs mt-1",
                msg.role === "user" ? "text-primary-foreground/70" : "text-muted-foreground"
              )}
            >
              {new Date(msg.timestamp).toLocaleTimeString()}
            </div>
          </div>
        </div>
      ))}

      {isLoading && (
        <div className="flex justify-start">
          <div className="bg-muted rounded-lg px-3 py-2">
            <div className="flex space-x-2">
              <div className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce"></div>
              <div
                className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce"
                style={{ animationDelay: "150ms" }}
              ></div>
              <div
                className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce"
                style={{ animationDelay: "300ms" }}
              ></div>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="bg-destructive/10 border border-destructive/30 rounded-lg p-2">
          <div className="flex items-start gap-2">
            <AlertCircle className="h-3 w-3 text-destructive mt-0.5 shrink-0" />
            <div className="flex-1">
              <p className="text-xs text-destructive">{error}</p>
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
  );
}
