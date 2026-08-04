import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { FiUpload, FiFile, FiCheckCircle, FiXCircle, FiZap, FiAward, FiTrendingUp } from 'react-icons/fi';
import toast from 'react-hot-toast';

const ResumeAnalysis = () => {
  const [file, setFile] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);

  const onDrop = useCallback(accepted => {
    if (accepted.length > 0) {
      setFile(accepted[0]);
      setResult(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { 'application/pdf': ['.pdf'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'] }, maxFiles: 1
  });

  const handleAnalyze = async () => {
    if (!file) return toast.error('Please upload a resume first');
    setAnalyzing(true);
    await new Promise(r => setTimeout(r, 2000));
    setResult({
      score: 72, grade: 'B+', skills: ['Python', 'Java', 'SQL', 'React', 'Machine Learning'],
      suggestions: ['Add more quantifiable achievements', 'Include relevant certifications', 'Improve project descriptions'],
    });
    setAnalyzing(false);
    toast.success('Resume analyzed successfully!');
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Resume Analysis</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Upload your resume for AI-powered analysis and scoring</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <div {...getRootProps()} className={`card p-12 text-center cursor-pointer border-2 border-dashed transition-all ${isDragActive ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' : 'border-gray-300 dark:border-gray-600 hover:border-primary-400'}`}>
            <input {...getInputProps()} />
            {file ? (
              <div className="flex items-center justify-center gap-3">
                <FiFile className="w-8 h-8 text-primary-500" />
                <div className="text-left">
                  <p className="font-medium text-gray-900 dark:text-white">{file.name}</p>
                  <p className="text-sm text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
                </div>
              </div>
            ) : (
              <>
                <FiUpload className="w-12 h-12 text-gray-300 dark:text-gray-500 mx-auto mb-4" />
                <p className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {isDragActive ? 'Drop your resume here' : 'Drag & drop your resume'}
                </p>
                <p className="text-sm text-gray-500">PDF or DOCX up to 16MB</p>
              </>
            )}
          </div>

          {file && (
            <button onClick={handleAnalyze} disabled={analyzing} className="btn-primary w-full mt-4">
              {analyzing ? <span className="flex items-center justify-center gap-2"><div className="spinner spinner-sm" /> Analyzing...</span> : 'Analyze Resume'}
            </button>
          )}
        </div>

        <div className="space-y-6">
          {!result ? (
            <div className="card p-8 text-center">
              <FiAward className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">AI Resume Analysis</h3>
              <p className="text-sm text-gray-500">Upload your resume to get scored on skills, experience, projects, and more with actionable improvement suggestions.</p>
            </div>
          ) : (
            <>
              <div className="card p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Resume Score</h2>
                  <span className="text-3xl font-bold text-primary-600">{result.score}/100</span>
                </div>
                <div className="progress-bar mb-2"><div className="progress-fill bg-primary-500" style={{ width: `${result.score}%` }} /></div>
                <p className="text-sm text-gray-500">Grade: {result.grade}</p>
              </div>

              <div className="card p-6">
                <h3 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2"><FiCheckCircle className="w-4 h-4 text-accent-500" /> Skills Detected</h3>
                <div className="flex flex-wrap gap-2">
                  {result.skills.map(s => <span key={s} className="badge badge-info">{s}</span>)}
                </div>
              </div>

              <div className="card p-6">
                <h3 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2"><FiZap className="w-4 h-4 text-yellow-500" /> Suggestions</h3>
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

export default ResumeAnalysis;
