import React, { useState, useRef, useEffect } from 'react';

interface EnhancedChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  placeholder?: string;
}

export const EnhancedChatInput: React.FC<EnhancedChatInputProps> = ({ 
  onSendMessage, 
  isLoading,
  placeholder = "Type a message..." 
}) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  }, [message]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmedMessage = message.trim();
    if (trimmedMessage && !isLoading) {
      onSendMessage(trimmedMessage);
      setMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  const canSend = message.trim() && !isLoading;

  return (
    <div className="p-4 bg-white/80 backdrop-blur-md border-t border-gray-200/50">
      <form onSubmit={handleSubmit} className="flex items-end space-x-3">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={isLoading ? "AI is thinking..." : placeholder}
            disabled={isLoading}
            rows={1}
            className={`w-full px-4 py-3 pr-12 bg-gray-50 border border-gray-200 rounded-2xl 
              focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
              resize-none transition-all duration-200 text-sm leading-relaxed
              ${isLoading ? 'opacity-60 cursor-not-allowed' : 'hover:bg-gray-100 focus:bg-white'}
              placeholder:text-gray-400`}
            style={{ minHeight: '48px', maxHeight: '120px' }}
          />
          
          {/* Character counter for long messages */}
          {message.length > 100 && (
            <div className="absolute bottom-1 right-3 text-xs text-gray-400">
              {message.length}/1000
            </div>
          )}
          
          {/* Emoji button */}
          <button
            type="button"
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
            disabled={isLoading}
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM7 9a1 1 0 100-2 1 1 0 000 2zm7-1a1 1 0 11-2 0 1 1 0 012 0zm-.464 5.535a1 1 0 10-1.415-1.414 3 3 0 01-4.242 0 1 1 0 00-1.415 1.414 5 5 0 007.072 0z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
        
        <button
          type="submit"
          disabled={!canSend}
          className={`
            flex items-center justify-center w-12 h-12 rounded-full transition-all duration-200 transform
            ${canSend 
              ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg hover:shadow-xl hover:scale-105 active:scale-95' 
              : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            }
          `}
        >
          {isLoading ? (
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          )}
        </button>
      </form>
    </div>
  );
}; 