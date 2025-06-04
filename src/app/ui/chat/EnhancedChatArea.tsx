import React, { useRef, useEffect } from 'react';
import { useSendMessage } from '../../../shared/hooks/useChatMutation';
import { AnimatedMessage } from '../components/AnimatedMessage';
import { TypingIndicator } from '../components/TypingIndicator';
import { EnhancedChatInput } from '../components/EnhancedChatInput';
import type { Chat } from '../../model/types';

interface EnhancedChatAreaProps {
  chat: Chat;
}

export const EnhancedChatArea: React.FC<EnhancedChatAreaProps> = ({ chat }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const sendMessageMutation = useSendMessage();

  const scrollToBottom = (behavior: ScrollBehavior = 'smooth') => {
    messagesEndRef.current?.scrollIntoView({ behavior });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chat.messages, chat.isTyping]);

  const handleSendMessage = (text: string) => {
    sendMessageMutation.mutate({
      text,
      chatId: chat.id
    });
  };

  return (
    <div className="flex-1 flex flex-col bg-gradient-to-br from-gray-50 to-gray-100/50 overflow-hidden">
      {/* Header */}
      <div className="bg-white/90 backdrop-blur-md border-b border-gray-200/50 px-6 py-4 shadow-sm">
        <div className="flex items-center gap-4">
          <div className="relative">
            <img
              src={chat.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(chat.name)}&background=3b82f6&color=ffffff`}
              alt={chat.name}
              className="w-12 h-12 rounded-full ring-2 ring-blue-100 shadow-md"
            />
            {chat.isOnline && (
              <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white shadow-sm online-pulse" />
            )}
          </div>
          <div className="flex-1">
            <h2 className="text-lg font-semibold text-gray-900">{chat.name}</h2>
            <div className="flex items-center space-x-2">
              {chat.isTyping ? (
                <div className="flex items-center text-sm text-blue-600">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse mr-2" />
                  <span className="font-medium">thinking...</span>
                </div>
              ) : chat.isOnline ? (
                <p className="text-sm text-green-600 font-medium">● online</p>
              ) : (
                <p className="text-sm text-gray-500">last seen recently</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-1 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent">
        {chat.messages.length === 0 ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center max-w-md">
              <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full mx-auto mb-4 flex items-center justify-center">
                <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-700 mb-2">Start a conversation</h3>
              <p className="text-gray-500">Send a message to begin chatting with {chat.name}</p>
            </div>
          </div>
        ) : (
          <>
            {chat.messages.map((message, index) => (
              <AnimatedMessage
                key={message.id}
                message={message}
                isNew={index === chat.messages.length - 1}
              />
            ))}
            <TypingIndicator isVisible={!!chat.isTyping} userName={chat.name} />
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <EnhancedChatInput
        onSendMessage={handleSendMessage}
        isLoading={sendMessageMutation.isPending}
        placeholder={`Message ${chat.name}...`}
      />

      {/* Error toast */}
      {sendMessageMutation.error && (
        <div className="absolute bottom-24 left-6 right-6 bg-red-500 text-white px-4 py-3 rounded-lg shadow-lg flex items-center justify-between animate-slide-up">
          <span className="text-sm font-medium">
            Failed to send message. Please try again.
          </span>
          <button
            onClick={() => sendMessageMutation.reset()}
            className="text-white hover:text-red-200 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
}; 