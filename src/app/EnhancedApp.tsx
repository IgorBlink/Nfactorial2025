import React, { useState } from 'react';
import { useChat } from '../shared/hooks/useChat';
import { useChatPersistence } from '../shared/hooks/useChatPersistence';
import { ChatList } from './ui/chat/ChatList';
import { EnhancedChatArea } from './ui/chat/EnhancedChatArea';

export const EnhancedApp: React.FC = () => {
  const [selectedChatId] = useState('1'); // По умолчанию выбираем первый чат
  
  const { data: chat, isLoading, error } = useChat(selectedChatId);
  const { clearOldChatData } = useChatPersistence();

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Loading your conversations...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-gradient-to-br from-red-50 to-pink-100 flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="w-16 h-16 bg-red-500 rounded-full mx-auto mb-4 flex items-center justify-center">
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.728-.833-2.498 0L4.316 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Something went wrong</h2>
          <p className="text-gray-600 mb-4">We couldn't load your chat. Please try refreshing the page.</p>
          <button 
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
          >
            Refresh Page
          </button>
        </div>
      </div>
    );
  }

  if (!chat) {
    return null;
  }

  return (
    <div className="h-screen flex bg-gradient-to-br from-gray-50 to-blue-50 overflow-hidden">
      <ChatList
        chats={[chat]}
        selectedChatId={selectedChatId}
        onChatSelect={() => {}}
      />
      <EnhancedChatArea chat={chat} />
    </div>
  );
}; 