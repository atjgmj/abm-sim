import React, { useState } from 'react';
import { Play, Settings } from 'lucide-react';
import { ScenarioRequest, KPICategory, Granularity, NetworkType } from '../types';
import { apiClient } from '../api/client';

interface Props {
  onScenarioCreated: (scenario: ScenarioRequest) => void;
}

const defaultScenario: ScenarioRequest = {
  name: "Baseline A",
  kpi: {
    categories: [
      KPICategory.AWARENESS,
      KPICategory.INTEREST, 
      KPICategory.KNOWLEDGE,
      KPICategory.LIKING,
      KPICategory.INTENT
    ],
    granularity: Granularity.BRAND
  },
  media_mix: {
    sns: { share: 0.5, alpha: 0.03 },
    video: { share: 0.3, alpha: 0.02 },
    search: { share: 0.2, alpha: 0.01 }
  },
  wom: {
    p_generate: 0.08,
    decay: 0.9
  },
  network: {
    type: NetworkType.WATTS_STROGATZ,
    n: 10000,
    k: 6,
    beta: 0.1
  },
  steps: 60,
  reps: 10,
  seed: 42
};

export const ScenarioForm: React.FC<Props> = ({ onScenarioCreated }) => {
  const [scenario, setScenario] = useState<ScenarioRequest>(defaultScenario);
  const [isLoading, setIsLoading] = useState(false);

  const updateScenario = (path: string, value: any) => {
    setScenario(prev => {
      const newScenario = { ...prev };
      const keys = path.split('.');
      let current: any = newScenario;
      
      for (let i = 0; i < keys.length - 1; i++) {
        current = current[keys[i]];
      }
      
      current[keys[keys.length - 1]] = value;
      return newScenario;
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      await apiClient.createScenario(scenario);
      onScenarioCreated(scenario);
    } catch (error) {
      console.error('Failed to create scenario:', error);
      alert('Failed to create scenario. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center space-x-3">
        <Settings className="h-6 w-6 text-blue-600" />
        <h2 className="text-2xl font-bold text-gray-900">Scenario Configuration</h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Basic Settings */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Scenario Name
              </label>
              <input
                type="text"
                value={scenario.name}
                onChange={(e) => updateScenario('name', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                KPI Granularity
              </label>
              <select
                value={scenario.kpi.granularity}
                onChange={(e) => updateScenario('kpi.granularity', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={Granularity.BRAND}>Brand</option>
                <option value={Granularity.SERVICE}>Service</option>
                <option value={Granularity.CAMPAIGN}>Campaign</option>
              </select>
            </div>
          </div>

          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Simulation Days
                </label>
                <input
                  type="number"
                  min="1"
                  max="365"
                  value={scenario.steps}
                  onChange={(e) => updateScenario('steps', parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Repetitions
                </label>
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={scenario.reps}
                  onChange={(e) => updateScenario('reps', parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Random Seed
              </label>
              <input
                type="number"
                value={scenario.seed}
                onChange={(e) => updateScenario('seed', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Media Mix */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Media Mix</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {(['sns', 'video', 'search'] as const).map(channel => (
              <div key={channel} className="space-y-3">
                <h4 className="font-medium text-gray-700 capitalize">{channel}</h4>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Share (0-1)</label>
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.01"
                    value={scenario.media_mix[channel].share}
                    onChange={(e) => updateScenario(`media_mix.${channel}.share`, parseFloat(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Alpha (0-1)</label>
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.001"
                    value={scenario.media_mix[channel].alpha}
                    onChange={(e) => updateScenario(`media_mix.${channel}.alpha`, parseFloat(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Network Configuration */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Network Configuration</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Type</label>
              <select
                value={scenario.network.type}
                onChange={(e) => updateScenario('network.type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={NetworkType.ERDOS_RENYI}>Erdős-Rényi</option>
                <option value={NetworkType.WATTS_STROGATZ}>Watts-Strogatz</option>
                <option value={NetworkType.BARABASI_ALBERT}>Barabási-Albert</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Nodes (N)</label>
              <input
                type="number"
                min="100"
                max="100000"
                value={scenario.network.n}
                onChange={(e) => updateScenario('network.n', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Avg Degree (k)</label>
              <input
                type="number"
                min="2"
                max="20"
                value={scenario.network.k}
                onChange={(e) => updateScenario('network.k', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            {scenario.network.type === NetworkType.WATTS_STROGATZ && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Beta</label>
                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.01"
                  value={scenario.network.beta || 0.1}
                  onChange={(e) => updateScenario('network.beta', parseFloat(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            )}
          </div>
        </div>

        {/* Word of Mouth */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Word of Mouth</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Generation Probability
              </label>
              <input
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={scenario.wom.p_generate}
                onChange={(e) => updateScenario('wom.p_generate', parseFloat(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Decay Factor
              </label>
              <input
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={scenario.wom.decay}
                onChange={(e) => updateScenario('wom.decay', parseFloat(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Submit */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isLoading}
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Play className="h-5 w-5 mr-2" />
            {isLoading ? 'Creating...' : 'Create Scenario'}
          </button>
        </div>
      </form>
    </div>
  );
};