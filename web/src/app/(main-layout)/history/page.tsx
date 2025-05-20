"use client";

import { AnimatedGridPattern } from '@/components/magicui/animated-grid-pattern';

export default function HistoryPage() {
  return (
    <div className="relative h-full flex flex-col p-6">
      {/* 动画背景 */}
      <div className="absolute inset-0 -z-10">
        <AnimatedGridPattern />
      </div>

      <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-xl p-6 shadow-md">
        <h1 className="text-2xl font-bold mb-6">历史记录</h1>
        
        <div className="space-y-4">
          <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
            <div className="flex justify-between items-start">
              <h3 className="font-medium">人工智能最新研究</h3>
              <span className="text-sm text-gray-500">2025-05-20</span>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">搜索了关于人工智能领域的最新研究进展</p>
          </div>
          
          <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
            <div className="flex justify-between items-start">
              <h3 className="font-medium">Next.js 15 新特性</h3>
              <span className="text-sm text-gray-500">2025-05-19</span>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">查询了 Next.js 15 版本的新功能和改进</p>
          </div>
          
          <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
            <div className="flex justify-between items-start">
              <h3 className="font-medium">React 服务器组件</h3>
              <span className="text-sm text-gray-500">2025-05-18</span>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">了解 React 服务器组件的工作原理和最佳实践</p>
          </div>
        </div>
      </div>
    </div>
  );
}
