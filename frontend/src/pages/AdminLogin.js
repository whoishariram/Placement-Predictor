import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiShield, FiEye, FiEyeOff, FiArrowRight } from 'react-icons/fi';
import { AuthContext } from '../App';
import toast from 'react-hot-toast';

const AdminLogin = () => {
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: 'admin', password: 'admin123' });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.username || !form.password) {
      toast.error('Please enter username and password');
      return;
    }
    setLoading(true);
    try {
      await new Promise(r => setTimeout(r, 800));
      if (form.username === 'admin' && form.password === 'admin123') {
        login({ id: 1, username: 'admin', email: 'admin@placementpredictor.com', role: 'admin' }, 'admin-token-789');
        toast.success('Welcome, Admin! 👋');
        navigate('/admin/dashboard');
      } else {
        toast.error('Invalid credentials');
      }
    } catch { toast.error('Login failed'); }
    finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 bg-gradient-to-br from-gray-900 via-primary-900 to-gray-900">
      <div className="w-full max-w-md">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8 border border-gray-200 dark:border-gray-700">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-br from-primary-600 to-primary-800 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
              <FiShield className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Admin Login</h1>
            <p className="text-sm text-gray-500 mt-1">Authorized personnel only</p>
          </div>
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="input-label">Username</label>
              <input type="text" className="input-field" placeholder="admin"
                value={form.username} onChange={e => setForm({ ...form, username: e.target.value })} />
            </div>
            <div>
              <label className="input-label">Password</label>
              <div className="relative">
                <input type={showPassword ? 'text' : 'password'} className="input-field pr-12"
                  placeholder="••••••••" value={form.password}
                  onChange={e => setForm({ ...form, password: e.target.value })} />
                <button type="button" onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
                  {showPassword ? <FiEyeOff className="w-4 h-4" /> : <FiEye className="w-4 h-4" />}
                </button>
              </div>
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full">
              {loading ? <span className="flex items-center justify-center gap-2"><div className="spinner spinner-sm" /> Authenticating...</span>
                : <span className="flex items-center justify-center gap-2">Sign In <FiArrowRight /></span>}
            </button>
          </form>
          <p className="text-center text-xs text-gray-400 mt-4">Default: admin / admin123</p>
        </div>
      </div>
    </div>
  );
};

export default AdminLogin;
