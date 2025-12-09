"use client";

import dynamic from "next/dynamic";
import { usePathname } from "next/navigation";

// Dynamically import FloatingChat to avoid SSR issues
const FloatingChat = dynamic(() => import("./FloatingChat"), {
  ssr: false,
});

export default function FloatingChatWrapper() {
  const pathname = usePathname();

  // Don't show on login/register pages
  if (pathname === "/login" || pathname === "/register") {
    return null;
  }

  // Don't show floating chat on learning node or exercise pages
  // (the side panel chat will be shown instead)
  if (pathname?.startsWith("/learn/") ||
      pathname?.startsWith("/exercise/") ||
      pathname?.startsWith("/nodes/")) {
    return null;
  }

  return <FloatingChat />;
}
