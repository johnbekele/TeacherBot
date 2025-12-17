import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import '@/styles/globals.css';
import AuthProvider from '@/components/providers/AuthProvider';
import { ChatContextProvider } from '@/contexts/ChatContext';
import { ThemeProvider } from '@/components/providers/ThemeProvider';
import FloatingChatWrapper from '@/components/chat/FloatingChatWrapper';
import { Toaster } from 'sonner';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'MyTeacher - AI DevOps Mentor',
  description: 'Your personal AI-powered DevOps learning platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.className} bg-background text-foreground antialiased`}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <AuthProvider>
            <ChatContextProvider>
              {children}
              <FloatingChatWrapper />
              <Toaster richColors position="top-right" />
            </ChatContextProvider>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
