import { useEffect } from 'react';
import { useThemeStore } from '../shared/store/themeStore';
import FeedbackForm from '../modules/feedback/components/FeedbackForm';
import FeedbackList from '../modules/feedback/components/FeedbackList';
import FeedbackControls from '../modules/feedback/components/FeedbackControls';
import FeedbackStats from '../modules/feedback/components/FeedbackStats';
import EditFeedbackModal from '../modules/feedback/components/EditFeedbackModal';
import ThemeToggle from '../shared/components/ThemeToggle';
import './App.css';

function App() {
  const { theme } = useThemeStore();

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  return (
    <div className="app">
      <ThemeToggle />
      
      <header className="app-header">
        <h1>Product Feedback Board</h1>
        <p>Поделитесь своими идеями по улучшению продукта</p>
      </header>
      
      <main className="app-main">
        <div className="app-grid">
          <div className="main-content">
            <FeedbackForm />
            <FeedbackControls />
            <FeedbackList />
          </div>
          
          <aside className="sidebar">
            <FeedbackStats />
          </aside>
        </div>
      </main>

      <EditFeedbackModal />
    </div>
  );
}

export default App;
