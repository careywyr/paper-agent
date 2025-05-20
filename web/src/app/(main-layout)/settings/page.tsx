"use client";

import { AnimatedGridPattern } from '@/components/magicui/animated-grid-pattern';
import { ShimmerButton } from '@/components/magicui/shimmer-button';

export default function SettingsPage() {
  return (
    <div className="relative h-full flex flex-col p-6">
      {/* 动画背景 */}
      <div className="absolute inset-0 -z-10">
        <AnimatedGridPattern />
      </div>

      <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-xl p-6 shadow-md">
        <h1 className="text-2xl font-bold mb-6">设置</h1>
        
        <div className="space-y-6">
          <div className="space-y-4">
            <h2 className="text-lg font-medium">个人信息</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">用户名</label>
                <input 
                  type="text" 
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="请输入用户名"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">邮箱</label>
                <input 
                  type="email" 
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="请输入邮箱"
                />
              </div>
            </div>
          </div>
          
          <div className="space-y-4">
            <h2 className="text-lg font-medium">界面设置</h2>
            <div className="flex items-center justify-between">
              <span>深色模式</span>
              <label className="relative inline-flex items-center cursor-pointer">
                <input 
                  type="checkbox" 
                  className="sr-only peer" 
                  defaultChecked={false}
                  onChange={(e) => console.log('深色模式设置更改:', e.target.checked)}
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
            </div>
            <div className="flex items-center justify-between">
              <span>保存搜索历史</span>
              <label className="relative inline-flex items-center cursor-pointer">
                <input 
                  type="checkbox" 
                  className="sr-only peer" 
                  defaultChecked={true} 
                  onChange={(e) => console.log('保存历史设置更改:', e.target.checked)}
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>
          
          <div className="pt-4">
            <ShimmerButton className="px-4 py-2">
              保存设置
            </ShimmerButton>
          </div>
        </div>
      </div>
    </div>
  );
}
