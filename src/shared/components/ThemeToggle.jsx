import { useThemeStore } from '../store/themeStore';
import './ThemeToggle.css';

const ThemeToggle = () => {
  const { theme, toggleTheme } = useThemeStore();

  return (
    <button 
      className="theme-toggle"
      onClick={toggleTheme}
      title={`Переключить на ${theme === 'light' ? 'темную' : 'светлую'} тему`}
    >
      {theme === 'light' ? '🌙' : '☀️'}
    </button>
  );
};

export default ThemeToggle; 