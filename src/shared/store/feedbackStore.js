import { create } from 'zustand';
import { persist, devtools } from 'zustand/middleware';

// Категории фидбеков
export const CATEGORIES = {
  UI: 'UI',
  PERFORMANCE: 'Performance',
  FEATURE: 'Feature',
  BUG: 'Bug',
};

// Начальное состояние
const initialState = {
  feedbacks: [],
  sortBy: 'newest',
  filterBy: 'all',
  selectedCategory: 'all',
  editingFeedback: null,
  isModalOpen: false,
};

// Функции для сортировки и фильтрации
const sortFeedbacks = (feedbacks, sortBy) => {
  const sorted = [...feedbacks];
  
  switch (sortBy) {
    case 'newest':
      return sorted.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    case 'oldest':
      return sorted.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
    case 'popular':
      return sorted.sort((a, b) => b.votes - a.votes);
    default:
      return sorted;
  }
};

const filterFeedbacks = (feedbacks, filterBy, selectedCategory) => {
  let filtered = feedbacks;

  // Фильтр по популярности
  if (filterBy === 'popular') {
    filtered = filtered.filter(f => f.votes > 5);
  }

  // Фильтр по категории
  if (selectedCategory !== 'all') {
    filtered = filtered.filter(f => f.category === selectedCategory);
  }

  return filtered;
};

export const useFeedbackStore = create(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,

        // Геттеры
        getProcessedFeedbacks: () => {
          const { feedbacks, sortBy, filterBy, selectedCategory } = get();
          const filtered = filterFeedbacks(feedbacks, filterBy, selectedCategory);
          return sortFeedbacks(filtered, sortBy);
        },

        getTotalCount: () => get().feedbacks.length,

        getStatistics: () => {
          const feedbacks = get().feedbacks;
          const now = new Date();
          const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

          const thisWeek = feedbacks.filter(f => 
            new Date(f.createdAt) >= weekAgo
          );

          const totalVotes = feedbacks.reduce((sum, f) => sum + f.votes, 0);
          const avgVotes = feedbacks.length > 0 ? totalVotes / feedbacks.length : 0;

          const categoryCounts = Object.values(CATEGORIES).reduce((acc, cat) => {
            acc[cat] = feedbacks.filter(f => f.category === cat).length;
            return acc;
          }, {});

          return {
            totalFeedbacks: feedbacks.length,
            thisWeekCount: thisWeek.length,
            totalVotes,
            avgVotes: Math.round(avgVotes * 10) / 10,
            categoryCounts,
          };
        },

        // Действия
        addFeedback: (feedback) => set((state) => ({
          feedbacks: [{
            ...feedback,
            id: Date.now(),
            votes: 0,
            createdAt: new Date().toISOString(),
            category: feedback.category || CATEGORIES.FEATURE,
          }, ...state.feedbacks],
        })),

        deleteFeedback: (id) => set((state) => ({
          feedbacks: state.feedbacks.filter(f => f.id !== id),
        })),

        updateFeedback: (id, updates) => set((state) => ({
          feedbacks: state.feedbacks.map(f =>
            f.id === id ? { ...f, ...updates } : f
          ),
        })),

        voteFeedback: (id, delta) => set((state) => ({
          feedbacks: state.feedbacks.map(f =>
            f.id === id ? { ...f, votes: Math.max(0, f.votes + delta) } : f
          ),
        })),

        setSortBy: (sortBy) => set({ sortBy }),

        setFilterBy: (filterBy) => set({ filterBy }),

        setSelectedCategory: (selectedCategory) => set({ selectedCategory }),

        // Модальное окно для редактирования
        openEditModal: (feedback) => set({
          editingFeedback: feedback,
          isModalOpen: true,
        }),

        closeEditModal: () => set({
          editingFeedback: null,
          isModalOpen: false,
        }),

        // Экспорт/импорт данных
        exportData: () => {
          const data = {
            feedbacks: get().feedbacks,
            exportedAt: new Date().toISOString(),
          };
          return JSON.stringify(data, null, 2);
        },

        importData: (jsonData) => {
          try {
            const data = JSON.parse(jsonData);
            if (data.feedbacks && Array.isArray(data.feedbacks)) {
              set({ feedbacks: data.feedbacks });
              return true;
            }
            return false;
          } catch {
            return false;
          }
        },

        // Очистка всех данных
        clearAllData: () => set(initialState),
      }),
      {
        name: 'feedback-storage',
        partialize: (state) => ({
          feedbacks: state.feedbacks,
          sortBy: state.sortBy,
          filterBy: state.filterBy,
          selectedCategory: state.selectedCategory,
        }),
      }
    ),
    {
      name: 'feedback-store',
    }
  )
); 