import React, { useState, useRef, useEffect } from 'react';
import type { ChatInputEvent, ChatInputChangeEvent, ChatKeyboardEvent } from '../model/types';

interface ChatInputProps {
  onSendMessage: (message: string) => Promise<void>;
  isLoading: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, isLoading }) => {
  const [inputMessage, setInputMessage] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = async (e: ChatInputEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    await onSendMessage(inputMessage);
    setInputMessage('');
  };

  const handleKeyPress = (e: ChatKeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as ChatInputEvent);
    }
  };

  const handleChange = (e: ChatInputChangeEvent) => {
    setInputMessage(e.target.value);
  };

  return (
    <form onSubmit={handleSubmit} className="mt-4 flex gap-2">
      <input
        ref={inputRef}
        type="text"
        value={inputMessage}
        onChange={handleChange}
        onKeyPress={handleKeyPress}
        placeholder="Type a message..."
        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        disabled={isLoading}
      />
      <button
        type="submit"
        disabled={!inputMessage.trim() || isLoading}
        className={`px-4 py-2 rounded-lg ${
          !inputMessage.trim() || isLoading
            ? 'bg-gray-300 text-gray-500'
            : 'bg-blue-500 text-white hover:bg-blue-600'
        }`}
      >
        {isLoading ? 'Sending...' : 'Send'}
      </button>
    </form>
  );
}; 