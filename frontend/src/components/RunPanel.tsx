import React, { useState, useEffect } from 'react';
import { Play, Pause, RotateCcw, CheckCircle, XCircle } from 'lucide-react';
import { ScenarioRequest, RunResponse, RunStatus, ResultsResponse } from '../types';
import { apiClient } from '../api/client';

interface Props {
  scenario: ScenarioRequest;
  onRunStarted: (run: RunResponse) => void;
  onRunCompleted: (results: ResultsResponse) => void;
}

export const RunPanel: React.FC<Props> = ({ scenario, onRunStarted, onRunCompleted }) => {
  const [currentRun, setCurrentRun] = useState<RunResponse | null>(null);
  const [status, setStatus] = useState<RunStatus | null>(null);
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState<string>('');
  const [isStarting, setIsStarting] = useState(false);

  // Poll run status
  useEffect(() => {
    if (!currentRun || status === RunStatus.DONE || status === RunStatus.ERROR) {
      return;
    }

    const pollStatus = async () => {
      try {
        const statusResponse = await apiClient.getRunStatus(currentRun.run_id);
        setStatus(statusResponse.status);
        setProgress(statusResponse.progress);
        setMessage(statusResponse.message || '');

        if (statusResponse.status === RunStatus.DONE) {
          // Fetch results
          const results = await apiClient.getResults(currentRun.run_id);
          onRunCompleted(results);
        }
      } catch (error) {
        console.error('Failed to fetch run status:', error);
        setStatus(RunStatus.ERROR);
        setMessage('Failed to fetch status');
      }
    };

    const interval = setInterval(pollStatus, 2000);
    return () => clearInterval(interval);
  }, [currentRun, status, onRunCompleted]);

  const handleStartRun = async () => {
    setIsStarting(true);
    try {
      // First create scenario
      const scenarioResponse = await apiClient.createScenario(scenario);
      
      // Then start run
      const runResponse = await apiClient.createRun({ 
        scenario_id: scenarioResponse.id 
      });
      
      setCurrentRun(runResponse);
      setStatus(RunStatus.QUEUED);
      setProgress(0);
      setMessage('Queued...');
      onRunStarted(runResponse);
      
    } catch (error) {
      console.error('Failed to start run:', error);
      alert('Failed to start simulation. Please try again.');
    } finally {
      setIsStarting(false);
    }
  };

  const handleReset = () => {
    setCurrentRun(null);
    setStatus(null);
    setProgress(0);
    setMessage('');
  };

  const getStatusIcon = () => {
    switch (status) {
      case RunStatus.DONE:
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case RunStatus.ERROR:
        return <XCircle className="h-5 w-5 text-red-600" />;
      case RunStatus.RUNNING:
        return <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600" />;
      default:
        return <Pause className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case RunStatus.DONE:
        return 'bg-green-200 text-green-800';
      case RunStatus.ERROR:
        return 'bg-red-200 text-red-800';
      case RunStatus.RUNNING:
        return 'bg-blue-200 text-blue-800';
      case RunStatus.QUEUED:
        return 'bg-yellow-200 text-yellow-800';
      default:
        return 'bg-gray-200 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Simulation Run</h2>
        {currentRun && (
          <button
            onClick={handleReset}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            Reset
          </button>
        )}
      </div>

      {/* Scenario Summary */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="font-medium text-gray-900 mb-4">Scenario Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="font-medium">Name:</span> {scenario.name}
          </div>
          <div>
            <span className="font-medium">Network:</span> {scenario.network.n.toLocaleString()} nodes
          </div>
          <div>
            <span className="font-medium">Duration:</span> {scenario.steps} days
          </div>
          <div>
            <span className="font-medium">Repetitions:</span> {scenario.reps}
          </div>
        </div>
      </div>

      {/* Run Controls */}
      {!currentRun ? (
        <div className="text-center">
          <button
            onClick={handleStartRun}
            disabled={isStarting}
            className="inline-flex items-center px-8 py-4 border border-transparent text-lg font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Play className="h-6 w-6 mr-3" />
            {isStarting ? 'Starting...' : 'Start Simulation'}
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Status Display */}
          <div className="flex items-center justify-between p-4 bg-white border rounded-lg">
            <div className="flex items-center space-x-3">
              {getStatusIcon()}
              <div>
                <div className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor()}`}>
                  {status?.toUpperCase()}
                </div>
                <div className="text-sm text-gray-600 mt-1">{message}</div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm font-medium text-gray-900">
                {Math.round(progress * 100)}% Complete
              </div>
              <div className="text-xs text-gray-500">
                Run ID: {currentRun.run_id.slice(0, 8)}...
              </div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-blue-600 h-3 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress * 100}%` }}
            />
          </div>

          {/* Estimated Time */}
          {status === RunStatus.RUNNING && (
            <div className="text-center text-sm text-gray-500">
              <div>Running simulation...</div>
              <div className="text-xs">
                Large networks may take several minutes to complete
              </div>
            </div>
          )}

          {/* Completion Message */}
          {status === RunStatus.DONE && (
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <CheckCircle className="h-8 w-8 text-green-600 mx-auto mb-2" />
              <div className="font-medium text-green-900">Simulation Completed!</div>
              <div className="text-sm text-green-700">Results are ready for analysis.</div>
            </div>
          )}

          {/* Error Message */}
          {status === RunStatus.ERROR && (
            <div className="text-center p-4 bg-red-50 rounded-lg">
              <XCircle className="h-8 w-8 text-red-600 mx-auto mb-2" />
              <div className="font-medium text-red-900">Simulation Failed</div>
              <div className="text-sm text-red-700">{message}</div>
              <button
                onClick={handleReset}
                className="mt-3 inline-flex items-center px-4 py-2 border border-red-300 rounded-md shadow-sm text-sm font-medium text-red-700 bg-white hover:bg-red-50"
              >
                Try Again
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};