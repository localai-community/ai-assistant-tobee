import type { Metadata } from 'next';
import './styles/globals.css';

export const metadata: Metadata = {
  title: 'LocalAI Community',
  description: 'A modern chat interface for LocalAI Community with MCP and RAG capabilities',
  icons: {
    icon: '🤖',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div id="root">
          {children}
        </div>
      </body>
    </html>
  );
}
