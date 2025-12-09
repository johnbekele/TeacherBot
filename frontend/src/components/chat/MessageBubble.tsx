"use client";

import { memo } from "react";
import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import InteractiveComponent from "./InteractiveComponent";
import { cn } from "@/lib/utils";

interface Message {
  role: string;
  content: string;
  timestamp: number | Date;
  component?: any;
}

interface MessageBubbleProps {
  message: Message;
  index: number;
}

// Helper function to detect and parse grading results in messages
const parseGradingResult = (content: string) => {
  const scoreMatch = content.match(/scored?\s+(\d+)\/100/i);
  if (!scoreMatch) return null;
  const score = parseInt(scoreMatch[1]);
  return { score, passed: score >= 70 };
};

// Memoized message bubble component for performance
// Only re-renders when message content actually changes
const MessageBubble = memo(({ message, index }: MessageBubbleProps) => {
  // Detect grading results in AI messages for rich display
  const gradingResult = message.role !== "user" ? parseGradingResult(message.content) : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{
        duration: 0.3,
        ease: "easeOut",
        delay: index * 0.05 // Stagger animation for multiple messages
      }}
      className={cn(
        "flex mb-4",
        message.role === "user" ? "justify-end" : "justify-start"
      )}
    >
      <motion.div
        whileHover={{ scale: 1.02 }}
        className={cn(
          "max-w-[80%] rounded-lg px-4 py-2",
          message.role === "user"
            ? "bg-primary text-primary-foreground"
            : "bg-muted"
        )}
      >
        {/* Rich grading display for exercise feedback */}
        {gradingResult && (
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className={cn(
              "mb-3 p-3 rounded-md border",
              gradingResult.passed
                ? "bg-green-50 dark:bg-green-950 border-green-200 dark:border-green-800"
                : "bg-yellow-50 dark:bg-yellow-950 border-yellow-200 dark:border-yellow-800"
            )}
          >
            <div className="flex items-center gap-2 mb-1">
              <span className="text-2xl">{gradingResult.passed ? "✅" : "📝"}</span>
              <span className="font-semibold text-base">
                Score: {gradingResult.score}/100
              </span>
            </div>
            <div className={cn(
              "text-xs",
              gradingResult.passed
                ? "text-green-700 dark:text-green-300"
                : "text-yellow-700 dark:text-yellow-300"
            )}>
              {gradingResult.passed ? "Great job! Moving to next challenge..." : "Keep practicing - you're learning!"}
            </div>
          </motion.div>
        )}

        <ReactMarkdown>{message.content}</ReactMarkdown>

        {message.component && message.role !== "user" && (
          <InteractiveComponent component={message.component} />
        )}

        <div
          className={cn(
            "text-xs mt-1",
            message.role === "user" ? "text-primary-foreground/70" : "text-muted-foreground"
          )}
        >
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>
      </motion.div>
    </motion.div>
  );
}, (prevProps, nextProps) => {
  // Custom comparison function - only re-render if message actually changed
  return (
    prevProps.message.content === nextProps.message.content &&
    prevProps.message.role === nextProps.message.role &&
    prevProps.message.timestamp === nextProps.message.timestamp &&
    prevProps.message.component === nextProps.message.component
  );
});

MessageBubble.displayName = "MessageBubble";

export default MessageBubble;
