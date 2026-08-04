import React, { useState, useContext, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../App';
import { FiTrendingUp, FiUser, FiBook, FiAward, FiBriefcase, FiFileText, FiArrowRight, FiCheckCircle, FiXCircle, FiAlertCircle } from 'react-icons/fi';

const StatCard = ({ icon: Icon, label, value, sub, color }) => (
  <div className="card p-6 flex items-center gap-4 hover:shadow-lg transition-shadow">
    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color}`}>
      <Icon className="w-6 h-6 text-white" />
    </div>
    <div>
      <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
      <p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
    </div>
  </div>
);

const StudentDashboard = () => {
  const { user } = useContext(AuthContext);
  const [prediction, setPrediction] = useState(null);

  const stats = [
    { icon: FiUser, label: 'CGPA', value: user?.cgpa || '8.2', sub: 'out of 10', color: 'bg-blue-500' },
    { icon: FiBook, label: 'Attendance', value: '92%', sub: 'This semester', color: 'bg-green-500' },
    { icon: FiAward, label: 'Projects', value: '4', sub: 'Completed', color: 'bg-purple-500' },
    { icon: FiBriefcase, label: 'Internships', value: '2', sub: 'Industry experience', color: 'bg-orange-500' },
  ];

  const quickActions = [
    { label: 'Get Prediction', desc: 'Predict your placement chances', link: '/student/predict', color: 'from-primary-600 to-primary-400' },
    { label: 'Check Eligibility', desc: 'View eligible companies', link: '/student/eligibility', color: 'from-accent-500 to-accent-400' },
    { label: 'Upload Resume', desc: 'Analyze your resume', link: '/student/resume', color: 'from-purple-600 to-purple-400' },
  ];

  const recentActivity = [
    { action: 'Profile Updated', time: '2 hours ago', icon: FiUser, color: 'text-blue-500' },
    { action: 'Resume Uploaded', time: '1 day ago', icon: FiFileText, color: 'text-purple-500' },
    { action: 'Prediction Generated', time: '3 days ago', icon: FiTrendingUp, color: 'text-green-500' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Welcome */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Welcome back, {user?.name || 'Student'}! 👋
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Here's your placement overview</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map(s => <StatCard key={s.label} {...s} />)}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {quickActions.map(a => (
              <Link key={a.label} to={a.link}
                className={`card-hover p-5 bg-gradient-to-br ${a.color} text-white`}>
                <h3 className="font-semibold mb-1">{a.label}</h3>
                <p className="text-sm text-white/80">{a.desc}</p>
                <FiArrowRight className="mt-3 group-hover:translate-x-1 transition-transform" />
              </Link>
            ))}
          </div>

          {/* Prediction Result */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Latest Prediction</h2>
            <div className="flex items-center justify-between p-4 bg-accent-50 dark:bg-accent-900/20 rounded-xl">
              <div className="flex items-center gap-3">
                {true ? <FiCheckCircle className="w-8 h-8 text-accent-500" /> : <FiXCircle className="w-8 h-8 text-danger-500" />}
                <div>
                  <p className="font-semibold text-gray-900 dark:text-white">High Chance of Placement 🎉</p>
                  <p className="text-sm text-gray-500">Probability: 87.5%</p>
                </div>
              </div>
              <Link to="/student/predict" className="btn-sm btn-secondary">View Details</Link>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Profile Card */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Profile</h2>
            <div className="space-y-3">
              <div className="flex justify-between text-sm"><span className="text-gray-500">Name</span><span className="font-medium text-gray-900 dark:text-white truncate ml-2">{user?.name}</span></div>
              <div className="flex justify-between text-sm"><span className="text-gray-500">ID</span><span className="font-medium">{user?.student_id}</span></div>
              <div className="flex justify-between text-sm"><span className="text-gray-500">Department</span><span className="font-medium">{user?.department}</span></div>
              <div className="flex justify-between text-sm"><span className="text-gray-500">Year</span><span className="font-medium">{user?.year}th Year</span></div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Activity</h2>
            <div className="space-y-4">
              {recentActivity.map((a, i) => (
                <div key={i} className="flex items-center gap-3">
                  <a.icon className={`w-4 h-4 ${a.color}`} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-700 dark:text-gray-300 truncate">{a.action}</p>
                    <p className="text-xs text-gray-400">{a.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Alerts */}
          <div className="card p-6 border-l-4 border-yellow-400">
            <div className="flex items-start gap-3">
              <FiAlertCircle className="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white text-sm">Upcoming Deadline</h3>
                <p className="text-xs text-gray-500 mt-1">Company registrations closing soon. Check eligibility now!</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;
