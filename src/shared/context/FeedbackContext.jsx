import { createContext, useContext, useReducer } from 'react';

// Типы действий
const ACTIONS = {
  ADD_FEEDBACK: 'ADD_FEEDBACK',
  DELETE_FEEDBACK: 'DELETE_FEEDBACK',
  VOTE_FEEDBACK: 'VOTE_FEEDBACK',
  SET_SORT: 'SET_SORT',
  SET_FILTER: 'SET_FILTER',
};

// Начальное состояние
const initialState = {
  feedbacks: [],
  sortBy: 'newest', // newest, oldest, popular
  filterBy: 'all', // all, popular (votes > 5)
};

// Reducer
const feedbackReducer = (state, action) => {
  switch (action.type) {
    case ACTIONS.ADD_FEEDBACK:
      return {
        ...state,
        feedbacks: [action.payload, ...state.feedbacks],
      };

    case ACTIONS.DELETE_FEEDBACK:
      return {
        ...state,
        feedbacks: state.feedbacks.filter(f => f.id !== action.payload),
      };

    case ACTIONS.VOTE_FEEDBACK:
      return {
        ...state,
        feedbacks: state.feedbacks.map(f =>
          f.id === action.payload.id
            ? { ...f, votes: f.votes + action.payload.delta }
            : f
        ),
      };

    case ACTIONS.SET_SORT:
      return {
        ...state,
        sortBy: action.payload,
      };

    case ACTIONS.SET_FILTER:
      return {
        ...state,
        filterBy: action.payload,
      };

    default:
      return state;
  }
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

const filterFeedbacks = (feedbacks, filterBy) => {
  switch (filterBy) {
    case 'popular':
      return feedbacks.filter(f => f.votes > 5);
    case 'all':
    default:
      return feedbacks;
  }
};

// Context
const FeedbackContext = createContext();

// Provider
export const FeedbackProvider = ({ children }) => {
  const [state, dispatch] = useReducer(feedbackReducer, initialState);

  // Получение отфильтрованных и отсортированных фидбеков
  const getProcessedFeedbacks = () => {
    const filtered = filterFeedbacks(state.feedbacks, state.filterBy);
    return sortFeedbacks(filtered, state.sortBy);
  };

  // Действия
  const addFeedback = (feedback) => {
    dispatch({
      type: ACTIONS.ADD_FEEDBACK,
      payload: {
        ...feedback,
        id: Date.now(),
        votes: 0,
        createdAt: new Date().toISOString(),
      },
    });
  };

  const deleteFeedback = (id) => {
    dispatch({
      type: ACTIONS.DELETE_FEEDBACK,
      payload: id,
    });
  };

  const voteFeedback = (id, delta) => {
    dispatch({
      type: ACTIONS.VOTE_FEEDBACK,
      payload: { id, delta },
    });
  };

  const setSortBy = (sortBy) => {
    dispatch({
      type: ACTIONS.SET_SORT,
      payload: sortBy,
    });
  };

  const setFilterBy = (filterBy) => {
    dispatch({
      type: ACTIONS.SET_FILTER,
      payload: filterBy,
    });
  };

  const value = {
    feedbacks: getProcessedFeedbacks(),
    totalCount: state.feedbacks.length,
    sortBy: state.sortBy,
    filterBy: state.filterBy,
    addFeedback,
    deleteFeedback,
    voteFeedback,
    setSortBy,
    setFilterBy,
  };

  return (
    <FeedbackContext.Provider value={value}>
      {children}
    </FeedbackContext.Provider>
  );
};

// Hook для использования контекста
export const useFeedback = () => {
  const context = useContext(FeedbackContext);
  if (!context) {
    throw new Error('useFeedback must be used within FeedbackProvider');
  }
  return context;
}; 