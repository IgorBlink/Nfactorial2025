import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useThemeStore = create(
  persist(
    (set, get) => ({
      theme: 'light', // 'light' | 'dark'
      
      toggleTheme: () => set((state) => ({
        theme: state.theme === 'light' ? 'dark' : 'light',
      })),
      
      setTheme: (theme) => set({ theme }),
      
      isDark: () => get().theme === 'dark',
    }),
    {
      name: 'theme-storage',
    }
  )
); 