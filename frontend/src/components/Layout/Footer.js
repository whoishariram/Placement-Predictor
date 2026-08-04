import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
  return (
    <footer className="bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <Link to="/" className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-primary-600 to-accent-500 rounded-lg flex items-center justify-center text-white font-bold">
                P
              </div>
              <span className="text-lg font-bold text-gray-900 dark:text-white">Placement Predictor</span>
            </Link>
            <p className="text-sm text-gray-500 dark:text-gray-400 max-w-md">
              An intelligent placement prediction system powered by Machine Learning to help students and colleges achieve better placement outcomes.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider mb-4">
              Quick Links
            </h3>
            <ul className="space-y-2">
              <li><Link to="/" className="text-sm text-gray-500 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400">Home</Link></li>
              <li><Link to="/login" className="text-sm text-gray-500 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400">Student Login</Link></li>
              <li><Link to="/register" className="text-sm text-gray-500 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400">Register</Link></li>
              <li><Link to="/admin/login" className="text-sm text-gray-500 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400">Admin Login</Link></li>
            </ul>
          </div>

          {/* Features */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider mb-4">
              Features
            </h3>
            <ul className="space-y-2">
              <li><span className="text-sm text-gray-500 dark:text-gray-400">Placement Prediction</span></li>
              <li><span className="text-sm text-gray-500 dark:text-gray-400">Resume Analysis</span></li>
              <li><span className="text-sm text-gray-500 dark:text-gray-400">Company Eligibility</span></li>
              <li><span className="text-sm text-gray-500 dark:text-gray-400">Mentor Alerts</span></li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-gray-200 dark:border-gray-800">
          <p className="text-center text-sm text-gray-400 dark:text-gray-600">
            &copy; {new Date().getFullYear()} Placement Predictor using Machine Learning. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
