import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import { QueryProvider } from './shared/providers/QueryProvider';
import { EnhancedApp } from './app/EnhancedApp';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <QueryProvider>
      <EnhancedApp />
    </QueryProvider>
  </React.StrictMode>
); 