import React, { useState } from 'react';
import { FiSearch, FiCheckCircle, FiXCircle, FiAlertTriangle, FiHome, FiTrendingUp } from 'react-icons/fi';

const CompanyEligibility = () => {
  const [selectedCompany, setSelectedCompany] = useState(null);

  const companies = [
    { name: 'Google', cgpa: 8.5, backlogs: 0, match: 92, status: 'Eligible', color: 'text-accent-500' },
    { name: 'Microsoft', cgpa: 8.0, backlogs: 0, match: 88, status: 'Eligible', color: 'text-accent-500' },
    { name: 'Amazon', cgpa: 7.5, backlogs: 1, match: 85, status: 'Eligible', color: 'text-accent-500' },
    { name: 'Infosys', cgpa: 6.0, backlogs: 2, match: 95, status: 'Eligible', color: 'text-accent-500' },
    { name: 'TCS', cgpa: 5.5, backlogs: 3, match: 98, status: 'Eligible', color: 'text-accent-500' },
    { name: 'Goldman Sachs', cgpa: 7.5, backlogs: 1, match: 72, status: 'Partial', color: 'text-yellow-500' },
    { name: 'Meta', cgpa: 8.0, backlogs: 0, match: 65, status: 'Partial', color: 'text-yellow-500' },
    { name: 'Apple', cgpa: 8.5, backlogs: 0, match: 45, status: 'Not Eligible', color: 'text-danger-500' },
  ];

  const statusIcon = (status) => {
    if (status === 'Eligible') return <FiCheckCircle className="w-5 h-5 text-accent-500" />;
    if (status === 'Partial') return <FiAlertTriangle className="w-5 h-5 text-yellow-500" />;
    return <FiXCircle className="w-5 h-5 text-danger-500" />;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Company Eligibility</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Check your eligibility for top companies</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Company List */}
        <div className="lg:col-span-2">
          <div className="card overflow-hidden">
            <div className="p-4 border-b border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
              <div className="flex items-center gap-3">
                <FiSearch className="w-5 h-5 text-gray-400" />
                <input type="text" className="flex-1 bg-transparent border-none outline-none text-sm text-gray-700 dark:text-gray-300 placeholder-gray-400"
                  placeholder="Search companies..." />
              </div>
            </div>
            <div className="divide-y divide-gray-100 dark:divide-gray-700">
              {companies.map(c => (
                <div key={c.name}
                  className={`flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${selectedCompany?.name === c.name ? 'bg-primary-50 dark:bg-primary-900/20' : ''}`}
                  onClick={() => setSelectedCompany(c)}>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900/30 rounded-xl flex items-center justify-center">
                      <FiHome className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{c.name}</p>
                      <p className="text-xs text-gray-500">CGPA: {c.cgpa}+ • Backlogs: ≤{c.backlogs}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <p className="text-sm font-semibold">{c.match}%</p>
                      <p className={`text-xs ${c.color}`}>{c.status}</p>
                    </div>
                    {statusIcon(c.status)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Details Panel */}
        <div>
          {selectedCompany ? (
            <div className="card p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-xl flex items-center justify-center">
                  <FiHome className="w-6 h-6 text-primary-600" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-gray-900 dark:text-white">{selectedCompany.name}</h2>
                  <p className="text-sm text-gray-500">{selectedCompany.status}</p>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1"><span className="text-gray-500">Match Score</span><span className="font-semibold">{selectedCompany.match}%</span></div>
                  <div className="progress-bar"><div className="progress-fill bg-accent-500" style={{ width: `${selectedCompany.match}%` }} /></div>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between"><span className="text-gray-500">Min CGPA</span><span className="font-medium">{selectedCompany.cgpa}+</span></div>
                  <div className="flex justify-between"><span className="text-gray-500">Max Backlogs</span><span className="font-medium">{selectedCompany.backlogs}</span></div>
                  <div className="flex justify-between"><span className="text-gray-500">Required Skills</span><span className="font-medium">Python, DSA, SQL</span></div>
                </div>
              </div>
            </div>
          ) : (
            <div className="card p-8 text-center">
              <FiTrendingUp className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
              <p className="text-gray-500 text-sm">Select a company to view eligibility details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CompanyEligibility;
