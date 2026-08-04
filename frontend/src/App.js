import React, { useState, useEffect, createContext, useContext } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// Pages
import Landing from './pages/Landing';
import StudentLogin from './pages/StudentLogin';
import StudentRegister from './pages/StudentRegister';
import AdminLogin from './pages/AdminLogin';
import StudentDashboard from './pages/StudentDashboard';
import AdminDashboard from './pages/AdminDashboard';
import ForgotPassword from './pages/ForgotPassword';
import StudentPrediction from './pages/StudentPrediction';
import CompanyEligibility from './pages/CompanyEligibility';
import Analytics from './pages/Analytics';
import ManageStudents from './pages/ManageStudents';
import ResumeAnalysis from './pages/ResumeAnalysis';
import MentorAlerts from './pages/MentorAlerts';
import NotFound from './pages/NotFound';

// Layout Components
import Navbar from './components/Layout/Navbar';
import Footer from './components/Layout/Footer';

// Context
export const ThemeContext = createContext();
export const AuthContext = createContext();

// Protected Route Component
const ProtectedRoute = ({ children, role }) => {
  const { user } = useContext(AuthContext);

  if (!user) {
    return <Navigate to={role === 'admin' ? '/admin/login' : '/login'} replace />;
  }

  if (role && user.role !== role) {
    return <Navigate to="/" replace />;
  }

  return children;
};

function App() {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : false;
  });

  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('user');
    return saved ? JSON.parse(saved) : null;
  });

  const [token, setToken] = useState(() => {
    return localStorage.getItem('token') || null;
  });

  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  const toggleDarkMode = () => setDarkMode(prev => !prev);

  const login = (userData, authToken) => {
    setUser(userData);
    setToken(authToken);
    localStorage.setItem('user', JSON.stringify(userData));
    localStorage.setItem('token', authToken);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('user');
    localStorage.removeItem('token');
  };

  return (
    <ThemeContext.Provider value={{ darkMode, toggleDarkMode }}>
      <AuthContext.Provider value={{ user, token, login, logout }}>
        <div className={`min-h-screen flex flex-col ${darkMode ? 'dark' : ''}`}>
          <Routes>
            {/* Public routes with Navbar */}
            <Route path="/*" element={
              <>
                <Navbar />
                <main className="flex-1">
                  <Routes>
                    <Route path="/" element={<Landing />} />
                    <Route path="/login" element={<StudentLogin />} />
                    <Route path="/register" element={<StudentRegister />} />
                    <Route path="/admin/login" element={<AdminLogin />} />
                    <Route path="/forgot-password" element={<ForgotPassword />} />
                    <Route path="/student/dashboard" element={
                      <ProtectedRoute role="student">
                        <StudentDashboard />
                      </ProtectedRoute>
                    } />
                    <Route path="/student/predict" element={
                      <ProtectedRoute role="student">
                        <StudentPrediction />
                      </ProtectedRoute>
                    } />
                    <Route path="/student/eligibility" element={
                      <ProtectedRoute role="student">
                        <CompanyEligibility />
                      </ProtectedRoute>
                    } />
                    <Route path="/student/resume" element={
                      <ProtectedRoute role="student">
                        <ResumeAnalysis />
                      </ProtectedRoute>
                    } />
                    <Route path="/admin/dashboard" element={
                      <ProtectedRoute role="admin">
                        <AdminDashboard />
                      </ProtectedRoute>
                    } />
                    <Route path="/admin/analytics" element={
                      <ProtectedRoute role="admin">
                        <Analytics />
                      </ProtectedRoute>
                    } />
                    <Route path="/admin/students" element={
                      <ProtectedRoute role="admin">
                        <ManageStudents />
                      </ProtectedRoute>
                    } />
                    <Route path="/admin/alerts" element={
                      <ProtectedRoute role="admin">
                        <MentorAlerts />
                      </ProtectedRoute>
                    } />
                    <Route path="*" element={<NotFound />} />
                  </Routes>
                </main>
                <Footer />
              </>
            } />
          </Routes>
        </div>
      </AuthContext.Provider>
    </ThemeContext.Provider>
  );
}

export default App;
