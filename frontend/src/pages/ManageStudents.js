import React, { useState } from 'react';
import { FiSearch, FiUserPlus, FiEdit2, FiTrash2, FiDownload, FiFilter } from 'react-icons/fi';

const ManageStudents = () => {
  const [students] = useState([
    { id: 'STU1001', name: 'Alice Johnson', dept: 'Computer Science', cgpa: 8.5, status: 'Placed', company: 'Google' },
    { id: 'STU1002', name: 'Bob Smith', dept: 'Information Technology', cgpa: 7.2, status: 'Not Placed', company: '-' },
    { id: 'STU1003', name: 'Carol Lee', dept: 'Electronics', cgpa: 6.8, status: 'Not Placed', company: '-' },
    { id: 'STU1004', name: 'David Brown', dept: 'Computer Science', cgpa: 9.1, status: 'Placed', company: 'Microsoft' },
    { id: 'STU1005', name: 'Eve Davis', dept: 'Mechanical', cgpa: 7.5, status: 'Placed', company: 'Infosys' },
  ]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Manage Students</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">View and manage all student records</p>
        </div>
        <div className="flex gap-3">
          <button className="btn-secondary btn-sm"><FiDownload className="w-4 h-4 mr-1 inline" /> Import</button>
          <button className="btn-primary btn-sm"><FiUserPlus className="w-4 h-4 mr-1 inline" /> Add Student</button>
        </div>
      </div>

      <div className="card">
        <div className="p-4 border-b border-gray-100 dark:border-gray-700 flex flex-wrap gap-4">
          <div className="flex items-center gap-3 flex-1 min-w-[200px]">
            <FiSearch className="w-5 h-5 text-gray-400" />
            <input type="text" className="flex-1 bg-transparent border-none outline-none text-sm text-gray-700 dark:text-gray-300 placeholder-gray-400" placeholder="Search by name, ID, or department..." />
          </div>
          <button className="btn-secondary btn-sm"><FiFilter className="w-4 h-4 mr-1 inline" /> Filters</button>
        </div>
        <div className="table-container border-0">
          <table className="table">
            <thead>
              <tr><th>ID</th><th>Name</th><th>Department</th><th>CGPA</th><th>Status</th><th>Company</th><th>Actions</th></tr>
            </thead>
            <tbody>
              {students.map(s => (
                <tr key={s.id}>
                  <td className="font-mono text-xs">{s.id}</td>
                  <td className="font-medium">{s.name}</td>
                  <td>{s.dept}</td>
                  <td>{s.cgpa}</td>
                  <td><span className={`badge ${s.status === 'Placed' ? 'badge-success' : 'badge-warning'}`}>{s.status}</span></td>
                  <td>{s.company}</td>
                  <td>
                    <div className="flex gap-2">
                      <button className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-primary-600"><FiEdit2 className="w-4 h-4" /></button>
                      <button className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-danger-600"><FiTrash2 className="w-4 h-4" /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="p-4 border-t border-gray-100 dark:border-gray-700 flex justify-between items-center text-sm text-gray-500">
          <span>Showing 5 of 1,024 students</span>
          <div className="flex gap-2">
            <button className="px-3 py-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">Previous</button>
            <button className="px-3 py-1 rounded-lg bg-primary-600 text-white">1</button>
            <button className="px-3 py-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">2</button>
            <button className="px-3 py-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">Next</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ManageStudents;
