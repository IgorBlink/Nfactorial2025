import { motion, AnimatePresence } from 'framer-motion';
import { useFeedbackStore } from '../../../shared/store/feedbackStore';
import FeedbackItem from './FeedbackItem';
import './FeedbackList.css';

const FeedbackList = () => {
  const { getProcessedFeedbacks } = useFeedbackStore();
  const feedbacks = getProcessedFeedbacks();

  if (feedbacks.length === 0) {
    return (
      <motion.div 
        className="feedback-list-empty"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <p>Пока нет предложений. Будьте первым!</p>
      </motion.div>
    );
  }

  return (
    <div className="feedback-list">
      <div className="feedback-items">
        <AnimatePresence mode="popLayout">
          {feedbacks.map((feedback) => (
            <motion.div
              key={feedback.id}
              layout
              initial={{ opacity: 0, scale: 0.8, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.8, x: -100 }}
              transition={{ 
                duration: 0.3,
                layout: { duration: 0.2 }
              }}
              whileHover={{ scale: 1.02 }}
            >
              <FeedbackItem feedback={feedback} />
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default FeedbackList; 