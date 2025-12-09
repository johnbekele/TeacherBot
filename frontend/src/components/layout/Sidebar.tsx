'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface SidebarProps {
  collapsed: boolean;
}

export default function Sidebar({ collapsed }: SidebarProps) {
  const pathname = usePathname();

  const links = [
    { href: '/dashboard', label: 'Dashboard', icon: '📊' },
    { href: '/nodes', label: 'Learning Path', icon: '🗺️' },
    { href: '/progress', label: 'Progress', icon: '📈' },
    { href: '/settings', label: 'Settings', icon: '⚙️' },
  ];

  if (collapsed) {
    return (
      <aside className="flex w-16 flex-col border-r bg-gray-50 py-4">
        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className={`flex items-center justify-center py-4 text-2xl transition-colors ${
              pathname === link.href
                ? 'bg-primary-100 text-primary-600'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
            title={link.label}
          >
            {link.icon}
          </Link>
        ))}
      </aside>
    );
  }

  return (
    <aside className="flex w-64 flex-col border-r bg-gray-50 py-4">
      <nav className="flex-1 space-y-1 px-3">
        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className={`flex items-center space-x-3 rounded-lg px-4 py-3 text-sm font-medium transition-colors ${
              pathname === link.href
                ? 'bg-primary-100 text-primary-600'
                : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            <span className="text-xl">{link.icon}</span>
            <span>{link.label}</span>
          </Link>
        ))}
      </nav>
    </aside>
  );
}
