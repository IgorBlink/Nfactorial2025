import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import type { Chat } from '../../app/model/types';

export const useChatPersistence = () => {
  const queryClient = useQueryClient();

  useEffect(() => {
    // Подписываемся на изменения в кэше TanStack Query
    const unsubscribe = queryClient.getQueryCache().subscribe((event) => {
      if (event?.query.queryKey[0] === 'chat' && event?.type === 'updated') {
        const chatId = event.query.queryKey[1] as string;
        const chatData = event.query.state.data as Chat;
        
        if (chatData) {
          // Сохраняем обновленные данные чата в localStorage
          localStorage.setItem(`gemini-chat-${chatId}`, JSON.stringify(chatData));
          
          // Также обновляем список всех чатов
          const allChats = [chatData]; // В простом случае у нас один чат
          localStorage.setItem('all-chats', JSON.stringify(allChats));
        }
      }
    });

    return unsubscribe;
  }, [queryClient]);

  // Функция для очистки старых данных
  const clearOldChatData = () => {
    const keys = Object.keys(localStorage);
    keys.forEach(key => {
      if (key.startsWith('gemini-chat-') || key === 'all-chats') {
        localStorage.removeItem(key);
      }
    });
    
    // Очищаем кэш TanStack Query
    queryClient.clear();
  };

  return { clearOldChatData };
}; 