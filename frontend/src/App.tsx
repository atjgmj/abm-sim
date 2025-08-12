import React, { useState } from 'react';
import { ScenarioForm } from './components/ScenarioForm';
import { NetworkPreview } from './components/NetworkPreview';
import { RunPanel } from './components/RunPanel';
import { Dashboard } from './components/Dashboard';
import { ParameterCalibration } from './components/ParameterCalibration';
import { ScenarioRequest, RunResponse, ResultsResponse } from './types';

function App() {
  const [currentScenario, setCurrentScenario] = useState<ScenarioRequest | null>(null);
  const [currentRun, setCurrentRun] = useState<RunResponse | null>(null);
  const [results, setResults] = useState<ResultsResponse | null>(null);
  const [activeTab, setActiveTab] = useState<'scenario' | 'calibrate' | 'network' | 'run' | 'results'>('scenario');

  const handleScenarioCreated = (scenario: ScenarioRequest) => {
    setCurrentScenario(scenario);
    setActiveTab('calibrate');
  };

  const handleCalibratedScenario = (calibrated: ScenarioRequest) => {
    setCurrentScenario(calibrated);
    setActiveTab('network');
  };

  const handleRunStarted = (run: RunResponse) => {
    setCurrentRun(run);
    setActiveTab('run');
  };

  const handleRunCompleted = (runResults: ResultsResponse) => {
    setResults(runResults);
    setActiveTab('results');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <h1 className="text-3xl font-bold text-gray-900">
              ABM Communication Campaign Simulator
            </h1>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <nav className="flex space-x-8 mb-8">
          {[
            { id: 'scenario', label: 'Scenario Setup', enabled: true },
            { id: 'calibrate', label: 'Smart Calibration', enabled: !!currentScenario },
            { id: 'network', label: 'Network Preview', enabled: !!currentScenario },
            { id: 'run', label: 'Simulation Run', enabled: !!currentScenario },
            { id: 'results', label: 'Results', enabled: !!results },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => tab.enabled && setActiveTab(tab.id as any)}
              className={`px-1 py-4 text-sm font-medium border-b-2 ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : tab.enabled
                  ? 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  : 'border-transparent text-gray-300 cursor-not-allowed'
              }`}
              disabled={!tab.enabled}
            >
              {tab.label}
            </button>
          ))}
        </nav>

        {/* Tab Content */}
        <div className="bg-white rounded-lg shadow">
          {activeTab === 'scenario' && (
            <div className="p-6">
              <ScenarioForm onScenarioCreated={handleScenarioCreated} />
            </div>
          )}

          {activeTab === 'calibrate' && currentScenario && (
            <div className="p-6">
              <ParameterCalibration 
                scenario={currentScenario}
                onCalibratedScenario={handleCalibratedScenario}
              />
            </div>
          )}

          {activeTab === 'network' && currentScenario && (
            <div className="p-6">
              <NetworkPreview networkConfig={currentScenario.network} />
            </div>
          )}

          {activeTab === 'run' && currentScenario && (
            <div className="p-6">
              <RunPanel 
                scenario={currentScenario}
                onRunStarted={handleRunStarted}
                onRunCompleted={handleRunCompleted}
              />
            </div>
          )}

          {activeTab === 'results' && results && (
            <div className="p-6">
              <Dashboard results={results} />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;