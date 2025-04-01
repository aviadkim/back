import React, { useState } from 'react';

// Sample data
const documents = [
  { id: 1, name: 'Q1 Financial Report.pdf', type: 'PDF', date: '2025-01-15', status: 'Processed', size: '1.2 MB' },
  { id: 2, name: 'Investment Portfolio.xlsx', type: 'Excel', date: '2025-02-20', status: 'Processed', size: '0.8 MB' },
  { id: 3, name: 'Bank Statement March.pdf', type: 'PDF', date: '2025-03-10', status: 'Processing', size: '2.1 MB' },
];

// Summary card stats
const stats = [
  { title: "Total Documents", value: "86", change: "+12%", color: "text-green-500" },
  { title: "Processing Rate", value: "94%", change: "+2%", color: "text-green-500" },
  { title: "Data Points Extracted", value: "12,453", change: "+1,240", color: "text-green-500" }
];

export default function App() { // Renamed from DashboardPreview to App
  const [selectedTab, setSelectedTab] = useState('dashboard');

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-md hidden md:block">
        <div className="flex items-center p-4">
          <div className="text-xl font-bold text-blue-600">FinDoc Analyzer</div>
        </div>
        <hr className="border-gray-200" />
        <nav className="py-4">
          <ul>
            <li
              className={`flex items-center px-4 py-3 cursor-pointer ${selectedTab === 'dashboard' ? 'bg-blue-50 text-blue-600 border-r-4 border-blue-600' : 'text-gray-600 hover:bg-gray-100'}`}
              onClick={() => setSelectedTab('dashboard')}
            >
              <span className="mr-3">📊</span>
              <span className="font-medium">Dashboard</span>
            </li>
            <li
              className={`flex items-center px-4 py-3 cursor-pointer ${selectedTab === 'documents' ? 'bg-blue-50 text-blue-600 border-r-4 border-blue-600' : 'text-gray-600 hover:bg-gray-100'}`}
              onClick={() => setSelectedTab('documents')}
            >
              <span className="mr-3">📄</span>
              <span className="font-medium">Documents</span>
            </li>
            <li
              className={`flex items-center px-4 py-3 cursor-pointer ${selectedTab === 'analytics' ? 'bg-blue-50 text-blue-600 border-r-4 border-blue-600' : 'text-gray-600 hover:bg-gray-100'}`}
              onClick={() => setSelectedTab('analytics')}
            >
              <span className="mr-3">📈</span>
              <span className="font-medium">Analytics</span>
            </li>
            <li
              className={`flex items-center px-4 py-3 cursor-pointer ${selectedTab === 'settings' ? 'bg-blue-50 text-blue-600 border-r-4 border-blue-600' : 'text-gray-600 hover:bg-gray-100'}`}
              onClick={() => setSelectedTab('settings')}
            >
              <span className="mr-3">⚙️</span>
              <span className="font-medium">Settings</span>
            </li>
          </ul>
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        {/* Header */}
        <header className="bg-white shadow-sm">
          <div className="flex justify-between items-center px-6 py-4">
            <h1 className="text-2xl font-bold text-gray-800">Financial Document Analysis</h1>
            <div className="flex items-center space-x-4">
              <div className="relative">
                <span className="p-2 bg-blue-600 text-white rounded-full">🔔</span>
                <span className="absolute top-0 right-0 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">3</span>
              </div>
              <div className="w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center">
                👤
              </div>
            </div>
          </div>
        </header>

        {/* Content */}
        <main className="p-6">
          {/* Document Upload Area */}
          <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
            <h2 className="text-xl font-bold mb-2">Upload Financial Documents</h2>
            <p className="text-gray-600 mb-4">Upload your bank statements, financial reports, or investment documents for analysis</p>

            <div
              className="border-2 border-dashed border-blue-400 rounded-lg p-8 text-center bg-blue-50 cursor-pointer hover:bg-blue-100 transition-colors"
              onClick={() => alert('Upload functionality would be implemented here')}
            >
              <div className="text-5xl text-blue-500 mb-4">📤</div>
              <h3 className="text-lg font-semibold mb-2">Drag and drop files here</h3>
              <p className="text-gray-500 mb-4">Supported formats: PDF, Excel, CSV</p>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                Browse Files
              </button>
            </div>
          </div>

          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            {stats.map((stat, index) => (
              <div key={index} className="bg-white rounded-xl shadow-sm p-6">
                <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">{stat.title}</h3>
                <div className="text-3xl font-bold mt-2 mb-1">{stat.value}</div>
                <div className={stat.color}>{stat.change} from last month</div>
              </div>
            ))}
          </div>

          {/* Documents Table */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold">Your Documents</h2>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center">
                <span className="mr-2">📈</span>
                Analyze Selected
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Document Name</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Upload Date</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Size</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {documents.map((doc) => (
                    <tr key={doc.id} className="hover:bg-gray-50">
                      <td className="px-4 py-4">{doc.name}</td>
                      <td className="px-4 py-4">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          doc.type === 'PDF' ? 'bg-blue-100 text-blue-800' :
                          doc.type === 'Excel' ? 'bg-green-100 text-green-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {doc.type}
                        </span>
                      </td>
                      <td className="px-4 py-4 text-gray-600">{doc.date}</td>
                      <td className="px-4 py-4">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          doc.status === 'Processed' ? 'bg-green-100 text-green-800' :
                          doc.status === 'Processing' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {doc.status}
                        </span>
                      </td>
                      <td className="px-4 py-4 text-gray-600">{doc.size}</td>
                      <td className="px-4 py-4">
                        <div className="flex space-x-2">
                          <button className="p-1 text-blue-600 hover:text-blue-800" title="View">👁️</button>
                          <button className="p-1 text-blue-600 hover:text-blue-800" title="Download">📥</button>
                          <button className="p-1 text-blue-600 hover:text-blue-800" title="Analyze">📊</button>
                          <button className="p-1 text-red-600 hover:text-red-800" title="Delete">🗑️</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
