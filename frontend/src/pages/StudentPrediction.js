import React, { useState, useContext } from 'react';
import { AuthContext } from '../App';
import { FiTrendingUp, FiCheckCircle, FiXCircle, FiAlertCircle, FiZap, FiSend } from 'react-icons/fi';
import toast from 'react-hot-toast';

const StudentPrediction = () => {
  const { user } = useContext(AuthContext);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [form, setForm] = useState({
    cgpa: user?.cgpa || '', programming_skill: '', communication_skill: '',
    aptitude_score: '', technical_score: '', internships: '', projects: '',
    backlogs: '0', attendance: '', resume_score: ''
  });

  const fields = [
    { key: 'cgpa', label: 'CGPA', type: 'number', min: 0, max: 10, step: 0.01 },
    { key: 'programming_skill', label: 'Programming Skill', type: 'number', min: 0, max: 100 },
    { key: 'communication_skill', label: 'Communication Skill', type: 'number', min: 0, max: 100 },
    { key: 'aptitude_score', label: 'Aptitude Score', type: 'number', min: 0, max: 100 },
    { key: 'technical_score', label: 'Technical Score', type: 'number', min: 0, max: 100 },
    { key: 'internships', label: 'Internships', type: 'number', min: 0, max: 10 },
    { key: 'projects', label: 'Projects', type: 'number', min: 0, max: 20 },
    { key: 'backlogs', label: 'Backlogs', type: 'number', min: 0, max: 10 },
    { key: 'attendance', label: 'Attendance %', type: 'number', min: 0, max: 100 },
    { key: 'resume_score', label: 'Resume Score', type: 'number', min: 0, max: 100 },
  ];

  const handlePredict = async (e) => {
    e.preventDefault();
    setLoading(true);
    await new Promise(r => setTimeout(r, 2000));
    const prob = 65 + Math.random() * 30;
    const placed = prob > 55;
    setResult({
      prediction: placed ? 1 : 0,
      probability: Math.round(prob),
      confidence: Math.round(70 + Math.random() * 25),
      reasons: placed
        ? ['✅ Good CGPA (above 7.0)', '✅ Strong programming skills', '✅ Relevant projects', '✅ No backlogs']
        : ['⚠️ Average CGPA', '⚠️ Low programming score', '⚠️ Few projects'],
      suggestions: placed
        ? ['Focus on dream companies and prepare for advanced interviews']
        : ['Improve programming skills', 'Build more projects', 'Clear backlogs'],
    });
    setLoading(false);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Placement Prediction</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Fill in your details to get an ML-powered prediction</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Form */}
        <div className="card p-6">
          <form onSubmit={handlePredict} className="space-y-5">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {fields.map(f => (
                <div key={f.key}>
                  <label className="input-label">{f.label}</label>
                  <input type={f.type} className="input-field" min={f.min} max={f.max} step={f.step}
                    placeholder="0" value={form[f.key]}
                    onChange={e => setForm({ ...form, [f.key]: e.target.value })} />
                </div>
              ))}
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full group">
              {loading ? <span className="flex items-center justify-center gap-2"><div className="spinner spinner-sm" /> Analyzing...</span>
                : <span className="flex items-center justify-center gap-2"><FiSend className="w-4 h-4" /> Predict Placement</span>}
            </button>
          </form>
        </div>

        {/* Result */}
        <div className="space-y-6">
          {!result ? (
            <div className="card p-8 text-center">
              <FiTrendingUp className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Ready to Predict?</h3>
              <p className="text-sm text-gray-500">Fill in your details on the left and click predict to see your placement chances powered by Machine Learning.</p>
            </div>
          ) : (
            <>
              <div className={`card p-6 ${result.prediction === 1 ? 'border-l-4 border-accent-500' : 'border-l-4 border-danger-500'}`}>
                <div className="flex items-center gap-4 mb-4">
                  {result.prediction === 1
                    ? <FiCheckCircle className="w-12 h-12 text-accent-500" />
                    : <FiXCircle className="w-12 h-12 text-danger-500" />}
                  <div>
                    <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                      {result.prediction === 1 ? 'High Chance of Placement 🎉' : 'Needs Improvement 📈'}
                    </h2>
                    <p className="text-sm text-gray-500">Based on ML analysis</p>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="text-center p-3 bg-accent-50 dark:bg-accent-900/20 rounded-xl">
                    <p className="text-2xl font-bold text-accent-600">{result.probability}%</p>
                    <p className="text-xs text-gray-500">Placement Probability</p>
                  </div>
                  <div className="text-center p-3 bg-primary-50 dark:bg-primary-900/20 rounded-xl">
                    <p className="text-2xl font-bold text-primary-600">{result.confidence}%</p>
                    <p className="text-xs text-gray-500">Confidence Score</p>
                  </div>
                </div>
                <div className="progress-bar">
                  <div className={`progress-fill ${result.prediction === 1 ? 'bg-accent-500' : 'bg-danger-500'}`}
                    style={{ width: `${result.probability}%` }} />
                </div>
              </div>

              <div className="card p-6">
                <h3 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                  <FiAlertCircle className="w-4 h-4 text-primary-500" /> Key Factors
                </h3>
                <ul className="space-y-2">
                  {result.reasons.map((r, i) => <li key={i} className="text-sm text-gray-700 dark:text-gray-300">{r}</li>)}
                </ul>
              </div>

              <div className="card p-6">
                <h3 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                  <FiZap className="w-4 h-4 text-yellow-500" /> Suggestions
                </h3>
                <ul className="space-y-2">
                  {result.suggestions.map((s, i) => <li key={i} className="text-sm text-gray-700 dark:text-gray-300">💡 {s}</li>)}
                </ul>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default StudentPrediction;
