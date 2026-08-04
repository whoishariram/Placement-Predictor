import React from 'react';
import { FiBarChart2, FiPieChart, FiTrendingUp, FiDownload, FiAward } from 'react-icons/fi';
import ChartCard from '../components/Charts/ChartCard';
import {
  BarChart,
  HorizontalBarChart,
  DoughnutChart,
  LineChart,
} from '../components/Charts/Charts';
import toast from 'react-hot-toast';

const Analytics = () => {
  // ============================================
  // MOCK DATA (replace with API calls later)
  // ============================================

  const departmentLabels = ['CSE', 'IT', 'ECE', 'ME', 'CE', 'AI&ML', 'DS'];
  const departmentPlaced = [153, 128, 105, 84, 60, 95, 72];
  const departmentTotal = [180, 160, 150, 140, 120, 110, 90];

  const cgpaLabels = ['9-10', '8-9', '7-8', '6-7', '5-6', '<5'];
  const cgpaData = [102, 256, 308, 205, 102, 51];

  const trendLabels = ['2019', '2020', '2021', '2022', '2023', '2024'];
  const trendRates = [68, 72, 68, 75, 82, 87];
  const trendStudents = [580, 620, 590, 650, 720, 780];

  const companyLabels = ['TCS', 'Infosys', 'Accenture', 'Wipro', 'Google', 'Amazon', 'Microsoft', 'Deloitte'];
  const companyHires = [150, 120, 85, 65, 45, 38, 35, 30];

  const placementSummary = [
    ['Computer Science', 180, 153, 27, '85%', '₹12.5 LPA'],
    ['Information Technology', 160, 128, 32, '80%', '₹10.2 LPA'],
    ['Electronics & Comm.', 150, 105, 45, '70%', '₹8.8 LPA'],
    ['Mechanical Engineering', 140, 84, 56, '60%', '₹6.5 LPA'],
    ['Civil Engineering', 120, 60, 60, '50%', '₹5.2 LPA'],
    ['AI & Machine Learning', 110, 95, 15, '86%', '₹14.0 LPA'],
    ['Data Science', 90, 72, 18, '80%', '₹11.5 LPA'],
  ];

  const handleExport = () => {
    toast.success('Report download started');
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-8 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Analytics Dashboard</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Comprehensive placement analytics and insights</p>
        </div>
        <div className="flex gap-3">
          <button onClick={handleExport} className="btn-secondary btn-sm">
            <FiDownload className="w-4 h-4 mr-1 inline" /> Export Report
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Total Students', value: '950', change: '+45 this year', color: 'from-blue-500 to-blue-400', icon: FiBarChart2 },
          { label: 'Overall Placement', value: '67.1%', change: '+5.2% vs last year', color: 'from-green-500 to-green-400', icon: FiTrendingUp },
          { label: 'Avg Package', value: '₹9.8 LPA', change: '+₹1.2 LPA', color: 'from-purple-500 to-purple-400', icon: FiAward },
          { label: 'Active Companies', value: '15', change: '3 new this year', color: 'from-orange-500 to-orange-400', icon: FiPieChart },
        ].map((stat, i) => (
          <div key={i} className="card p-5 flex items-center gap-4 hover:shadow-lg transition-shadow">
            <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${stat.color} flex items-center justify-center shadow-sm`}>
              <stat.icon className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 font-medium uppercase tracking-wider">{stat.label}</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stat.value}</p>
              <p className="text-xs text-gray-400 mt-0.5">{stat.change}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Department-wise Placement */}
        <ChartCard title="Department-wise Placement" icon={FiBarChart2} gradient="from-primary-500 to-primary-400" downloadable>
          <BarChart
            labels={departmentLabels}
            datasets={[
              { label: 'Placed', data: departmentPlaced, backgroundColor: '#3b82f6' },
              { label: 'Total', data: departmentTotal, backgroundColor: '#93c5fd' },
            ]}
            height={300}
          />
        </ChartCard>

        {/* CGPA Distribution */}
        <ChartCard title="CGPA Distribution" icon={FiPieChart} gradient="from-accent-500 to-accent-400" downloadable>
          <DoughnutChart
            labels={cgpaLabels}
            data={cgpaData}
            height={300}
          />
        </ChartCard>

        {/* Placement Trend */}
        <ChartCard title="Placement Trend" icon={FiTrendingUp} gradient="from-purple-500 to-purple-400" downloadable>
          <LineChart
            labels={trendLabels}
            datasets={[
              {
                label: 'Placement Rate (%)',
                data: trendRates,
                borderColor: '#9333ea',
                backgroundColor: 'rgba(147, 51, 234, 0.1)',
                fill: true,
              },
              {
                label: 'Total Students Placed',
                data: trendStudents,
                borderColor: '#14b8a6',
                backgroundColor: 'rgba(20, 184, 166, 0.1)',
                fill: true,
                yAxisID: 'y1',
              },
            ]}
            height={300}
          />
        </ChartCard>

        {/* Company-wise Hires */}
        <ChartCard title="Company-wise Hires" icon={FiBarChart2} gradient="from-orange-500 to-orange-400" downloadable>
          <HorizontalBarChart
            labels={companyLabels}
            datasets={[
              {
                label: 'Students Hired',
                data: companyHires,
                backgroundColor: [
                  '#3b82f6', '#22c55e', '#f97316', '#9333ea',
                  '#ef4444', '#14b8a6', '#eab308', '#ec4899',
                ],
              },
            ]}
            height={300}
          />
        </ChartCard>

        {/* Placement Rate by Department */}
        <ChartCard title="Placement Rate by Department" icon={FiBarChart2} gradient="from-pink-500 to-pink-400" downloadable>
          <BarChart
            labels={departmentLabels}
            datasets={[
              {
                label: 'Placement Rate (%)',
                data: departmentLabels.map((_, i) => Math.round((departmentPlaced[i] / departmentTotal[i]) * 100)),
                backgroundColor: departmentLabels.map(() => '#ec4899'),
              },
            ]}
            height={300}
          />
        </ChartCard>

        {/* Skills Distribution */}
        <ChartCard title="Top Skills in Demand" icon={FiPieChart} gradient="from-cyan-500 to-cyan-400" downloadable>
          <DoughnutChart
            labels={['Python', 'Java', 'SQL', 'React', 'Machine Learning', 'AWS']}
            data={[85, 72, 68, 55, 48, 42]}
            height={300}
          />
        </ChartCard>

        {/* Summary Table */}
        <div className="lg:col-span-2 card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Placement Summary</h2>
            <span className="text-xs text-gray-400">Academic Year 2023-24</span>
          </div>
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Department</th>
                  <th>Total</th>
                  <th>Placed</th>
                  <th>Not Placed</th>
                  <th>Rate</th>
                  <th>Avg Package</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {placementSummary.map((row, i) => {
                  const rate = parseInt(row[4]);
                  return (
                    <tr key={i}>
                      <td className="font-medium">{row[0]}</td>
                      <td>{row[1]}</td>
                      <td className="text-accent-600 font-medium">{row[2]}</td>
                      <td className="text-danger-500">{row[3]}</td>
                      <td>
                        <div className="flex items-center gap-2">
                          <span className="font-semibold">{row[4]}</span>
                          <div className="flex-1 max-w-[60px]">
                            <div className="progress-bar">
                              <div
                                className={`progress-fill ${
                                  rate >= 80 ? 'bg-accent-500' : rate >= 60 ? 'bg-yellow-500' : 'bg-danger-500'
                                }`}
                                style={{ width: `${rate}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="font-medium">{row[5]}</td>
                      <td>
                        <span className={`badge ${
                          rate >= 80 ? 'badge-success' : rate >= 60 ? 'badge-warning' : 'badge-danger'
                        }`}>
                          {rate >= 80 ? 'Excellent' : rate >= 60 ? 'Good' : 'Needs Work'}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
