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
import LeftPanel from './LeftPanel';
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

  // Debug logging
  console.log("AppLayout received:", `contextType="${contextType}", contextId="${contextId}", sessionId="${sessionId}", showRightPanel="${showRightPanel}"`);

  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset className="flex flex-col">
        {/* Header */}
        <header className="flex h-16 shrink-0 items-center gap-2 border-b bg-background transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12">
          <div className="flex w-full items-center justify-between px-4">
            <div className="flex items-center gap-2">
              <SidebarTrigger className="-ml-1" />
              <Separator orientation="vertical" className="mr-2 h-4" />
              <div>
                <h1 className="text-lg font-semibold">MyTeacher AI</h1>
              </div>
            </div>
            <ThemeToggle />
          </div>
        </header>

        {/* Main Content Area with Conditional Dual Panels */}
        <div className="flex flex-1 overflow-hidden">
          {showRightPanel ? (
            // Dual panel layout for learning/exercise pages
            <div className="flex flex-col lg:flex-row w-full">
              {/* Left Panel - Learning Pad */}
              <LeftPanel>{children}</LeftPanel>

              {/* Right Panel - AI Chat */}
              <RightPanel
                sessionId={sessionId}
                contextType={contextType}
                contextId={contextId}
                onActionReceived={onActionReceived}
              />
            </div>
          ) : (
            // Full width content for other pages
            <div className="flex w-full">
              <div className="flex w-full flex-col overflow-hidden">
                <div className="flex-1 overflow-y-auto bg-background p-4 lg:p-6">
                  {children}
                </div>
              </div>
            </div>
          )}
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}
