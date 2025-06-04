import React from 'react';

interface TypingIndicatorProps {
  isVisible: boolean;
  userName?: string;
}

export const TypingIndicator: React.FC<TypingIndicatorProps> = ({ 
  isVisible, 
  userName = 'AI Assistant' 
}) => {
  if (!isVisible) return null;

  return (
    <div className="flex justify-start mb-4 animate-pulse">
      <div className="bg-white rounded-2xl rounded-bl-sm px-4 py-3 shadow-md border border-gray-100 max-w-[70%]">
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-500 font-medium">{userName} is typing</span>
          <div className="flex space-x-1">
            <div 
              className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
              style={{ animationDelay: '0ms', animationDuration: '1.4s' }}
            />
            <div 
              className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
              style={{ animationDelay: '200ms', animationDuration: '1.4s' }}
            />
            <div 
              className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
              style={{ animationDelay: '400ms', animationDuration: '1.4s' }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}; 