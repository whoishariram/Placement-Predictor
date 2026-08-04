import React, { useState } from 'react';
import { FiBell, FiSend, FiAlertCircle, FiCheckCircle, FiClock, FiUser } from 'react-icons/fi';
import toast from 'react-hot-toast';

const MentorAlerts = () => {
  const [sending, setSending] = useState(false);

  const alerts = [
    { name: 'Alice Johnson', id: 'STU1001', type: 'Low CGPA', detail: 'CGPA: 6.2 (below 7.0 threshold)', severity: 'High', time: '2 hours ago' },
    { name: 'Bob Smith', id: 'STU1002', type: 'Low Resume Score', detail: 'Resume Score: 35/100', severity: 'High', time: '3 hours ago' },
    { name: 'Carol Lee', id: 'STU1003', type: 'Low Probability', detail: 'Placement probability: 28%', severity: 'Medium', time: '5 hours ago' },
    { name: 'David Brown', id: 'STU1004', type: 'Low Programming', detail: 'Programming Skill: 38/100', severity: 'Medium', time: '1 day ago' },
    { name: 'Eve Davis', id: 'STU1005', type: 'Low Communication', detail: 'Communication: 42/100', severity: 'Low', time: '2 days ago' },
  ];

  const handleSendAlerts = async () => {
    setSending(true);
    await new Promise(r => setTimeout(r, 2000));
    toast.success('Alert emails sent to all mentors!');
    setSending(false);
  };

  const severityColor = { High: 'text-danger-600 bg-danger-50 dark:bg-danger-900/20', Medium: 'text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20', Low: 'text-blue-600 bg-blue-50 dark:bg-blue-900/20' };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Mentor Alerts</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Monitor at-risk students and send notifications to mentors</p>
        </div>
        <button onClick={handleSendAlerts} disabled={sending} className="btn-primary btn-sm">
          {sending ? <span className="flex items-center gap-2"><div className="spinner spinner-sm" /> Sending...</span>
            : <span className="flex items-center gap-2"><FiSend className="w-4 h-4" /> Send All Alerts</span>}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
        {[
          { label: 'Active Alerts', value: '23', icon: FiBell, color: 'text-orange-500 bg-orange-50 dark:bg-orange-900/20 border-orange-200' },
          { label: 'High Priority', value: '8', icon: FiAlertCircle, color: 'text-danger-500 bg-danger-50 dark:bg-danger-900/20 border-danger-200' },
          { label: 'Medium Priority', value: '10', icon: FiClock, color: 'text-yellow-500 bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200' },
          { label: 'Emails Sent', value: '142', icon: FiCheckCircle, color: 'text-accent-500 bg-accent-50 dark:bg-accent-900/20 border-accent-200' },
        ].map(s => (
          <div key={s.label} className={`card p-4 flex items-center gap-3 border-l-4 ${s.color.split(' ').pop()}`}>
            <s.icon className={`w-8 h-8 ${s.color.split(' ')[0]}`} />
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{s.value}</p>
              <p className="text-xs text-gray-500">{s.label}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="space-y-4">
        {alerts.map((a, i) => (
          <div key={i} className="card p-5 flex items-start gap-4 hover:shadow-lg transition-shadow">
            <div className="w-10 h-10 rounded-xl bg-gray-100 dark:bg-gray-700 flex items-center justify-center flex-shrink-0">
              <FiUser className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-1">
                <h3 className="font-semibold text-gray-900 dark:text-white">{a.name}</h3>
                <span className="text-xs text-gray-400">{a.id}</span>
                <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${severityColor[a.severity]}`}>{a.severity}</span>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400"><strong>{a.type}:</strong> {a.detail}</p>
              <p className="text-xs text-gray-400 mt-1">{a.time}</p>
            </div>
            <button className="btn-sm btn-secondary flex-shrink-0">Notify Mentor</button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MentorAlerts;
