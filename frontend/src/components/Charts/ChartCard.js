import React, { useState } from 'react';
import { FiMaximize2, FiMinimize2, FiDownload, FiRefreshCw } from 'react-icons/fi';
import { jsPDF } from 'jspdf';
import html2canvas from 'html2canvas';
import toast from 'react-hot-toast';

const ChartCard = ({
  title,
  icon: Icon,
  gradient = 'from-primary-500 to-primary-400',
  children,
  height = 350,
  action,
  onRefresh,
  className = '',
  downloadable = false,
}) => {
  const [expanded, setExpanded] = useState(false);
  const [exporting, setExporting] = useState(false);

  const handleDownload = async () => {
    setExporting(true);
    try {
      const element = document.getElementById(`chart-${title?.replace(/\s+/g, '-')}`);
      if (!element) {
        toast.error('Chart element not found');
        return;
      }
      const canvas = await html2canvas(element, {
        backgroundColor: '#ffffff',
        scale: 2,
      });
      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('landscape');
      pdf.addImage(imgData, 'PNG', 10, 10, 280, 150);
      pdf.save(`${title?.replace(/\s+/g, '_')}_chart.pdf`);
      toast.success('Chart downloaded as PDF');
    } catch (err) {
      toast.error('Failed to download chart');
    } finally {
      setExporting(false);
    }
  };

  return (
    <div
      className={`card ${expanded ? 'fixed inset-4 z-50 overflow-auto' : ''} transition-all duration-300 ${className}`}
      id={`chart-${title?.replace(/\s+/g, '-')}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          {Icon && (
            <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center shadow-sm`}>
              <Icon className="w-5 h-5 text-white" />
            </div>
          )}
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white text-sm">{title}</h3>
            {action && <p className="text-xs text-gray-400 mt-0.5">{action}</p>}
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-1">
          {downloadable && (
            <button
              onClick={handleDownload}
              disabled={exporting}
              className="p-2 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all"
              title="Download as PDF"
            >
              <FiDownload className={`w-4 h-4 ${exporting ? 'animate-pulse' : ''}`} />
            </button>
          )}
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="p-2 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all"
              title="Refresh"
            >
              <FiRefreshCw className="w-4 h-4" />
            </button>
          )}
          <button
            onClick={() => setExpanded(!expanded)}
            className="p-2 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all"
            title={expanded ? 'Collapse' : 'Expand'}
          >
            {expanded ? <FiMinimize2 className="w-4 h-4" /> : <FiMaximize2 className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Chart Content */}
      <div style={{ height: expanded ? 'calc(100% - 60px)' : height }} className="transition-all duration-300">
        {children}
      </div>
    </div>
  );
};

export default ChartCard;
