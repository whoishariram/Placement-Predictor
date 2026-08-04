/**
 * Placement Predictor - Frontend Tests
 * Basic React component smoke tests for critical pages and components
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';

// Helper to wrap components with Router for testing
const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('Landing Page', () => {
  test('renders without crashing', () => {
    const Landing = require('../pages/Landing').default;
    renderWithRouter(<Landing />);
    // Verify the page rendered by checking for common elements
    expect(document.body.innerHTML.length).toBeGreaterThan(0);
  });
});

describe('Student Login Page', () => {
  test('renders without crashing', () => {
    const StudentLogin = require('../pages/StudentLogin').default;
    renderWithRouter(<StudentLogin />);
    expect(document.body.innerHTML.length).toBeGreaterThan(0);
  });
});

describe('Admin Login Page', () => {
  test('renders without crashing', () => {
    const AdminLogin = require('../pages/AdminLogin').default;
    renderWithRouter(<AdminLogin />);
    expect(document.body.innerHTML.length).toBeGreaterThan(0);
  });
});

describe('Student Register Page', () => {
  test('renders without crashing', () => {
    const StudentRegister = require('../pages/StudentRegister').default;
    renderWithRouter(<StudentRegister />);
    expect(document.body.innerHTML.length).toBeGreaterThan(0);
  });
});

describe('Forgot Password Page', () => {
  test('renders without crashing', () => {
    const ForgotPassword = require('../pages/ForgotPassword').default;
    renderWithRouter(<ForgotPassword />);
    expect(document.body.innerHTML.length).toBeGreaterThan(0);
  });
});

describe('404 Not Found Page', () => {
  test('renders without crashing', () => {
    const NotFound = require('../pages/NotFound').default;
    renderWithRouter(<NotFound />);
    expect(document.body.innerHTML.length).toBeGreaterThan(0);
  });
});

describe('Navbar Component', () => {
  test('renders without crashing', () => {
    const Navbar = require('../components/Layout/Navbar').default;
    renderWithRouter(<Navbar />);
    expect(document.body.innerHTML.length).toBeGreaterThan(0);
  });
});

describe('Footer Component', () => {
  test('renders without crashing', () => {
    const Footer = require('../components/Layout/Footer').default;
    renderWithRouter(<Footer />);
    expect(document.body.innerHTML.length).toBeGreaterThan(0);
  });
});

describe('Chart Components', () => {
  test('ChartCard renders without crashing', () => {
    const ChartCard = require('../components/Charts/ChartCard').default;
    renderWithRouter(
      <ChartCard title="Test Chart">
        <div>Chart Content</div>
      </ChartCard>
    );
    expect(document.body.innerHTML.length).toBeGreaterThan(0);
  });
});

describe('Dashboard Pages', () => {
  test('StudentDashboard renders without crashing', () => {
    const StudentDashboard = require('../pages/StudentDashboard').default;
    renderWithRouter(<StudentDashboard />);
    expect(document.body.innerHTML.length).toBeGreaterThan(0);
  });

  test('AdminDashboard renders without crashing', () => {
    const AdminDashboard = require('../pages/AdminDashboard').default;
    renderWithRouter(<AdminDashboard />);
    expect(document.body.innerHTML.length).toBeGreaterThan(0);
  });

  test('Analytics page renders without crashing', () => {
    const Analytics = require('../pages/Analytics').default;
    renderWithRouter(<Analytics />);
    expect(document.body.innerHTML.length).toBeGreaterThan(0);
  });
});

describe('App Routing', () => {
  test('renders without crashing', () => {
    const App = require('../App').default;
    renderWithRouter(<App />);
    expect(document.body.innerHTML.length).toBeGreaterThan(0);
  });
});
