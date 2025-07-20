import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

// Cognitio Chat Framework Store
interface ChatState {
  messages: Array<{
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: number;
  }>;
  isLoading: boolean;
  model: string;
  temperature: number;
  
  // Actions
  addMessage: (message: { role: 'user' | 'assistant'; content: string }) => void;
  clearMessages: () => void;
  setLoading: (loading: boolean) => void;
  setModel: (model: string) => void;
  setTemperature: (temp: number) => void;
}

export const useChatStore = create<ChatState>()(
  devtools(
    (set) => ({
      messages: [],
      isLoading: false,
      model: 'Llama-3.2-3B-Instruct-q4f32_1-MLC',
      temperature: 0.7,
      
      addMessage: (message) => set((state) => ({
        messages: [...state.messages, {
          id: Date.now().toString(),
          ...message,
          timestamp: Date.now()
        }]
      })),
      
      clearMessages: () => set({ messages: [] }),
      setLoading: (loading) => set({ isLoading: loading }),
      setModel: (model) => set({ model }),
      setTemperature: (temp) => set({ temperature: temp })
    }),
    {
      name: 'webllm-chat-store'
    }
  )
);
