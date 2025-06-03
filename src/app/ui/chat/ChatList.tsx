import React, { useState } from 'react';
import type { Chat } from '../../model/types';
import type { InputChangeEvent } from '../../model/events';

interface ChatListProps {
  chats: Chat[];
  onChatSelect: (chatId: string) => void;
  selectedChatId?: string;
}

export const ChatList: React.FC<ChatListProps> = ({ chats, onChatSelect, selectedChatId }) => {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearchChange = (e: InputChangeEvent) => {
    setSearchQuery(e.target.value);
  };

  const filteredChats = chats.filter(chat =>
    chat.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const humanChats = filteredChats.filter(chat => chat.type === 'human');
  const aiChats = filteredChats.filter(chat => chat.type === 'ai');

  return (
    <div className="w-80 flex flex-col min-h-0 bg-white border-r border-gray-200">
      <div className="p-4 border-b border-gray-200 shrink-0">
        <div className="relative">
          <input
            type="text"
            placeholder="Search chats..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={searchQuery}
            onChange={handleSearchChange}
          />
          <svg
            className="absolute left-3 top-2.5 w-5 h-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        {humanChats.length > 0 && (
          <>
            <div className="px-4 py-2 text-sm font-semibold text-gray-500 sticky top-0 bg-white">People</div>
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

        {aiChats.length > 0 && (
          <>
            <div className="px-4 py-2 text-sm font-semibold text-gray-500 sticky top-0 bg-white">AI s</div>
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
      </div>

      <div className="p-4 border-t border-gray-200 shrink-0">
        <button
          className="w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 transition-colors"
          onClick={() => console.log("New chat")}
        >
          New Chat
        </button>
      </div>
    </div>
  );
};

interface ChatListItemProps {
  chat: Chat;
  isSelected: boolean;
  onClick: () => void;
}

const ChatListItem: React.FC<ChatListItemProps> = ({ chat, isSelected, onClick }) => {
  return (
    <div
      className={`px-4 py-3 cursor-pointer hover:bg-gray-100 ${
        isSelected ? 'bg-gray-100' : ''
      }`}
      onClick={onClick}
    >
      <div className="flex items-center">
        <div className="relative">
          <img
            src={chat.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(chat.name)}`}
            alt={chat.name}
            className="w-12 h-12 rounded-full"
          />
          {chat.isOnline && (
            <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-white" />
          )}
        </div>
        <div className="ml-4 flex-1">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-900">{chat.name}</h3>
            {chat.lastMessage && (
              <span className="text-xs text-gray-500">
                {new Date(chat.lastMessage.timestamp).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </span>
            )}
          </div>
          {chat.lastMessage && (
            <p className="text-sm text-gray-500 truncate">{chat.lastMessage.text}</p>
          )}
        </div>
        {typeof chat.unreadCount === 'number' && chat.unreadCount > 0 && (
          <div className="ml-2 bg-blue-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
            {chat.unreadCount}
          </div>
        )}
      </div>
    </div>
  );
}; 