import { useMutation, useQueryClient } from '@tanstack/react-query';
import { getChatResponse } from '../api/gemini';
import type { Message, Chat } from '../../app/model/types';

interface SendMessageParams {
  text: string;
  chatId: string;
}

interface SendMessageResponse {
  userMessage: Message;
  aiMessage: Message;
}

export const useSendMessage = () => {
  const queryClient = useQueryClient();

  return useMutation<SendMessageResponse, Error, SendMessageParams>({
    mutationFn: async ({ text, chatId }) => {
      const userMessage: Message = {
        id: Date.now().toString(),
        text: text.trim(),
        senderId: 'user',
        timestamp: Date.now(),
        status: 'sent',
        type: 'text'
      };

      // Optimistically update the chat with user message
      queryClient.setQueryData<Chat>(['chat', chatId], (oldChat) => {
        if (!oldChat) return oldChat;
        return {
          ...oldChat,
          messages: [...oldChat.messages, userMessage],
          isTyping: true
        };
      });

      try {
        const aiResponse = await getChatResponse(text);
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: aiResponse,
          senderId: 'ai',
          timestamp: Date.now(),
          status: 'read',
          type: 'text'
        };

        return { userMessage: { ...userMessage, status: 'read' }, aiMessage };
      } catch (error) {
        throw error;
      }
    },
    onSuccess: ({ userMessage, aiMessage }, { chatId }) => {
      // Update chat with both messages and remove typing indicator
      queryClient.setQueryData<Chat>(['chat', chatId], (oldChat) => {
        if (!oldChat) return oldChat;
        
        const updatedMessages = oldChat.messages.map(msg => 
          msg.id === userMessage.id ? userMessage : msg
        );
        
        return {
          ...oldChat,
          messages: [...updatedMessages, aiMessage],
          isTyping: false,
          lastMessage: aiMessage
        };
      });
    },
    onError: (error, { chatId }) => {
      // Remove typing indicator and mark user message as delivered
      queryClient.setQueryData<Chat>(['chat', chatId], (oldChat) => {
        if (!oldChat) return oldChat;
        
        const updatedMessages = oldChat.messages.map(msg => 
          msg.senderId === 'user' && msg.status === 'sent' 
            ? { ...msg, status: 'delivered' } 
            : msg
        );
        
        return {
          ...oldChat,
          messages: updatedMessages,
          isTyping: false
        };
      });
    }
  });
}; 