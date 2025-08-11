import React, { useMemo, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Download, BarChart3 } from 'lucide-react';
import { ResultsResponse, KPICategory } from '../types';
import { apiClient } from '../api/client';

interface Props {
  results: ResultsResponse;
}

const KPI_COLORS = {
  [KPICategory.AWARENESS]: '#3B82F6',   // blue
  [KPICategory.INTEREST]: '#10B981',    // green
  [KPICategory.KNOWLEDGE]: '#F59E0B',   // yellow
  [KPICategory.LIKING]: '#EF4444',      // red
  [KPICategory.INTENT]: '#8B5CF6',      // purple
};

const KPI_LABELS = {
  [KPICategory.AWARENESS]: 'Awareness',
  [KPICategory.INTEREST]: 'Interest', 
  [KPICategory.KNOWLEDGE]: 'Knowledge',
  [KPICategory.LIKING]: 'Liking',
  [KPICategory.INTENT]: 'Intent',
};

export const Dashboard: React.FC<Props> = ({ results }) => {
  const [activeTab, setActiveTab] = useState<'chart' | 'summary'>('chart');
  const [isExporting, setIsExporting] = useState(false);

  const chartData = useMemo(() => {
    const dataByDay = new Map();
    
    // Group data by day
    results.series.forEach(point => {
      if (!dataByDay.has(point.day)) {
        dataByDay.set(point.day, { day: point.day });
      }
      dataByDay.get(point.day)[point.metric] = point.value;
    });
    
    return Array.from(dataByDay.values()).sort((a, b) => a.day - b.day);
  }, [results.series]);

  const handleExportCSV = async () => {
    setIsExporting(true);
    try {
      const blob = await apiClient.exportResultsCSV(results.run_id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `simulation_${results.run_id.slice(0, 8)}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Export failed:', error);
      alert('Failed to export data. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  const handleExportJSON = () => {
    const dataStr = JSON.stringify(results, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `simulation_${results.run_id.slice(0, 8)}.json`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <BarChart3 className="h-6 w-6 text-blue-600" />
          <h2 className="text-2xl font-bold text-gray-900">Simulation Results</h2>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={handleExportCSV}
            disabled={isExporting}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
          >
            <Download className="h-4 w-4 mr-2" />
            {isExporting ? 'Exporting...' : 'Export CSV'}
          </button>
          <button
            onClick={handleExportJSON}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <Download className="h-4 w-4 mr-2" />
            Export JSON
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <nav className="flex space-x-8">
        {[
          { id: 'chart', label: 'Time Series Chart' },
          { id: 'summary', label: 'Summary Table' },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-1 py-4 text-sm font-medium border-b-2 ${
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      {/* Tab Content */}
      {activeTab === 'chart' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg border">
            <h3 className="text-lg font-medium text-gray-900 mb-4">KPI Evolution Over Time</h3>
            <div style={{ width: '100%', height: '400px' }}>
              <ResponsiveContainer>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="day" 
                    label={{ value: 'Day', position: 'insideBottom', offset: -5 }}
                  />
                  <YAxis 
                    label={{ value: 'Number of People', angle: -90, position: 'insideLeft' }}
                  />
                  <Tooltip 
                    formatter={(value, name) => [value, KPI_LABELS[name as KPICategory]]}
                    labelFormatter={(day) => `Day ${day}`}
                  />
                  <Legend 
                    formatter={(value) => KPI_LABELS[value as KPICategory]}
                  />
                  {Object.entries(KPI_COLORS).map(([kpi, color]) => (
                    <Line
                      key={kpi}
                      type="monotone"
                      dataKey={kpi}
                      stroke={color}
                      strokeWidth={2}
                      dot={false}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* KPI Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {Object.entries(results.summary).map(([kpi, summary]) => (
              <div key={kpi} className="bg-white p-4 rounded-lg border">
                <div className="flex items-center">
                  <div 
                    className="w-3 h-3 rounded-full mr-2"
                    style={{ backgroundColor: KPI_COLORS[kpi as KPICategory] }}
                  />
                  <div className="text-sm font-medium text-gray-900">
                    {KPI_LABELS[kpi as KPICategory]}
                  </div>
                </div>
                <div className="mt-2">
                  <div className="text-2xl font-bold text-gray-900">
                    {summary.end.toLocaleString()}
                  </div>
                  <div className={`text-sm ${
                    summary.delta >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {summary.delta >= 0 ? '+' : ''}{summary.delta.toLocaleString()} from start
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'summary' && (
        <div className="bg-white rounded-lg border">
          <div className="p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Summary Statistics</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      KPI
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Initial
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Final
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Change
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Growth Rate
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {Object.entries(results.summary).map(([kpi, summary]) => {
                    const growthRate = summary.start > 0 
                      ? ((summary.end - summary.start) / summary.start * 100)
                      : 0;
                    
                    return (
                      <tr key={kpi}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div 
                              className="w-3 h-3 rounded-full mr-2"
                              style={{ backgroundColor: KPI_COLORS[kpi as KPICategory] }}
                            />
                            <div className="text-sm font-medium text-gray-900">
                              {KPI_LABELS[kpi as KPICategory]}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {summary.start.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {summary.end.toLocaleString()}
                        </td>
                        <td className={`px-6 py-4 whitespace-nowrap text-sm ${
                          summary.delta >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {summary.delta >= 0 ? '+' : ''}{summary.delta.toLocaleString()}
                        </td>
                        <td className={`px-6 py-4 whitespace-nowrap text-sm ${
                          growthRate >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {growthRate >= 0 ? '+' : ''}{growthRate.toFixed(1)}%
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Run Info */}
      <div className="text-xs text-gray-500 text-center">
        Run ID: {results.run_id} | Generated: {new Date().toLocaleString()}
      </div>
    </div>
  );
};