import { useState, useRef } from 'react';
import { useFeedbackStore } from '../../../shared/store/feedbackStore';
import './DataManager.css';

const DataManager = () => {
  const { exportData, importData, clearAllData } = useFeedbackStore();
  const [importStatus, setImportStatus] = useState('');
  const fileInputRef = useRef(null);

  const handleExport = () => {
    const data = exportData();
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `feedback-data-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleImportClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const jsonData = event.target?.result;
        const success = importData(jsonData);
        
        if (success) {
          setImportStatus('✅ Данные успешно импортированы!');
        } else {
          setImportStatus('❌ Ошибка: неверный формат файла');
        }
      } catch (error) {
        setImportStatus('❌ Ошибка при чтении файла');
      }
      
      // Очистить статус через 3 секунды
      setTimeout(() => setImportStatus(''), 3000);
    };
    
    reader.readAsText(file);
    e.target.value = ''; // Сбросить input
  };

  const handleClearData = () => {
    if (window.confirm('Вы уверены, что хотите удалить все данные? Это действие нельзя отменить.')) {
      clearAllData();
      setImportStatus('🗑️ Все данные удалены');
      setTimeout(() => setImportStatus(''), 3000);
    }
  };

  return (
    <div className="data-manager">
      <h3>🔧 Управление данными</h3>
      
      <div className="data-actions">
        <button 
          className="btn-export"
          onClick={handleExport}
          title="Скачать данные в формате JSON"
        >
          📥 Экспорт данных
        </button>
        
        <button 
          className="btn-import"
          onClick={handleImportClick}
          title="Загрузить данные из JSON файла"
        >
          📤 Импорт данных
        </button>
        
        <button 
          className="btn-clear"
          onClick={handleClearData}
          title="Удалить все данные"
        >
          🗑️ Очистить все
        </button>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".json"
        onChange={handleFileChange}
        style={{ display: 'none' }}
      />

      {importStatus && (
        <div className="import-status">
          {importStatus}
        </div>
      )}
    </div>
  );
};

export default DataManager; 