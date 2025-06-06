import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useFeedbackStore, CATEGORIES } from '../../../shared/store/feedbackStore';
import './EditFeedbackModal.css';

const EditFeedbackModal = () => {
  const { 
    editingFeedback, 
    isModalOpen, 
    closeEditModal, 
    updateFeedback 
  } = useFeedbackStore();

  const [text, setText] = useState('');
  const [category, setCategory] = useState(CATEGORIES.FEATURE);

  useEffect(() => {
    if (editingFeedback) {
      setText(editingFeedback.text);
      setCategory(editingFeedback.category || CATEGORIES.FEATURE);
    }
  }, [editingFeedback]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (text.trim() && editingFeedback) {
      updateFeedback(editingFeedback.id, {
        text: text.trim(),
        category,
        updatedAt: new Date().toISOString(),
      });
      closeEditModal();
    }
  };

  const handleClose = () => {
    closeEditModal();
  };

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      handleClose();
    }
  };

  return (
    <AnimatePresence>
      {isModalOpen && editingFeedback && (
        <motion.div 
          className="modal-backdrop" 
          onClick={handleBackdropClick}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
        >
          <motion.div 
            className="modal-content"
            initial={{ opacity: 0, scale: 0.8, y: 50 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 50 }}
            transition={{ duration: 0.3, type: "spring", damping: 25, stiffness: 300 }}
          >
            <div className="modal-header">
              <h2>Редактировать предложение</h2>
              <motion.button 
                className="modal-close"
                onClick={handleClose}
                type="button"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                ✕
              </motion.button>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="edit-text">Текст предложения:</label>
                <textarea
                  id="edit-text"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  rows={4}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="edit-category">Категория:</label>
                <select
                  id="edit-category"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                >
                  {Object.entries(CATEGORIES).map(([key, value]) => (
                    <option key={key} value={value}>
                      {value}
                    </option>
                  ))}
                </select>
              </div>

              <div className="modal-actions">
                <motion.button 
                  type="button" 
                  className="btn-secondary"
                  onClick={handleClose}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Отмена
                </motion.button>
                <motion.button 
                  type="submit" 
                  className="btn-primary"
                  disabled={!text.trim()}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Сохранить
                </motion.button>
              </div>
            </form>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default EditFeedbackModal; 