"use client";

import { useState } from 'react';
import { ShimmerButton } from '@/components/magicui/shimmer-button';
import { AnimatedGridPattern } from '@/components/magicui/animated-grid-pattern';
import { AnimatedGradientText } from '@/components/magicui/animated-gradient-text';

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<'search' | 'read'>('search');
  
  const recommendedSearches: string[] = [
    '人工智能',
    '机器学习',
    '深度学习',
    'Next.js',
    'React',
    'TypeScript'
  ];

  return (
    <div className="relative h-full flex flex-col items-center justify-center p-4">
      {/* 动画背景 */}
      <div className="absolute inset-0 -z-10">
        <AnimatedGridPattern />
      </div>

      {/* 搜索区域 */}
      <div className="w-full max-w-3xl space-y-8 mx-auto">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold">
            <AnimatedGradientText 
              colorFrom="#3b82f6" 
              colorTo="#8b5cf6"
              speed={2}
              className="font-bold tracking-tight"
            >
              Paper Agent
            </AnimatedGradientText>
          </h1>
        </div>

        {/* Tab切换 */}
        <div className="flex justify-center mb-6">
          <div className="flex bg-white/10 backdrop-blur-sm rounded-full p-1 border border-gray-200/20">
            <button
              onClick={() => setActiveTab('search')}
              className={`px-6 py-2 rounded-full transition-all duration-300 ${
                activeTab === 'search'
                  ? 'bg-white text-gray-900 shadow-lg'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              搜索
            </button>
            <button
              onClick={() => setActiveTab('read')}
              className={`px-6 py-2 rounded-full transition-all duration-300 ${
                activeTab === 'read'
                  ? 'bg-white text-gray-900 shadow-lg'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              阅读
            </button>
          </div>
        </div>

        {/* 输入框区域 */}
        <div className="flex gap-2">
          {activeTab === 'search' ? (
            <input
              type="text"
              placeholder="你想搜索哪方面的论文？..."
              className="flex-1 px-6 py-3 rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300 bg-white/80 backdrop-blur-sm"
            />
          ) : (
            <input
              type="text"
              placeholder="输入论文链接或上传文件进行阅读..."
              className="flex-1 px-6 py-3 rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-300 bg-white/80 backdrop-blur-sm"
            />
          )}
          <ShimmerButton className="px-8 py-3 rounded-full">
            {activeTab === 'search' ? '搜索' : '阅读'}
          </ShimmerButton>
        </div>

        {/* 推荐搜索 */}
        <div className="flex flex-wrap justify-center gap-2 mt-6">
          {recommendedSearches.map((term: string) => (
            <button
              key={term}
              className="px-4 py-2 rounded-full bg-white/10 hover:bg-white/20 backdrop-blur-sm border border-gray-200/20 text-sm transition-all duration-300 hover:scale-105"
            >
              {term}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
