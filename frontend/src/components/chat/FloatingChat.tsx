"use client";

import { useState, useEffect, useRef, useMemo, useCallback, memo } from "react";
import { useChatStore } from "@/stores/chatStore";
import ReactMarkdown from "react-markdown";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
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

  // Memoize filtered messages to prevent recalculation on every render
  const planningMessages = useMemo(
    () => messages.filter(m => !(m as any).context_type || (m as any).context_type === 'planning'),
    [messages]
  );

  const aboutMessages = useMemo(
    () => messages.filter(m => (m as any).context_type === 'about'),
    [messages]
  );

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Memoize handlers to prevent unnecessary re-renders
  const handleSendMessage = useCallback(async (e: React.FormEvent) => {
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
  }, [inputValue, isLoading, sendMessage, activeAssistant]);

  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e as any);
    }
  }, [handleSendMessage]);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  }, []);

  // Floating button when closed
  if (!isOpen) {
    return (
      <Button
        size="lg"
        className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg hover:shadow-primary hover:scale-105 transition-all duration-200 z-50"
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
        <Card className="w-72 sm:w-80 shadow-xl border-border/60">
          <CardHeader className="cursor-pointer p-4" onClick={() => setIsMinimized(false)}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="p-1.5 bg-primary/10 rounded-lg">
                  <MessageSquare className="h-4 w-4 text-primary" />
                </div>
                <CardTitle className="text-sm font-medium">AI Assistant</CardTitle>
              </div>
              <div className="flex gap-1">
                <Button
                  size="sm"
                  variant="ghost"
                  className="h-7 w-7 p-0 hover:bg-accent"
                  onClick={(e) => {
                    e.stopPropagation();
                    setIsMinimized(false);
                  }}
                >
                  <Maximize2 className="h-3.5 w-3.5" />
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  className="h-7 w-7 p-0 hover:bg-accent"
                  onClick={(e) => {
                    e.stopPropagation();
                    setIsOpen(false);
                  }}
                >
                  <X className="h-3.5 w-3.5" />
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
    <div className="fixed bottom-6 right-6 z-50 w-[calc(100vw-3rem)] sm:w-96 max-h-[min(600px,calc(100vh-6rem))]">
      <Card className="flex flex-col h-full shadow-xl border-border/60">
        <CardHeader className="bg-gradient-to-r from-primary/5 to-primary/10 border-b border-border/50 pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="p-2 bg-primary/10 rounded-lg">
                <MessageSquare className="h-4 w-4 text-primary" />
              </div>
              <div>
                <CardTitle className="text-base font-semibold">AI Assistant</CardTitle>
                <CardDescription className="text-xs mt-0.5">
                  Choose your assistant below
                </CardDescription>
              </div>
            </div>
            <div className="flex gap-1">
              <Button
                size="sm"
                variant="ghost"
                className="h-8 w-8 p-0 hover:bg-background/80"
                onClick={() => setIsMinimized(true)}
              >
                <Minimize2 className="h-4 w-4" />
              </Button>
              <Button
                size="sm"
                variant="ghost"
                className="h-8 w-8 p-0 hover:bg-background/80"
                onClick={() => setIsOpen(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>

        <Tabs
          value={activeAssistant}
          onValueChange={(value) => setActiveAssistant(value as AssistantType)}
          className="flex flex-col flex-1 overflow-hidden"
        >
          <div className="px-4 pt-3">
            <TabsList className="grid w-full grid-cols-2 bg-muted/50">
              <TabsTrigger value="planning" className="text-xs data-[state=active]:bg-background data-[state=active]:shadow-sm">
                <Calendar className="h-3.5 w-3.5 mr-1.5" />
                Planner
              </TabsTrigger>
              <TabsTrigger value="about" className="text-xs data-[state=active]:bg-background data-[state=active]:shadow-sm">
                <Info className="h-3.5 w-3.5 mr-1.5" />
                About
              </TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="planning" className="flex-1 overflow-hidden m-0">
            <div className="px-4 py-2.5 bg-primary/5 border-b border-border/50">
              <div className="flex items-start gap-2.5">
                <div className="p-1.5 bg-primary/10 rounded-md mt-0.5">
                  <Calendar className="h-3.5 w-3.5 text-primary" />
                </div>
                <div>
                  <p className="text-xs font-medium text-foreground">
                    Planning Assistant
                  </p>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    Creates learning plans and nodes. Asks questions, then builds your plan.
                  </p>
                </div>
              </div>
            </div>
            <ChatMessages
              messages={planningMessages}
              isLoading={isLoading}
              error={error}
              clearError={clearError}
              messagesEndRef={messagesEndRef}
            />
          </TabsContent>

          <TabsContent value="about" className="flex-1 overflow-hidden m-0">
            <div className="px-4 py-2.5 bg-info/5 border-b border-border/50">
              <div className="flex items-start gap-2.5">
                <div className="p-1.5 bg-info/10 rounded-md mt-0.5">
                  <Info className="h-3.5 w-3.5 text-info" />
                </div>
                <div>
                  <p className="text-xs font-medium text-foreground">
                    About & Help
                  </p>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    Learn about the app features and how to use them
                  </p>
                </div>
              </div>
            </div>
            <ChatMessages
              messages={aboutMessages}
              isLoading={isLoading}
              error={error}
              clearError={clearError}
              messagesEndRef={messagesEndRef}
            />
          </TabsContent>

          <div className="p-3 border-t border-border/50 bg-background">
            <form onSubmit={handleSendMessage} className="flex gap-2">
              <Input
                type="text"
                value={inputValue}
                onChange={handleInputChange}
                onKeyPress={handleKeyPress}
                placeholder={`Ask ${activeAssistant === 'planning' ? 'Planner' : 'About'}...`}
                disabled={isLoading}
                className="flex-1 text-sm h-9"
              />
              <Button
                type="submit"
                disabled={!inputValue.trim() || isLoading}
                size="icon"
                className="shrink-0 h-9 w-9"
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

// Memoized chat messages component to prevent unnecessary re-renders
const ChatMessages = memo(function ChatMessages({
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
    <CardContent className="flex-1 overflow-y-auto p-3 space-y-3" style={{ maxHeight: "320px" }}>
      {messages.length === 0 && (
        <div className="flex flex-col items-center justify-center h-full text-center py-8">
          <div className="p-3 bg-primary/10 rounded-xl mb-3">
            <Sparkles className="h-8 w-8 text-primary" />
          </div>
          <p className="text-sm font-medium text-foreground mb-1">Start a conversation!</p>
          <p className="text-xs text-muted-foreground">I'm here to help you</p>
        </div>
      )}

      {messages.map((msg, idx) => (
        <div
          key={idx}
          className={cn(
            "flex animate-fade-in",
            msg.role === "user" ? "justify-end" : "justify-start"
          )}
        >
          <div
            className={cn(
              "max-w-[85%] rounded-xl px-3.5 py-2.5 text-sm",
              msg.role === "user"
                ? "bg-primary text-primary-foreground shadow-sm"
                : "bg-muted/70 text-foreground"
            )}
          >
            <ReactMarkdown className="prose prose-sm dark:prose-invert max-w-none [&>p]:m-0 [&>p]:leading-relaxed">
              {msg.content}
            </ReactMarkdown>
            <div
              className={cn(
                "text-[10px] mt-1.5 opacity-70",
                msg.role === "user" ? "text-primary-foreground" : "text-muted-foreground"
              )}
            >
              {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </div>
          </div>
        </div>
      ))}

      {isLoading && (
        <div className="flex justify-start animate-fade-in">
          <div className="bg-muted/70 rounded-xl px-4 py-3">
            <div className="flex space-x-1.5">
              <div className="w-2 h-2 bg-muted-foreground/40 rounded-full animate-bounce"></div>
              <div
                className="w-2 h-2 bg-muted-foreground/40 rounded-full animate-bounce"
                style={{ animationDelay: "150ms" }}
              ></div>
              <div
                className="w-2 h-2 bg-muted-foreground/40 rounded-full animate-bounce"
                style={{ animationDelay: "300ms" }}
              ></div>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-3 animate-fade-in">
          <div className="flex items-start gap-2">
            <AlertCircle className="h-4 w-4 text-destructive mt-0.5 shrink-0" />
            <div className="flex-1">
              <p className="text-xs text-destructive leading-relaxed">{error}</p>
              <Button
                variant="link"
                size="sm"
                onClick={clearError}
                className="h-auto p-0 text-xs text-destructive hover:text-destructive/80 mt-1"
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
});
