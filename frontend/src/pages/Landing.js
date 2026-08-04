import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { motion, useInView } from 'framer-motion';
import {
  FiArrowRight,
  FiTrendingUp,
  FiFileText,
  FiShield,
  FiUsers,
  FiBarChart2,
  FiMail,
  FiCpu,
  FiChevronDown,
  FiStar,
} from 'react-icons/fi';

// ── Animated Counter ──────────────────────────────────────────
const Counter = ({ from = 0, to, suffix = '', duration = 2 }) => {
  const [count, setCount] = useState(from);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-50px' });

  useEffect(() => {
    if (!isInView) return;
    let startTime = null;
    const step = (timestamp) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / (duration * 1000), 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setCount(Math.floor(from + (to - from) * eased));
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [isInView, from, to, duration]);

  return (
    <span ref={ref}>
      {count}
      {suffix}
    </span>
  );
};

// ── Stat Badge ─────────────────────────────────────────────────
const StatBadge = ({ value, label }) => {
  const numValue = parseInt(value.replace(/[^0-9]/g, ''));
  const suffixChar = value.replace(/[0-9]/g, '');

  return (
    <motion.div
      className="text-center p-4 sm:p-6"
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-50px' }}
      transition={{ duration: 0.6 }}
    >
      <div className="text-3xl sm:text-4xl font-bold gradient-text mb-1 tabular-nums">
        <Counter from={0} to={numValue} suffix={suffixChar} duration={2.5} />
      </div>
      <div className="text-sm text-gray-500 dark:text-gray-400">{label}</div>
    </motion.div>
  );
};

// ── Feature Card ───────────────────────────────────────────────
const FeatureCard = ({ icon: Icon, title, description, gradient, index }) => {
  return (
    <motion.div
      className="group relative p-6 sm:p-8 rounded-2xl border border-gray-100 dark:border-gray-700/50 bg-white dark:bg-gray-800/50 backdrop-blur-sm cursor-default"
      initial={{ opacity: 0, y: 60 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-30px' }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      whileHover={{ y: -8, transition: { duration: 0.3 } }}
    >
      {/* Hover glow */}
      <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
        style={{
          background: `radial-gradient(600px circle at var(--mouse-x, 50%) var(--mouse-y, 50%), rgba(59,130,246,0.06), transparent 40%)`
        }}
      />

      <div
        className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 bg-gradient-to-br ${gradient} group-hover:scale-110 group-hover:rotate-3 transition-all duration-300 shadow-lg`}
      >
        <Icon className="w-6 h-6 text-white" />
      </div>

      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
        {title}
      </h3>

      <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
        {description}
      </p>

      {/* Bottom accent line */}
      <div className="mt-4 h-0.5 w-0 group-hover:w-full bg-gradient-to-r from-primary-500 to-accent-400 transition-all duration-500 rounded-full" />
    </motion.div>
  );
};

// ── Floating Orb ───────────────────────────────────────────────
const FloatingOrb = ({ className, size = 'w-72 h-72', gradient = 'from-primary-400/20 to-accent-300/20' }) => (
  <motion.div
    className={`absolute rounded-full blur-3xl ${size} bg-gradient-to-br ${gradient} ${className}`}
    animate={{
      y: [0, -30, 0],
      x: [0, 15, 0],
      scale: [1, 1.05, 1],
    }}
    transition={{
      duration: 8,
      repeat: Infinity,
      ease: 'easeInOut',
    }}
  />
);

// ── Particle Background ────────────────────────────────────────
const ParticleField = () => {
  const particles = Array.from({ length: 20 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: Math.random() * 3 + 1,
    delay: Math.random() * 5,
    duration: Math.random() * 10 + 10,
  }));

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {particles.map((p) => (
        <motion.div
          key={p.id}
          className="absolute rounded-full bg-primary-400/20 dark:bg-primary-400/10"
          style={{
            left: `${p.x}%`,
            top: `${p.y}%`,
            width: p.size,
            height: p.size,
          }}
          animate={{
            y: [0, -30, 0],
            opacity: [0.2, 0.6, 0.2],
          }}
          transition={{
            duration: p.duration,
            repeat: Infinity,
            delay: p.delay,
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  );
};

// ── Animated Step Card ─────────────────────────────────────────
const StepCard = ({ step, title, desc, index }) => {
  return (
    <motion.div
      className="text-center p-6 relative"
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-30px' }}
      transition={{ duration: 0.6, delay: index * 0.2 }}
    >
      {/* Step number */}
      <motion.div
        className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-600 to-accent-500 flex items-center justify-center mx-auto mb-6 text-white text-2xl font-bold shadow-xl relative"
        whileHover={{ scale: 1.1, rotate: [0, -5, 5, 0] }}
        transition={{ duration: 0.3 }}
      >
        {step}
        {/* Pulse ring */}
        <div className="absolute inset-0 rounded-2xl animate-ping-slow opacity-20 bg-primary-500" />
      </motion.div>

      {/* Connector line (desktop) */}
      {index < 2 && (
        <div className="hidden lg:block absolute top-8 left-[60%] w-[80%] h-0.5 bg-gradient-to-r from-primary-300 to-accent-300 dark:from-primary-600 dark:to-accent-600">
          <motion.div
            className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-accent-400"
            animate={{ x: [0, -8, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
        </div>
      )}

      <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">{title}</h3>
      <p className="text-gray-600 dark:text-gray-400 max-w-xs mx-auto">{desc}</p>
    </motion.div>
  );
};

// ── Stagger Container ──────────────────────────────────────────
const StaggerContainer = ({ children, className = '' }) => (
  <motion.div
    className={className}
    initial="hidden"
    whileInView="visible"
    viewport={{ once: true, margin: '-50px' }}
    variants={{
      hidden: {},
      visible: {
        transition: { staggerChildren: 0.1, delayChildren: 0.1 },
      },
    }}
  >
    {children}
  </motion.div>
);

const StaggerItem = ({ children, className = '' }) => (
  <motion.div
    className={className}
    variants={{
      hidden: { opacity: 0, y: 30 },
      visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: 'easeOut' } },
    }}
  >
    {children}
  </motion.div>
);

// ── Section Wrapper ────────────────────────────────────────────
const Section = ({ children, className = '', id }) => (
  <section className={`relative ${className}`} id={id}>
    {children}
  </section>
);

// ── MAIN LANDING COMPONENT ─────────────────────────────────────
const Landing = () => {
  const features = [
    { icon: FiCpu, title: 'ML Predictions', description: 'AI-powered predictions using multiple ML models with auto model selection for best accuracy.', gradient: 'from-primary-600 to-primary-400' },
    { icon: FiFileText, title: 'Resume Analysis', description: 'Upload your resume for AI-powered scoring and actionable improvement suggestions.', gradient: 'from-accent-500 to-accent-400' },
    { icon: FiShield, title: 'Company Eligibility', description: 'Instantly check your eligibility for top companies based on your profile.', gradient: 'from-purple-600 to-purple-400' },
    { icon: FiUsers, title: 'Student Dashboard', description: 'Comprehensive dashboard with placement predictions, eligibility, and history.', gradient: 'from-orange-500 to-orange-400' },
    { icon: FiBarChart2, title: 'Analytics', description: 'Detailed analytics with charts showing placement trends and department performance.', gradient: 'from-pink-600 to-pink-400' },
    { icon: FiMail, title: 'Mentor Alerts', description: 'Automatic email alerts to mentors for students needing guidance and support.', gradient: 'from-red-600 to-red-400' },
  ];

  const stats = [
    { value: '95%+', label: 'Prediction Accuracy' },
    { value: '1000+', label: 'Students Analyzed' },
    { value: '15+', label: 'Companies Evaluated' },
    { value: '10+', label: 'ML Models' },
  ];

  const steps = [
    { step: '01', title: 'Register & Profile', desc: 'Create your account and fill in your academic and skill details.' },
    { step: '02', title: 'Upload Resume', desc: 'Upload your resume for AI-powered analysis and scoring.' },
    { step: '03', title: 'Get Predictions', desc: 'Receive placement predictions and check company eligibility.' },
  ];

  const [scrollY, setScrollY] = useState(0);
  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Spotlight effect tracking for cards (throttled with rAF)
  useEffect(() => {
    let rafId = null;
    const handleMouseMove = (e) => {
      if (rafId) return;
      rafId = requestAnimationFrame(() => {
        rafId = null;
        document.querySelectorAll('.group').forEach((card) => {
          const rect = card.getBoundingClientRect();
          card.style.setProperty('--mouse-x', `${e.clientX - rect.left}px`);
          card.style.setProperty('--mouse-y', `${e.clientY - rect.top}px`);
        });
      });
    };
    window.addEventListener('mousemove', handleMouseMove, { passive: true });
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      if (rafId) cancelAnimationFrame(rafId);
    };
  }, []);

  return (
    <div className="min-h-screen overflow-hidden">
      {/* ════════════════════════════════════════════════════════
          HERO SECTION
          ════════════════════════════════════════════════════════ */}
      <Section className="relative min-h-[90vh] flex items-center overflow-hidden pt-16 pb-20 lg:pb-28">
        {/* Background layers */}
        <div
          className="absolute inset-0 bg-gradient-to-br from-primary-50 via-white to-accent-50 dark:from-gray-900 dark:via-gray-800/95 dark:to-gray-900"
          style={{ transform: `translateY(${scrollY * 0.1}px)` }}
        />

        {/* Grid pattern */}
        <div className="absolute inset-0 bg-grid-gray dark:bg-grid-white opacity-40 dark:opacity-20" />

        {/* Particle field */}
        <ParticleField />

        {/* Gradient orbs */}
        <FloatingOrb className="-top-32 -left-32" size="w-96 h-96" gradient="from-primary-300/20 to-blue-300/10" />
        <FloatingOrb className="-bottom-40 -right-32" size="w-80 h-80" gradient="from-accent-300/20 to-emerald-300/10" />
        <FloatingOrb className="top-1/2 left-1/3" size="w-64 h-64" gradient="from-purple-300/15 to-pink-300/10" />

        {/* Content */}
        <div className="relative w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            className="text-center max-w-4xl mx-auto"
            initial="hidden"
            animate="visible"
            variants={{
              hidden: {},
              visible: {
                transition: { staggerChildren: 0.15, delayChildren: 0.2 },
              },
            }}
          >
            {/* Badge */}
            <StaggerItem>
              <motion.div
                className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 text-sm font-medium mb-8 border border-primary-200 dark:border-primary-700/50"
                whileHover={{ scale: 1.05 }}
              >
                <FiCpu className="w-4 h-4" />
                Powered by Machine Learning
                <span className="w-1.5 h-1.5 rounded-full bg-accent-500 animate-pulse" />
              </motion.div>
            </StaggerItem>

            {/* Headline */}
            <StaggerItem>
              <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-extrabold tracking-tight mb-6 leading-[1.1]">
                <span className="text-gray-900 dark:text-white">Predict Your </span>
                <span className="gradient-text animate-gradient-shift bg-gradient-to-r from-primary-600 via-accent-500 to-purple-600 bg-clip-text">
                  Placement
                </span>
                <br />
                <span className="text-gray-900 dark:text-white">with Confidence</span>
              </h1>
            </StaggerItem>

            {/* Subtitle */}
            <StaggerItem>
              <motion.p
                className="text-lg sm:text-xl md:text-2xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto mb-10 leading-relaxed"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6, duration: 0.8 }}
              >
                An intelligent placement prediction system that helps colleges identify students likely to get placed,
                provides eligibility checking for companies, analyzes resumes, and alerts mentors when guidance is needed.
              </motion.p>
            </StaggerItem>

            {/* CTA Buttons */}
            <StaggerItem>
              <motion.div
                className="flex flex-col sm:flex-row items-center justify-center gap-4"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8, duration: 0.6 }}
              >
                <Link
                  to="/register"
                  className="group relative inline-flex items-center gap-2 bg-primary-600 text-white font-semibold px-8 py-4 rounded-xl hover:bg-primary-700 active:bg-primary-800 transition-all shadow-lg hover:shadow-xl overflow-hidden"
                >
                  {/* Shimmer on hover */}
                  <div className="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-700 bg-gradient-to-r from-transparent via-white/20 to-transparent" />
                  <span className="relative z-10 flex items-center gap-2">
                    Get Started
                    <FiArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </span>
                </Link>

                <Link
                  to="/login"
                  className="relative inline-flex items-center gap-2 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 font-semibold px-8 py-4 rounded-xl border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 active:bg-gray-100 transition-all shadow-sm hover:shadow-md group overflow-hidden"
                >
                  {/* Subtle border glow */}
                  <div className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 bg-gradient-to-r from-primary-500/10 to-accent-500/10" />
                  Student Login
                </Link>
              </motion.div>
            </StaggerItem>

            {/* Scroll indicator */}
            <motion.div
              className="mt-16 flex flex-col items-center gap-2 text-gray-400 dark:text-gray-500"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.5, duration: 1 }}
            >
              <span className="text-xs font-medium tracking-widest uppercase">Scroll to explore</span>
              <motion.div
                animate={{ y: [0, 8, 0] }}
                transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
              >
                <FiChevronDown className="w-5 h-5" />
              </motion.div>
            </motion.div>
          </motion.div>
        </div>
      </Section>

      {/* ════════════════════════════════════════════════════════
          STATS SECTION
          ════════════════════════════════════════════════════════ */}
      <Section className="py-12 sm:py-16 bg-white dark:bg-gray-800/30 border-y border-gray-100 dark:border-gray-700/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 divide-x divide-gray-200 dark:divide-gray-700">
            {stats.map((stat) => (
              <StatBadge key={stat.label} {...stat} />
            ))}
          </div>
        </div>
      </Section>

      {/* ════════════════════════════════════════════════════════
          FEATURES SECTION
          ════════════════════════════════════════════════════════ */}
      <Section className="py-20 sm:py-28 overflow-hidden">
        {/* Background decoration */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-br from-primary-200/10 to-accent-200/10 dark:from-primary-500/5 dark:to-accent-500/5 rounded-full blur-3xl" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Section header */}
          <motion.div
            className="text-center mb-16 sm:mb-20"
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-50px' }}
            transition={{ duration: 0.7 }}
          >
            <motion.div
              className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400 text-xs font-semibold uppercase tracking-wider mb-4"
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4 }}
            >
              <FiStar className="w-3 h-3" />
              Features
            </motion.div>

            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
              Everything You Need
            </h2>
            <p className="text-lg sm:text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              Comprehensive tools for students, mentors, and placement officers
            </p>
          </motion.div>

          {/* Feature grid */}
          <StaggerContainer className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
            {features.map((feature, i) => (
              <FeatureCard key={feature.title} {...feature} index={i} />
            ))}
          </StaggerContainer>
        </div>
      </Section>

      {/* ════════════════════════════════════════════════════════
          HOW IT WORKS SECTION
          ════════════════════════════════════════════════════════ */}
      <Section className="py-20 sm:py-28 bg-white dark:bg-gray-800/30 overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Section header */}
          <motion.div
            className="text-center mb-16 sm:mb-20"
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-50px' }}
            transition={{ duration: 0.7 }}
          >
            <motion.div
              className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent-50 dark:bg-accent-900/20 text-accent-600 dark:text-accent-400 text-xs font-semibold uppercase tracking-wider mb-4"
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4 }}
            >
              <FiTrendingUp className="w-3 h-3" />
              Process
            </motion.div>

            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
              How It Works
            </h2>
            <p className="text-lg sm:text-xl text-gray-600 dark:text-gray-400">
              Simple 3-step process to get your placement prediction
            </p>
          </motion.div>

          {/* Steps */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-12 max-w-4xl mx-auto">
            {steps.map((item, i) => (
              <StepCard key={item.step} {...item} index={i} />
            ))}
          </div>
        </div>
      </Section>

      {/* ════════════════════════════════════════════════════════
          CTA SECTION
          ════════════════════════════════════════════════════════ */}
      <Section className="py-20 sm:py-28 overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary-600 via-primary-700 to-accent-600 p-8 sm:p-12 lg:p-16 text-center"
            initial={{ opacity: 0, y: 60 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-50px' }}
            transition={{ duration: 0.8 }}
          >
            {/* Grid pattern overlay */}
            <div className="absolute inset-0 bg-grid-white opacity-10" />

            {/* Floating orbs inside CTA */}
            <motion.div
              className="absolute -top-20 -right-20 w-60 h-60 rounded-full bg-white/5 blur-3xl"
              animate={{
                scale: [1, 1.2, 1],
                rotate: [0, 45, 0],
              }}
              transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut' }}
            />
            <motion.div
              className="absolute -bottom-20 -left-20 w-60 h-60 rounded-full bg-white/5 blur-3xl"
              animate={{
                scale: [1.2, 1, 1.2],
                rotate: [45, 0, 45],
              }}
              transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut' }}
            />

            {/* Content */}
            <div className="relative">
              <motion.h2
                className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-4"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.2, duration: 0.6 }}
              >
                Ready to Predict Your Placement?
              </motion.h2>

              <motion.p
                className="text-primary-100/90 text-lg mb-8 max-w-xl mx-auto"
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true }}
                transition={{ delay: 0.4, duration: 0.6 }}
              >
                Join thousands of students using our ML-powered system to prepare for campus placements.
              </motion.p>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.6, duration: 0.6 }}
              >
                <Link
                  to="/register"
                  className="group relative inline-flex items-center gap-2 bg-white text-primary-700 font-semibold px-8 sm:px-10 py-4 sm:py-5 rounded-xl hover:bg-primary-50 transition-all shadow-xl hover:shadow-2xl overflow-hidden"
                >
                  {/* Glow effect */}
                  <div className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity bg-gradient-to-r from-primary-100 via-white to-accent-100" />
                  {/* Shimmer */}
                  <div className="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-700 bg-gradient-to-r from-transparent via-primary-200/30 to-transparent" />
                  <span className="relative z-10 flex items-center gap-2">
                    Get Started Free
                    <FiArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </span>
                </Link>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </Section>
    </div>
  );
};

export default Landing;
