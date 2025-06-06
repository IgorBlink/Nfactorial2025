import { useState } from 'react';
import { useFeedbackStore, CATEGORIES } from '../../../shared/store/feedbackStore';
import './FeedbackForm.css';

const FeedbackForm = () => {
  const [text, setText] = useState('');
  const [category, setCategory] = useState(CATEGORIES.FEATURE);
  const { addFeedback } = useFeedbackStore();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (text.trim()) {
      addFeedback({
        text: text.trim(),
        category,
      });
      setText('');
      setCategory(CATEGORIES.FEATURE);
    }
  };

  const categoryOptions = [
    { value: CATEGORIES.FEATURE, label: '✨ Feature', color: '#8b5cf6' },
    { value: CATEGORIES.UI, label: '🎨 UI', color: '#3b82f6' },
    { value: CATEGORIES.PERFORMANCE, label: '⚡ Performance', color: '#10b981' },
    { value: CATEGORIES.BUG, label: '🐛 Bug', color: '#ef4444' },
  ];

  return (
    <div className="feedback-form">
      <div className="form-header">
        <h2>💡 Добавить предложение</h2>
        <p>Поделитесь своей идеей по улучшению продукта</p>
      </div>
      
      <form onSubmit={handleSubmit} className="form-content">
        <div className="form-group">
          <label htmlFor="category-select" className="form-label">
            Категория
          </label>
          <div className="select-wrapper">
            <select
              id="category-select"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="form-select"
            >
              {categoryOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="feedback-text" className="form-label">
            Ваше предложение
          </label>
          <textarea
            id="feedback-text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Опишите ваше предложение по улучшению продукта..."
            className="form-textarea"
            rows={4}
            required
          />
        </div>
        
        <button 
          type="submit" 
          disabled={!text.trim()} 
          className="submit-button"
        >
          <span>🚀</span>
          Добавить предложение
        </button>
      </form>
    </div>
  );
};

export default FeedbackForm; 