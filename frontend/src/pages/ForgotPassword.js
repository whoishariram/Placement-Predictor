import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { FiMail, FiArrowLeft, FiCheckCircle } from 'react-icons/fi';
import toast from 'react-hot-toast';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email) return toast.error('Please enter your email');
    setLoading(true);
    await new Promise(r => setTimeout(r, 1500));
    setSent(true);
    setLoading(false);
    toast.success('Reset link sent! Check your email.');
  };

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4">
      <div className="w-full max-w-md">
        <div className="card p-8">
          {!sent ? (
            <>
              <div className="text-center mb-8">
                <div className="w-16 h-16 bg-gradient-to-br from-primary-600 to-accent-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <FiMail className="w-8 h-8 text-white" />
                </div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Forgot Password</h1>
                <p className="text-sm text-gray-500 mt-1">Enter your email to receive a reset link</p>
              </div>
              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <label className="input-label">Email Address</label>
                  <input type="email" className="input-field" placeholder="john@college.edu"
                    value={email} onChange={e => setEmail(e.target.value)} />
                </div>
                <button type="submit" disabled={loading} className="btn-primary w-full">
                  {loading ? <span className="flex items-center justify-center gap-2"><div className="spinner spinner-sm" /> Sending...</span> : 'Send Reset Link'}
                </button>
              </form>
              <Link to="/login" className="flex items-center justify-center gap-2 text-sm text-gray-500 mt-6 hover:text-primary-600">
                <FiArrowLeft className="w-4 h-4" /> Back to Login
              </Link>
            </>
          ) : (
            <div className="text-center py-8">
              <FiCheckCircle className="w-16 h-16 text-accent-500 mx-auto mb-4" />
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Check Your Email</h2>
              <p className="text-sm text-gray-500 mb-6">We've sent a password reset link to <strong className="text-gray-700 dark:text-gray-300">{email}</strong></p>
              <Link to="/login" className="btn-primary">Back to Login</Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
