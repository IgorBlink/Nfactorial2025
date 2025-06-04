import React, { useState, useEffect } from 'react';
import type { Message } from '../../model/types';

interface AnimatedMessageProps {
  message: Message & { text: string | React.ReactNode };
  isNew?: boolean;
}

export const AnimatedMessage: React.FC<AnimatedMessageProps> = ({ message, isNew = false }) => {
  const [isVisible, setIsVisible] = useState(!isNew);
  const isUser = message.senderId === 'user';

  useEffect(() => {
    if (isNew) {
      const timer = setTimeout(() => setIsVisible(true), 50);
      return () => clearTimeout(timer);
    }
  }, [isNew]);

  const getStatusIcon = () => {
    switch (message.status) {
      case 'sent':
        return (
          <svg className="w-4 h-4 text-blue-300" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
        );
      case 'delivered':
        return (
          <div className="flex space-x-0.5">
            <svg className="w-4 h-4 text-blue-300" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            <svg className="w-4 h-4 text-blue-300" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          </div>
        );
      case 'read':
        return (
          <div className="flex space-x-0.5">
            <svg className="w-4 h-4 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            <svg className="w-4 h-4 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 transform transition-all duration-300 ease-out ${
        isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'
      }`}
    >
      <div
        className={`max-w-[70%] px-4 py-3 rounded-2xl relative transition-all duration-200 hover:shadow-md ${
          isUser
            ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-br-sm shadow-lg'
            : 'bg-white text-gray-900 rounded-bl-sm shadow-md border border-gray-100'
        }`}
      >
        <div className="text-sm leading-relaxed whitespace-pre-wrap break-words">
          {typeof message.text === 'string' ? message.text : message.text}
        </div>
        <div className={`flex items-center justify-end gap-2 mt-2 ${
          isUser ? 'text-blue-100' : 'text-gray-400'
        }`}>
          <span className="text-xs font-medium">
            {new Date(message.timestamp).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
          {isUser && getStatusIcon()}
        </div>
        
        {/* Добавляем тонкий градиент для глубины */}
        {isUser && (
          <div className="absolute inset-0 rounded-2xl bg-gradient-to-t from-black/10 to-transparent pointer-events-none" />
        )}
      </div>
    </div>
  );
}; 