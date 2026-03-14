import { useState, useRef } from 'react';
import { ChatMessage } from '../types';

export const useSendChatMessage = () => {
  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    try {
      const saved = sessionStorage.getItem('chat_history');
      if (saved) {
        return JSON.parse(saved);
      }
    } catch (e) {
      console.error('Failed to parse chat history from sessionStorage', e);
    }
    return [];
  });

  const [isPending, setIsPending] = useState(false);
  const pendingRef = useRef(false);

  const updateMessages = (newMessages: ChatMessage[]) => {
    setMessages(newMessages);
    try {
      sessionStorage.setItem('chat_history', JSON.stringify(newMessages));
    } catch (e) {
      console.error('Failed to save chat history to sessionStorage', e);
    }
  };

  const sendMessage = async (content: string) => {
    if (!content.trim() || pendingRef.current) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: new Date().toISOString()
    };

    const newHistory = [...messages, userMessage];
    updateMessages(newHistory);
    
    setIsPending(true);
    pendingRef.current = true;

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: content,
          history: messages // Pass history specifically BEFORE adding the new message (as requested or implied by typical conversational structures, but the user requested history, I'll pass newHistory minus the latest if backend expects it, or just `newHistory`)
        })
      });

      if (!response.ok) {
        throw new Error('Chat API failed');
      }

      const data = await response.json();
      
      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.reply?.content || data.message || 'Errore nella risposta AI.',
        timestamp: new Date().toISOString()
      };
      
      updateMessages([...newHistory, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: '**Errore:** Connessione AI fallita.',
        timestamp: new Date().toISOString()
      };
      updateMessages([...newHistory, errorMessage]);
    } finally {
      setIsPending(false);
      pendingRef.current = false;
    }
  };

  return {
    messages,
    isPending,
    sendMessage,
    setMessages: updateMessages
  };
};