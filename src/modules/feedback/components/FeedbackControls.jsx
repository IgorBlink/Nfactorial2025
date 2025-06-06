import { useFeedbackStore, CATEGORIES } from '../../../shared/store/feedbackStore';
import './FeedbackControls.css';

const FeedbackControls = () => {
  const { 
    sortBy, 
    filterBy, 
    selectedCategory,
    setSortBy, 
    setFilterBy, 
    setSelectedCategory,
    getTotalCount 
  } = useFeedbackStore();

  const totalCount = getTotalCount();

  return (
    <div className="feedback-controls">
      <div className="controls-header">
        <h3>Всего предложений: {totalCount}</h3>
      </div>
      
      <div className="controls-row">
        <div className="control-group">
          <label htmlFor="sort-select">Сортировка:</label>
          <select
            id="sort-select"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="newest">Сначала новые</option>
            <option value="oldest">Сначала старые</option>
            <option value="popular">По популярности</option>
          </select>
        </div>

        <div className="control-group">
          <label htmlFor="filter-select">Фильтр:</label>
          <select
            id="filter-select"
            value={filterBy}
            onChange={(e) => setFilterBy(e.target.value)}
          >
            <option value="all">Все предложения</option>
            <option value="popular">Популярные (&gt;5 голосов)</option>
          </select>
        </div>

        <div className="control-group">
          <label htmlFor="category-filter">Категория:</label>
          <select
            id="category-filter"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            <option value="all">Все категории</option>
            {Object.entries(CATEGORIES).map(([key, value]) => (
              <option key={key} value={value}>
                {value}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
};

export default FeedbackControls; 