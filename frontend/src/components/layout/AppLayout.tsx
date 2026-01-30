'use client';

import { ReactNode } from 'react';
import { usePathname } from 'next/navigation';
import {
  SidebarProvider,
  SidebarInset,
  SidebarTrigger,
} from '@/components/ui/sidebar';
import { Separator } from '@/components/ui/separator';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { AppSidebar } from './AppSidebar';
import RightPanel from './RightPanel';

interface AppLayoutProps {
  children?: ReactNode;
  sessionId?: string;
  contextType?: string;
  contextId?: string;
  onActionReceived?: (action: any) => void;
}

export default function AppLayout({
  children,
  sessionId,
  contextType,
  contextId,
  onActionReceived
}: AppLayoutProps) {
  const pathname = usePathname();

  // Check if we're on a learning/exercise page (show side panel chat)
  const showRightPanel = pathname?.startsWith('/learn/') ||
                          pathname?.startsWith('/exercise/') ||
                          pathname?.startsWith('/nodes/');

  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset className="flex flex-col h-screen max-h-screen">
        {/* Header */}
        <header className="flex h-14 sm:h-16 shrink-0 items-center gap-2 border-b border-border/60 bg-background/95 backdrop-blur-sm supports-[backdrop-filter]:bg-background/80 transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12 sticky top-0 z-10">
          <div className="flex w-full items-center justify-between px-3 sm:px-4">
            <div className="flex items-center gap-2">
              <SidebarTrigger className="-ml-1 hover:bg-accent/80" />
              <Separator orientation="vertical" className="mr-2 h-4 bg-border/60" />
              <div>
                <h1 className="text-base sm:text-lg font-semibold text-foreground">MyTeacher AI</h1>
              </div>
            </div>
            <ThemeToggle />
          </div>
        </header>

        {/* Main Content Area with Conditional Dual Panels */}
        <div className="flex flex-1 min-h-0 overflow-hidden">
          {showRightPanel ? (
            // Dual panel layout for learning/exercise pages
            <div className="flex w-full h-full min-h-0">
              {/* Left Panel - Learning Pad (scrollable content) */}
              <div className="w-full lg:w-1/2 xl:w-3/5 h-full overflow-y-auto scroll-smooth bg-background">
                <div className="min-h-full">
                  {children}
                </div>
              </div>

              {/* Right Panel - AI Chat (fixed in place, doesn't scroll with content) */}
              <div className="hidden lg:flex lg:w-1/2 xl:w-2/5 h-full flex-col border-l border-border/60 bg-muted/30 overflow-hidden">
                <RightPanel
                  sessionId={sessionId}
                  contextType={contextType}
                  contextId={contextId}
                  onActionReceived={onActionReceived}
                />
              </div>
            </div>
          ) : (
            // Full width content for other pages
            <div className="flex w-full">
              <div className="flex w-full flex-col overflow-hidden">
                <div className="flex-1 overflow-y-auto bg-background">
                  <div className="p-4 sm:p-6 lg:p-8">
                    {children}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}
