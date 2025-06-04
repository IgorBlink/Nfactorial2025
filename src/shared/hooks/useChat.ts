import { useQuery } from '@tanstack/react-query';
import type { Chat } from '../../app/model/types';

const INITIAL_CHAT: Chat = {
  id: '1',
  name: 'AI Assistant',
  avatar: 'https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d4735304ff6292a690345.svg',
  messages: [],
  type: 'ai',
  isOnline: true
};

const getChatData = async (chatId: string): Promise<Chat> => {
  // Simulate API call - in real app this would fetch from server
  const savedChat = localStorage.getItem(`gemini-chat-${chatId}`);
  if (savedChat) {
    return JSON.parse(savedChat);
  }
  return INITIAL_CHAT;
};

export const useChat = (chatId: string) => {
  return useQuery({
    queryKey: ['chat', chatId],
    queryFn: () => getChatData(chatId),
    staleTime: 1000 * 60 * 5, // 5 minutes
    initialData: INITIAL_CHAT
  });
};

// Hook для получения списка чатов
export const useChats = () => {
  return useQuery({
    queryKey: ['chats'],
    queryFn: async (): Promise<Chat[]> => {
      // В реальном приложении здесь был бы API вызов
      const savedChats = localStorage.getItem('all-chats');
      if (savedChats) {
        return JSON.parse(savedChats);
      }
      return [INITIAL_CHAT];
    },
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}; 