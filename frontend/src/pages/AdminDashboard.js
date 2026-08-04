import React, { useContext } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../App';
import { FiUsers, FiTrendingUp, FiBarChart2, FiBell, FiDownload, FiSettings, FiUserPlus, FiFileText, FiCpu } from 'react-icons/fi';

const AdminDashboard = () => {
  const { user } = useContext(AuthContext);

  const stats = [
    { icon: FiUsers, label: 'Total Students', value: '1,024', change: '+12 this month', color: 'bg-blue-500' },
    { icon: FiTrendingUp, label: 'Placed Students', value: '687', change: '67.1% placement rate', color: 'bg-green-500' },
    { icon: FiBarChart2, label: 'Model Accuracy', value: '94.2%', change: 'Best: Random Forest', color: 'bg-purple-500' },
    { icon: FiBell, label: 'Active Alerts', value: '23', change: '5 urgent', color: 'bg-orange-500' },
  ];

  const quickActions = [
    { label: 'Manage Students', desc: 'Add, edit, or remove students', link: '/admin/students', icon: FiUsers, color: 'from-blue-600 to-blue-400' },
    { label: 'View Analytics', desc: 'Placement trends and charts', link: '/admin/analytics', icon: FiBarChart2, color: 'from-purple-600 to-purple-400' },
    { label: 'Mentor Alerts', desc: 'Review and send alerts', link: '/admin/alerts', icon: FiBell, color: 'from-orange-600 to-orange-400' },
    { label: 'Train Model', desc: 'Retrain ML model', link: '/admin/dashboard', icon: FiCpu, color: 'from-green-600 to-green-400' },
  ];

  const placementData = [
    { dept: 'Computer Science', total: 180, placed: 153, rate: '85%' },
    { dept: 'Information Technology', total: 160, placed: 128, rate: '80%' },
    { dept: 'Electronics & Comm.', total: 150, placed: 105, rate: '70%' },
    { dept: 'Mechanical Engineering', total: 140, placed: 84, rate: '60%' },
    { dept: 'Civil Engineering', total: 120, placed: 60, rate: '50%' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Admin Dashboard</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Welcome back, {user?.username || 'Admin'} 👋</p>
        </div>
        <div className="flex gap-3">
          <button className="btn-secondary btn-sm"><FiDownload className="w-4 h-4 mr-1 inline" /> Export</button>
          <button className="btn-primary btn-sm"><FiSettings className="w-4 h-4 mr-1 inline" /> Settings</button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map(s => (
          <div key={s.label} className="card p-6 flex items-center gap-4 hover:shadow-lg transition-shadow">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${s.color}`}>
              <s.icon className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">{s.label}</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{s.value}</p>
              <p className="text-xs text-gray-400 mt-0.5">{s.change}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <div className="lg:col-span-2 space-y-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {quickActions.map(a => (
              <Link key={a.label} to={a.link}
                className={`card p-5 bg-gradient-to-br ${a.color} text-white hover:shadow-xl transition-all group`}>
                <a.icon className="w-8 h-8 mb-3 opacity-80" />
                <h3 className="font-semibold mb-1">{a.label}</h3>
                <p className="text-sm text-white/70">{a.desc}</p>
              </Link>
            ))}
          </div>

          {/* Department Placement */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Department-wise Placement</h2>
            <div className="space-y-4">
              {placementData.map(d => (
                <div key={d.dept}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-700 dark:text-gray-300">{d.dept}</span>
                    <span className="text-gray-500">{d.placed}/{d.total} ({d.rate})</span>
                  </div>
                  <div className="progress-bar">
                    <div className="progress-fill bg-gradient-to-r from-primary-500 to-accent-500"
                      style={{ width: d.rate }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Sidebar */}
        <div className="space-y-6">
          {/* System Status */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">System Status</h2>
            <div className="space-y-4">
              {[
                { label: 'ML Model', status: 'Active', color: 'text-accent-500' },
                { label: 'Database', status: 'Connected', color: 'text-accent-500' },
                { label: 'Email Service', status: 'Configured', color: 'text-yellow-500' },
                { label: 'API Server', status: 'Running', color: 'text-accent-500' },
              ].map(s => (
                <div key={s.label} className="flex justify-between text-sm">
                  <span className="text-gray-500">{s.label}</span>
                  <span className={`font-medium ${s.color}`}>● {s.status}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Alerts */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Alerts</h2>
            <div className="space-y-3">
              {[
                { name: 'Alice Smith', issue: 'Low CGPA (6.2)', time: '1 hour ago' },
                { name: 'Bob Jones', issue: 'Poor resume score', time: '3 hours ago' },
                { name: 'Carol Lee', issue: 'Low probability (28%)', time: '5 hours ago' },
              ].map((a, i) => (
                <div key={i} className="flex items-start gap-3 p-3 bg-red-50 dark:bg-red-900/10 rounded-xl">
                  <div className="w-2 h-2 bg-danger-500 rounded-full mt-2 flex-shrink-0" />
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">{a.name}</p>
                    <p className="text-xs text-gray-500">{a.issue} • {a.time}</p>
                  </div>
                </div>
              ))}
            </div>
            <Link to="/admin/alerts" className="btn-sm btn-secondary w-full mt-4 text-center">View All Alerts</Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
