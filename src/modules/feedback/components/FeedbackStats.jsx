import { motion } from 'framer-motion';
import { useFeedbackStore } from '../../../shared/store/feedbackStore';
import './FeedbackStats.css';

const FeedbackStats = () => {
  const { getStatistics } = useFeedbackStore();
  const stats = getStatistics();

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <motion.div 
      className="feedback-stats"
      initial="hidden"
      animate="visible"
      variants={containerVariants}
    >
      <motion.h3 variants={itemVariants}>📊 Статистика</motion.h3>
      
      <motion.div 
        className="stats-grid"
        variants={containerVariants}
      >
        <motion.div className="stat-card" variants={itemVariants}>
          <motion.div 
            className="stat-value"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
          >
            {stats.totalFeedbacks}
          </motion.div>
          <div className="stat-label">Всего предложений</div>
        </motion.div>
        
        <motion.div className="stat-card" variants={itemVariants}>
          <motion.div 
            className="stat-value"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.3, type: "spring", stiffness: 200 }}
          >
            {stats.thisWeekCount}
          </motion.div>
          <div className="stat-label">За эту неделю</div>
        </motion.div>
        
        <motion.div className="stat-card" variants={itemVariants}>
          <motion.div 
            className="stat-value"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.4, type: "spring", stiffness: 200 }}
          >
            {stats.totalVotes}
          </motion.div>
          <div className="stat-label">Всего голосов</div>
        </motion.div>
        
        <motion.div className="stat-card" variants={itemVariants}>
          <motion.div 
            className="stat-value"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.5, type: "spring", stiffness: 200 }}
          >
            {stats.avgVotes}
          </motion.div>
          <div className="stat-label">Среднее голосов</div>
        </motion.div>
      </motion.div>

      <motion.div className="category-stats" variants={itemVariants}>
        <h4>По категориям:</h4>
        <motion.div 
          className="category-list"
          variants={containerVariants}
        >
          {Object.entries(stats.categoryCounts).map(([category, count], index) => (
            <motion.div 
              key={category} 
              className="category-item"
              variants={itemVariants}
              whileHover={{ scale: 1.02, x: 5 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <span className="category-name">{category}</span>
              <motion.span 
                className="category-count"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.6 + index * 0.1, type: "spring", stiffness: 200 }}
              >
                {count}
              </motion.span>
            </motion.div>
          ))}
        </motion.div>
      </motion.div>
    </motion.div>
  );
};

export default FeedbackStats; 