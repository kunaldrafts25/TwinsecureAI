import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type Theme = 'light' | 'dark';

interface ThemeState {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  initTheme: () => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      theme: 'dark',
      setTheme: (theme) => set({ theme }),
      toggleTheme: () => set({ theme: get().theme === 'dark' ? 'light' : 'dark' }),
      initTheme: () => {
        const systemPreference = window.matchMedia('(prefers-color-scheme: dark)').matches
          ? 'dark'
          : 'light';
        
        // If no stored theme preference exists, use system preference
        if (!localStorage.getItem('theme-storage')) {
          set({ theme: systemPreference });
        }
      },
    }),
    {
      name: 'theme-storage',
    }
  )
);