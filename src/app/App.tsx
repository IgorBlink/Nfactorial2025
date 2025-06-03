import React, { useState } from 'react';
import { useLocalStorage } from '../shared/hooks/useLocalStorage';
import { getChatResponse } from '../shared/api/gemini';
import { ChatArea } from './components/ChatArea';
import { ChatList } from './components/ChatList';
import type { Message, Chat } from './model/types';

const INITIAL_CHAT: Chat = {
  id: '1',
  name: 'AI Assistant',
  avatar: 'https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d4735304ff6292a690345.svg',
  messages: [],
  type: 'ai'
};

export const App: React.FC = () => {
  const [chat, setChat] = useLocalStorage<Chat>('gemini-chat', INITIAL_CHAT);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (text: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      text: text.trim(),
      senderId: 'user',
      timestamp: Date.now(),
      status: 'sent',
      type: 'text'
    };

    setChat(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage]
    }));
    setIsLoading(true);

    try {
      // Показываем, что AI печатает
      setChat(prev => ({ ...prev, isTyping: true }));

      const aiResponse = await getChatResponse(text);
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: aiResponse,
        senderId: 'ai',
        timestamp: Date.now(),
        status: 'read',
        type: 'text'
      };

      // Обновляем статус сообщения пользователя на "прочитано" и добавляем ответ AI
      setChat(prev => ({
        ...prev,
        isTyping: false,
        messages: [
          ...prev.messages.slice(0, -1),
          { ...prev.messages[prev.messages.length - 1], status: 'read' },
          aiMessage
        ]
      }));
    } catch (error) {
      console.error('Error getting AI response:', error);
      // В случае ошибки помечаем сообщение пользователя как доставленное
      setChat(prev => ({
        ...prev,
        isTyping: false,
        messages: prev.messages.map(msg => 
          msg.id === userMessage.id ? { ...msg, status: 'delivered' } : msg
        )
      }));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 flex flex-col overflow-hidden">
      <header className="bg-white border-b border-gray-200 p-4 shrink-0">
        <h1 className="text-xl font-bold text-gray-800">Telegram Clone - Gemini AI Chat</h1>
      </header>
      <main className="flex-1 flex min-h-0">
        <ChatList
          chats={[chat]}
          selectedChatId={chat.id}
          onChatSelect={() => {}}
        />
        <ChatArea
          chat={chat}
          messages={chat.messages}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
        />
      </main>
    </div>
  );
}; 