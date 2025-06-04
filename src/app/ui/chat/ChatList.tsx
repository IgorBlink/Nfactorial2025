import React from 'react';
import type { Chat } from '../../model/types';

interface ChatListProps {
  chats: Chat[];
  onChatSelect: (chatId: string) => void;
  selectedChatId?: string;
}

export const ChatList: React.FC<ChatListProps> = ({ 
  chats, 
  onChatSelect, 
  selectedChatId
}) => {
  const humanChats = chats.filter(chat => chat.type === 'human');
  const aiChats = chats.filter(chat => chat.type === 'ai');

  return (
    <div className="w-80 h-full flex flex-col bg-white border-r border-gray-200">
      {/* Simple Header */}
      <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-blue-500 to-purple-600">
        <h2 className="text-lg font-bold text-white">Chats</h2>
      </div>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent">
        {aiChats.length > 0 && (
          <>
            <div className="px-4 py-3 text-sm font-semibold text-gray-500 bg-gray-50/50">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                AI Assistants
              </div>
            </div>
            {aiChats.map(chat => (
              <ChatListItem
                key={chat.id}
                chat={chat}
                isSelected={chat.id === selectedChatId}
                onClick={() => onChatSelect(chat.id)}
              />
            ))}
          </>
        )}

        {humanChats.length > 0 && (
          <>
            <div className="px-4 py-3 text-sm font-semibold text-gray-500 bg-gray-50/50">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                People
              </div>
            </div>
            {humanChats.map(chat => (
              <ChatListItem
                key={chat.id}
                chat={chat}
                isSelected={chat.id === selectedChatId}
                onClick={() => onChatSelect(chat.id)}
              />
            ))}
          </>
        )}
      </div>
    </div>
  );
};

interface ChatListItemProps {
  chat: Chat;
  isSelected: boolean;
  onClick: () => void;
}

const ChatListItem: React.FC<ChatListItemProps> = ({ 
  chat, 
  isSelected, 
  onClick
}) => {
  const lastMessage = chat.messages[chat.messages.length - 1];

  return (
    <div
      className={`px-4 py-3 cursor-pointer transition-all duration-200 border-l-4 ${
        isSelected 
          ? 'bg-blue-50 border-l-blue-500 shadow-sm' 
          : 'border-l-transparent hover:bg-gray-50'
      }`}
      onClick={onClick}
    >
      <div className="flex items-center">
        <div className="relative flex-shrink-0">
          <img
            src={chat.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(chat.name)}&background=3b82f6&color=ffffff`}
            alt={chat.name}
            className="w-12 h-12 rounded-full shadow-md"
          />
          {chat.isOnline && (
            <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white shadow-sm online-pulse" />
          )}
        </div>
        
        <div className="ml-3 flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-gray-900 truncate">
              {chat.name}
            </h3>
            {lastMessage && (
              <span className="text-xs text-gray-500 flex-shrink-0 ml-2">
                {new Date(lastMessage.timestamp).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </span>
            )}
          </div>
          
          {lastMessage && (
            <p className="text-sm text-gray-500 truncate mt-1">
              {lastMessage.senderId === 'user' && (
                <span className="text-blue-600 font-medium">You: </span>
              )}
              {lastMessage.text}
            </p>
          )}
          
          {chat.messages.length === 0 && (
            <p className="text-sm text-gray-400 italic">No messages yet</p>
          )}
        </div>
        
        {typeof chat.unreadCount === 'number' && chat.unreadCount > 0 && (
          <div className="ml-2 bg-blue-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-medium shadow-sm">
            {chat.unreadCount > 99 ? '99+' : chat.unreadCount}
          </div>
        )}
      </div>
    </div>
  );
}; 