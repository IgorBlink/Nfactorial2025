export type MessageStatus = 'sent' | 'delivered' | 'read';
export type MessageType = 'text' | 'image' | 'file';
export type SenderType = 'user' | 'ai';
export type ChatType = 'human' | 'ai';

export interface Message {
  id: string;
  text: string;
  senderId: SenderType;
  timestamp: number;
  status: MessageStatus;
  type: MessageType;
}

export interface Chat {
  id: string;
  name: string;
  avatar?: string;
  messages: Message[];
  isTyping?: boolean;
  lastSeen?: number;
  type: ChatType;
  isOnline?: boolean;
  lastMessage?: Message;
  unreadCount?: number;
}

export interface User {
  id: string;
  name: string;
  avatar?: string;
  isOnline: boolean;
}

export type Theme = 'light' | 'dark';

export interface ChatInputEvent extends React.FormEvent<HTMLFormElement> {
  target: HTMLFormElement & {
    message: HTMLInputElement;
  };
}

export interface ChatInputChangeEvent extends React.ChangeEvent<HTMLInputElement> {
  target: HTMLInputElement;
}

export interface ChatKeyboardEvent extends React.KeyboardEvent<HTMLInputElement> {
  target: HTMLInputElement;
} 