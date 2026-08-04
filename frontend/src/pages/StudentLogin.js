import React, { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FiMail, FiLock, FiEye, FiEyeOff, FiArrowRight } from 'react-icons/fi';
import { AuthContext } from '../App';
import toast from 'react-hot-toast';

const StudentLogin = () => {
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({ emailOrId: '', password: '' });
  const [errors, setErrors] = useState({});

  const validate = () => {
    const errs = {};
    if (!form.emailOrId.trim()) errs.emailOrId = 'Email or Student ID is required';
    if (!form.password) errs.password = 'Password is required';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    try {
      // Simulate API call — replace with real API when backend is ready
      await new Promise(r => setTimeout(r, 1000));
      
      login({
        id: 1,
        student_id: form.emailOrId,
        name: 'Demo Student',
        email: form.emailOrId.includes('@') ? form.emailOrId : 'student@demo.edu',
        role: 'student',
        department: 'Computer Science',
        year: 4,
        cgpa: 8.2,
      }, 'demo-token-123');

      toast.success('Welcome back! 👋');
      navigate('/student/dashboard');
    } catch (err) {
      toast.error('Invalid credentials. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4">
      <div className="w-full max-w-md">
        <div className="card p-8">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-br from-primary-600 to-accent-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <FiMail className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Student Login</h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Sign in to check your placement status</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="input-label">Email or Student ID</label>
              <input
                type="text"
                className={`input-field ${errors.emailOrId ? 'input-error' : ''}`}
                placeholder="john@college.edu or STU2024001"
                value={form.emailOrId}
                onChange={(e) => setForm({ ...form, emailOrId: e.target.value })}
              />
              {errors.emailOrId && <p className="text-xs text-danger-500 mt-1">{errors.emailOrId}</p>}
            </div>

            <div>
              <label className="input-label">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  className={`input-field pr-12 ${errors.password ? 'input-error' : ''}`}
                  placeholder="Enter your password"
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <FiEyeOff className="w-4 h-4" /> : <FiEye className="w-4 h-4" />}
                </button>
              </div>
              {errors.password && <p className="text-xs text-danger-500 mt-1">{errors.password}</p>}
            </div>

            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                <input type="checkbox" className="rounded border-gray-300" />
                Remember me
              </label>
              <Link to="/forgot-password" className="text-primary-600 hover:text-primary-700 font-medium">
                Forgot password?
              </Link>
            </div>

            <button type="submit" disabled={loading} className="btn-primary w-full group">
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <div className="spinner spinner-sm" /> Signing in...
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  Sign In <FiArrowRight className="group-hover:translate-x-1 transition-transform" />
                </span>
              )}
            </button>
          </form>

          <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-6">
            Don't have an account?{' '}
            <Link to="/register" className="text-primary-600 hover:text-primary-700 font-medium">
              Register here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default StudentLogin;
