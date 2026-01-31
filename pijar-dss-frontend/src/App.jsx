/**
 * Main Application Component
 */

import React, { useState } from 'react';
import { Navbar } from './components/common/Navbar';
import { HomePage } from './components/home/Homepage';
import { GuidePage } from './components/home/GuidePage';
import { DashboardPage } from './components/dashboard/DashboardPage';
import './styles/index.css';

function App() {
  const [currentPage, setCurrentPage] = useState('home');

  const renderPage = () => {
    switch (currentPage) {
      case 'home':
        return <HomePage onNavigate={setCurrentPage} />;
      case 'guide':
        return <GuidePage onNavigate={setCurrentPage} />;
      case 'dashboard':
        return <DashboardPage />;
      default:
        return <HomePage onNavigate={setCurrentPage} />;
    }
  };

  return (
    <div>
      <Navbar currentPage={currentPage} onNavigate={setCurrentPage} />
      {renderPage()}
    </div>
  );
}

export default App;