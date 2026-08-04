import React, { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FiUserPlus, FiEye, FiEyeOff, FiArrowRight } from 'react-icons/fi';
import { AuthContext } from '../App';
import toast from 'react-hot-toast';

const StudentRegister = () => {
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    studentId: '', name: '', email: '', password: '', confirmPassword: '',
    department: '', year: '', cgpa: ''
  });
  const [errors, setErrors] = useState({});

  const departments = [
    'Computer Science', 'Information Technology', 'Electronics & Communication',
    'Electrical Engineering', 'Mechanical Engineering', 'Civil Engineering',
    'Artificial Intelligence & ML', 'Data Science'
  ];

  const validate = () => {
    const errs = {};
    if (!form.studentId.trim()) errs.studentId = 'Student ID is required';
    if (!form.name.trim()) errs.name = 'Name is required';
    if (!form.email.trim()) errs.email = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(form.email)) errs.email = 'Invalid email format';
    if (!form.password) errs.password = 'Password is required';
    else if (form.password.length < 6) errs.password = 'Min 6 characters';
    if (form.password !== form.confirmPassword) errs.confirmPassword = 'Passwords do not match';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    try {
      await new Promise(r => setTimeout(r, 1000));
      login({
        id: 1, student_id: form.studentId, name: form.name,
        email: form.email, role: 'student',
        department: form.department || 'Computer Science',
        year: parseInt(form.year) || 4, cgpa: parseFloat(form.cgpa) || 0,
      }, 'demo-token-456');
      toast.success('Registration successful! Welcome aboard 🎉');
      navigate('/student/dashboard');
    } catch {
      toast.error('Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const updateField = (field, value) => {
    setForm(prev => ({ ...prev, [field]: value }));
    if (errors[field]) setErrors(prev => ({ ...prev, [field]: undefined }));
  };

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4">
      <div className="w-full max-w-2xl">
        <div className="card p-8">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-br from-accent-500 to-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <FiUserPlus className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Student Registration</h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Create your account to get started</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div>
                <label className="input-label">Student ID *</label>
                <input type="text" className={`input-field ${errors.studentId ? 'input-error' : ''}`}
                  placeholder="STU2024001" value={form.studentId}
                  onChange={e => updateField('studentId', e.target.value)} />
                {errors.studentId && <p className="text-xs text-danger-500 mt-1">{errors.studentId}</p>}
              </div>
              <div>
                <label className="input-label">Full Name *</label>
                <input type="text" className={`input-field ${errors.name ? 'input-error' : ''}`}
                  placeholder="John Doe" value={form.name}
                  onChange={e => updateField('name', e.target.value)} />
                {errors.name && <p className="text-xs text-danger-500 mt-1">{errors.name}</p>}
              </div>
              <div>
                <label className="input-label">Email *</label>
                <input type="email" className={`input-field ${errors.email ? 'input-error' : ''}`}
                  placeholder="john@college.edu" value={form.email}
                  onChange={e => updateField('email', e.target.value)} />
                {errors.email && <p className="text-xs text-danger-500 mt-1">{errors.email}</p>}
              </div>
              <div>
                <label className="input-label">Department</label>
                <select className="input-field" value={form.department}
                  onChange={e => updateField('department', e.target.value)}>
                  <option value="">Select Department</option>
                  {departments.map(d => <option key={d} value={d}>{d}</option>)}
                </select>
              </div>
              <div>
                <label className="input-label">Year</label>
                <select className="input-field" value={form.year}
                  onChange={e => updateField('year', e.target.value)}>
                  <option value="">Select Year</option>
                  {[1, 2, 3, 4].map(y => <option key={y} value={y}>{y}th Year</option>)}
                </select>
              </div>
              <div>
                <label className="input-label">CGPA</label>
                <input type="number" step="0.01" min="0" max="10" className="input-field"
                  placeholder="8.5" value={form.cgpa}
                  onChange={e => updateField('cgpa', e.target.value)} />
              </div>
              <div>
                <label className="input-label">Password *</label>
                <div className="relative">
                  <input type={showPassword ? 'text' : 'password'}
                    className={`input-field pr-12 ${errors.password ? 'input-error' : ''}`}
                    placeholder="Min 6 characters" value={form.password}
                    onChange={e => updateField('password', e.target.value)} />
                  <button type="button" onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
                    {showPassword ? <FiEyeOff className="w-4 h-4" /> : <FiEye className="w-4 h-4" />}
                  </button>
                </div>
                {errors.password && <p className="text-xs text-danger-500 mt-1">{errors.password}</p>}
              </div>
              <div>
                <label className="input-label">Confirm Password *</label>
                <input type="password"
                  className={`input-field ${errors.confirmPassword ? 'input-error' : ''}`}
                  placeholder="Repeat password" value={form.confirmPassword}
                  onChange={e => updateField('confirmPassword', e.target.value)} />
                {errors.confirmPassword && <p className="text-xs text-danger-500 mt-1">{errors.confirmPassword}</p>}
              </div>
            </div>

            <button type="submit" disabled={loading} className="btn-primary w-full group">
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <div className="spinner spinner-sm" /> Creating account...
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  Create Account <FiArrowRight className="group-hover:translate-x-1 transition-transform" />
                </span>
              )}
            </button>
          </form>

          <p className="text-center text-sm text-gray-500 mt-6">
            Already have an account?{' '}
            <Link to="/login" className="text-primary-600 hover:text-primary-700 font-medium">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default StudentRegister;
