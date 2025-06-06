import { useFeedbackStore } from '../../../shared/store/feedbackStore';
import './FeedbackItem.css';

const FeedbackItem = ({ feedback }) => {
  const { deleteFeedback, voteFeedback, openEditModal } = useFeedbackStore();

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const handleVote = (delta) => {
    voteFeedback(feedback.id, delta);
  };

  const getCategoryColor = (category) => {
    const colors = {
      'UI': '#3b82f6',
      'Performance': '#10b981',
      'Feature': '#8b5cf6',
      'Bug': '#ef4444',
    };
    return colors[category] || '#6b7280';
  };

  return (
    <div className="feedback-item">
      <div className="feedback-content">
        <div className="feedback-header">
          <span 
            className="feedback-category"
            style={{ backgroundColor: getCategoryColor(feedback.category) }}
          >
            {feedback.category}
          </span>
          {feedback.updatedAt && (
            <span className="feedback-updated" title="Отредактировано">
              ✏️
            </span>
          )}
        </div>
        
        <p className="feedback-text">{feedback.text}</p>
        
        <div className="feedback-meta">
          <span className="feedback-date">
            {formatDate(feedback.createdAt)}
          </span>
          <div className="feedback-voting">
            <button 
              className="vote-button vote-up"
              onClick={() => handleVote(1)}
              title="Поддержать идею"
            >
              👍
            </button>
            <span className="feedback-votes">
              {feedback.votes}
            </span>
            <button 
              className="vote-button vote-down"
              onClick={() => handleVote(-1)}
              title="Не поддержать идею"
              disabled={feedback.votes <= 0}
            >
              👎
            </button>
          </div>
        </div>
      </div>
      
      <div className="feedback-actions">
        <button 
          className="edit-button"
          onClick={() => openEditModal(feedback)}
          title="Редактировать предложение"
        >
          ✏️
        </button>
        <button 
          className="delete-button"
          onClick={() => deleteFeedback(feedback.id)}
          title="Удалить предложение"
        >
          ✕
        </button>
      </div>
    </div>
  );
};

export default FeedbackItem; 