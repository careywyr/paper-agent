"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, History, Settings, ChevronLeft, ChevronRight } from 'lucide-react';

interface SidebarItemProps {
  icon: React.ReactNode;
  label: string;
  href: string;
  isActive: boolean;
  isCollapsed: boolean;
}

const SidebarItem = ({ icon, label, href, isActive, isCollapsed }: SidebarItemProps) => {
  return (
    <Link 
      href={href}
      className={`flex items-center ${isCollapsed ? 'justify-center' : 'gap-3 px-4'} py-3 rounded-lg transition-all duration-200 ${
        isActive 
          ? 'bg-blue-100 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400' 
          : 'hover:bg-gray-100 dark:hover:bg-gray-800/50'
      }`}
      title={isCollapsed ? label : ''}
    >
      <div className="w-5 h-5">{icon}</div>
      {!isCollapsed && <span className="font-medium">{label}</span>}
    </Link>
  );
};

interface SidebarProps {
  isCollapsed: boolean;
  toggleSidebar: () => void;
}

export function Sidebar({ isCollapsed, toggleSidebar }: SidebarProps) {
  const pathname = usePathname();
  
  const menuItems = [
    {
      icon: <Home className="w-5 h-5" />,
      label: '首页',
      href: '/home',
    },
    {
      icon: <History className="w-5 h-5" />,
      label: '历史记录',
      href: '/history',
    },
    {
      icon: <Settings className="w-5 h-5" />,
      label: '设置',
      href: '/settings',
    }
  ];

  return (
    <div className={`h-full ${isCollapsed ? 'w-16' : 'w-64'} border-r border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 flex flex-col transition-all duration-300`}>
      <div className="p-4 border-b border-gray-200 dark:border-gray-800 flex justify-between items-center">
        {!isCollapsed && (
          <h2 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-500 to-purple-500">
            Paper Agent
          </h2>
        )}
        <button 
          onClick={toggleSidebar}
          className="p-1 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          aria-label={isCollapsed ? '展开侧边栏' : '收起侧边栏'}
        >
          {isCollapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
        </button>
      </div>
      <div className="flex-1 p-3 space-y-1">
        {menuItems.map((item) => (
          <SidebarItem
            key={item.href}
            icon={item.icon}
            label={item.label}
            href={item.href}
            isActive={pathname === item.href}
            isCollapsed={isCollapsed}
          />
        ))}
      </div>
    </div>
  );
}
