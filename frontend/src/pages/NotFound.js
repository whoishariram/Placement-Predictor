import React from 'react';
import { Link } from 'react-router-dom';
import { FiHome, FiArrowLeft } from 'react-icons/fi';

const NotFound = () => (
  <div className="min-h-[70vh] flex items-center justify-center px-4">
    <div className="text-center max-w-md">
      <div className="text-8xl font-extrabold gradient-text mb-4">404</div>
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Page Not Found</h1>
      <p className="text-gray-500 dark:text-gray-400 mb-8">The page you're looking for doesn't exist or has been moved.</p>
      <div className="flex items-center justify-center gap-4">
        <Link to="/" className="btn-primary"><FiHome className="w-4 h-4 mr-2 inline" />Go Home</Link>
        <button onClick={() => window.history.back()} className="btn-secondary"><FiArrowLeft className="w-4 h-4 mr-2 inline" />Go Back</button>
      </div>
    </div>
  </div>
);

export default NotFound;
