import React, { useState, useRef, useEffect } from 'react';
import type { Message, Chat } from '../../model/types';
import type { TextareaChangeEvent, KeyboardEventType, FormEventType } from '../../model/events';

interface ChatAreaProps {
  chat: Chat;
  messages: Message[];
  onSendMessage: (text: string) => void;
  isLoading: boolean;
}

export const ChatArea: React.FC<ChatAreaProps> = ({ chat, messages, onSendMessage, isLoading }) => {
  const [messageText, setMessageText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: FormEventType) => {
    e.preventDefault();
    const trimmedMessage = messageText.trim();
    if (trimmedMessage && !isLoading) {
      setMessageText('');
      await onSendMessage(trimmedMessage);
    }
  };

  const handleKeyPress = (e: KeyboardEventType) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as FormEventType);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full max-h-screen overflow-hidden">
      <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center shrink-0">
        <div className="relative">
          <img
            src={chat.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(chat.name)}`}
            alt={chat.name}
            className="w-10 h-10 rounded-full"
          />
          {chat.isOnline && (
            <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-white" />
          )}
        </div>
        <div className="ml-4">
          <h2 className="text-lg font-medium text-gray-900">{chat.name}</h2>
          {isLoading ? (
            <div className="flex items-center text-sm text-gray-500">
              <span className="mr-2">thinking</span>
              <div className="flex space-x-1">
                <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
                <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          ) : chat.isOnline && (
            <p className="text-sm text-gray-500">online</p>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 bg-gray-50" style={{ minHeight: '0px' }}>
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            isOutgoing={message.senderId === 'user'}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="bg-white border-t border-gray-200 px-4 py-3 shrink-0">
        <form onSubmit={handleSubmit} className="flex items-end space-x-4">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={messageText}
              onChange={(e) => setMessageText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={isLoading ? "Please wait for response..." : "Type a message..."}
              className={`w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none transition-opacity duration-200 ${
                isLoading ? 'opacity-50 cursor-not-allowed' : ''
              }`}
              disabled={isLoading}
              rows={1}
              style={{ minHeight: '44px', maxHeight: '120px' }}
            />
          </div>
          <button
            type="submit"
            disabled={!messageText.trim() || isLoading}
            className={`px-4 py-2 rounded-lg transition-all duration-200 ${
              messageText.trim() && !isLoading
                ? 'bg-blue-500 text-white hover:bg-blue-600'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            }`}
          >
            {isLoading ? 'Wait...' : 'Send'}
          </button>
        </form>
      </div>
    </div>
  );
};

interface MessageBubbleProps {
  message: Message;
  isOutgoing: boolean;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, isOutgoing }) => {
  return (
    <div
      className={`flex ${isOutgoing ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div
        className={`max-w-[70%] px-4 py-2 rounded-2xl ${
          isOutgoing
            ? 'bg-blue-500 text-white rounded-br-md'
            : 'bg-white text-gray-900 rounded-bl-md shadow-sm'
        }`}
      >
        <p className="text-sm">{message.text}</p>
        <div className={`flex items-center justify-end mt-1 ${
          isOutgoing ? 'text-blue-100' : 'text-gray-400'
        }`}>
          <span className="text-xs">
            {new Date(message.timestamp).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
          {isOutgoing && (
            <span className="ml-1">
              {message.status === 'read' ? '✓✓' : '✓'}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}; 