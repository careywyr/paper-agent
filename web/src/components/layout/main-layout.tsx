"use client";

import { ReactNode, useState, useEffect } from 'react';
import { Sidebar } from '@/components/ui/sidebar';

interface MainLayoutProps {
  children: ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  // 使用 localStorage 记住侧边栏状态，默认展开
  const [isCollapsed, setIsCollapsed] = useState(false);
  
  // 在客户端加载时读取保存的状态
  useEffect(() => {
    const savedState = localStorage.getItem('sidebarCollapsed');
    if (savedState) {
      setIsCollapsed(savedState === 'true');
    }
  }, []);
  
  // 切换侧边栏状态
  const toggleSidebar = () => {
    const newState = !isCollapsed;
    setIsCollapsed(newState);
    localStorage.setItem('sidebarCollapsed', String(newState));
  };

  return (
    <div className="flex h-screen">
      {/* 侧边栏 */}
      <Sidebar isCollapsed={isCollapsed} toggleSidebar={toggleSidebar} />
      
      {/* 主内容区域 */}
      <div className="flex-1 overflow-auto transition-all duration-300">
        {children}
      </div>
    </div>
  );
}
