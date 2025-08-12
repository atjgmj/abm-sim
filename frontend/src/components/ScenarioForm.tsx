import React, { useState } from 'react';
import { Play, Settings } from 'lucide-react';
import { ScenarioRequest, KPICategory, Granularity, NetworkType, PersonalityConfig, DemographicConfig, InfluencerConfig } from '../types';
import { apiClient } from '../api/client';
import { FieldWithTooltip } from './Tooltip';
import { PARAMETER_TOOLTIPS } from '../utils/tooltips';

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
    decay: 0.9,
    personality_weight: 0.3,
    demographic_weight: 0.2
  },
  network: {
    type: NetworkType.WATTS_STROGATZ,
    n: 10000,
    k: 6,
    beta: 0.1
  },
  personality: {
    openness: 0.5,
    social_influence: 0.5,
    media_affinity: 0.5,
    risk_tolerance: 0.5
  },
  demographics: {
    age_group: 3,
    income_level: 3,
    urban_rural: 0.5,
    education_level: 3
  },
  influencers: {
    enable_influencers: true,
    influencer_ratio: 0.02,
    influence_multiplier: 3.0
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
              <FieldWithTooltip
                label="Simulation Days"
                tooltip={PARAMETER_TOOLTIPS.steps}
              >
                <input
                  type="number"
                  min="1"
                  max="365"
                  value={scenario.steps}
                  onChange={(e) => updateScenario('steps', parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </FieldWithTooltip>
              <FieldWithTooltip
                label="Repetitions"
                tooltip={PARAMETER_TOOLTIPS.repetitions}
              >
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={scenario.reps}
                  onChange={(e) => updateScenario('reps', parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </FieldWithTooltip>
            </div>
            <FieldWithTooltip
              label="Random Seed"
              tooltip={PARAMETER_TOOLTIPS.randomSeed}
            >
              <input
                type="number"
                value={scenario.seed}
                onChange={(e) => updateScenario('seed', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </FieldWithTooltip>
          </div>
        </div>

        {/* Media Mix */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Media Mix</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {(['sns', 'video', 'search'] as const).map(channel => (
              <div key={channel} className="space-y-3">
                <h4 className="font-medium text-gray-700 capitalize">{channel.toUpperCase()}</h4>
                <FieldWithTooltip
                  label="Share (0-1)"
                  tooltip={channel === 'sns' ? PARAMETER_TOOLTIPS.snsShare : 
                          channel === 'video' ? PARAMETER_TOOLTIPS.videoShare : 
                          PARAMETER_TOOLTIPS.searchShare}
                >
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.01"
                    value={scenario.media_mix[channel].share}
                    onChange={(e) => updateScenario(`media_mix.${channel}.share`, parseFloat(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </FieldWithTooltip>
                <FieldWithTooltip
                  label="Alpha (0-1)"
                  tooltip={channel === 'sns' ? PARAMETER_TOOLTIPS.snsAlpha : 
                          channel === 'video' ? PARAMETER_TOOLTIPS.videoAlpha : 
                          PARAMETER_TOOLTIPS.searchAlpha}
                >
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.001"
                    value={scenario.media_mix[channel].alpha}
                    onChange={(e) => updateScenario(`media_mix.${channel}.alpha`, parseFloat(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </FieldWithTooltip>
              </div>
            ))}
          </div>
        </div>

        {/* Network Configuration */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Network Configuration</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <FieldWithTooltip
              label="Type"
              tooltip={PARAMETER_TOOLTIPS.networkType}
            >
              <select
                value={scenario.network.type}
                onChange={(e) => updateScenario('network.type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={NetworkType.ERDOS_RENYI}>Erdős-Rényi</option>
                <option value={NetworkType.WATTS_STROGATZ}>Watts-Strogatz</option>
                <option value={NetworkType.BARABASI_ALBERT}>Barabási-Albert</option>
              </select>
            </FieldWithTooltip>
            <FieldWithTooltip
              label="Nodes (N)"
              tooltip={PARAMETER_TOOLTIPS.networkNodes}
            >
              <input
                type="number"
                min="100"
                max="100000"
                value={scenario.network.n}
                onChange={(e) => updateScenario('network.n', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </FieldWithTooltip>
            <FieldWithTooltip
              label="Avg Degree (k)"
              tooltip={PARAMETER_TOOLTIPS.avgDegree}
            >
              <input
                type="number"
                min="2"
                max="20"
                value={scenario.network.k}
                onChange={(e) => updateScenario('network.k', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </FieldWithTooltip>
            {scenario.network.type === NetworkType.WATTS_STROGATZ && (
              <FieldWithTooltip
                label="Beta"
                tooltip={PARAMETER_TOOLTIPS.rewiringProb}
              >
                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.01"
                  value={scenario.network.beta || 0.1}
                  onChange={(e) => updateScenario('network.beta', parseFloat(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </FieldWithTooltip>
            )}
          </div>
        </div>

        {/* Word of Mouth */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Word of Mouth</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <FieldWithTooltip
              label="Generation Probability"
              tooltip={PARAMETER_TOOLTIPS.womGenerate}
            >
              <input
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={scenario.wom.p_generate}
                onChange={(e) => updateScenario('wom.p_generate', parseFloat(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </FieldWithTooltip>
            <FieldWithTooltip
              label="Decay Factor"
              tooltip={PARAMETER_TOOLTIPS.womDecay}
            >
              <input
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={scenario.wom.decay}
                onChange={(e) => updateScenario('wom.decay', parseFloat(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </FieldWithTooltip>
            <FieldWithTooltip
              label="Personality Weight"
              tooltip={PARAMETER_TOOLTIPS.personalityWeight}
            >
              <input
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={scenario.wom.personality_weight}
                onChange={(e) => updateScenario('wom.personality_weight', parseFloat(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </FieldWithTooltip>
            <FieldWithTooltip
              label="Demographic Weight"
              tooltip={PARAMETER_TOOLTIPS.demographicWeight}
            >
              <input
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={scenario.wom.demographic_weight}
                onChange={(e) => updateScenario('wom.demographic_weight', parseFloat(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </FieldWithTooltip>
          </div>
        </div>

        {/* Personality Configuration */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Personality Configuration</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <FieldWithTooltip
              label="Openness (0-1)"
              tooltip={PARAMETER_TOOLTIPS.openness}
            >
              <input
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={scenario.personality.openness}
                onChange={(e) => updateScenario('personality.openness', parseFloat(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </FieldWithTooltip>
            <FieldWithTooltip
              label="Social Influence (0-1)"
              tooltip={PARAMETER_TOOLTIPS.socialInfluence}
            >
              <input
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={scenario.personality.social_influence}
                onChange={(e) => updateScenario('personality.social_influence', parseFloat(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </FieldWithTooltip>
            <FieldWithTooltip
              label="Media Affinity (0-1)"
              tooltip={PARAMETER_TOOLTIPS.mediaAffinity}
            >
              <input
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={scenario.personality.media_affinity}
                onChange={(e) => updateScenario('personality.media_affinity', parseFloat(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </FieldWithTooltip>
            <FieldWithTooltip
              label="Risk Tolerance (0-1)"
              tooltip={PARAMETER_TOOLTIPS.riskTolerance}
            >
              <input
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={scenario.personality.risk_tolerance}
                onChange={(e) => updateScenario('personality.risk_tolerance', parseFloat(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </FieldWithTooltip>
          </div>
        </div>

        {/* Demographics Configuration */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Demographics Configuration</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <FieldWithTooltip
              label="Age Group (1-5)"
              tooltip={PARAMETER_TOOLTIPS.ageGroup}
            >
              <select
                value={scenario.demographics.age_group}
                onChange={(e) => updateScenario('demographics.age_group', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={1}>18-24</option>
                <option value={2}>25-34</option>
                <option value={3}>35-44</option>
                <option value={4}>45-54</option>
                <option value={5}>55+</option>
              </select>
            </FieldWithTooltip>
            <FieldWithTooltip
              label="Income Level (1-5)"
              tooltip={PARAMETER_TOOLTIPS.incomeLevel}
            >
              <select
                value={scenario.demographics.income_level}
                onChange={(e) => updateScenario('demographics.income_level', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={1}>Very Low</option>
                <option value={2}>Low</option>
                <option value={3}>Medium</option>
                <option value={4}>High</option>
                <option value={5}>Very High</option>
              </select>
            </FieldWithTooltip>
            <FieldWithTooltip
              label="Urban-Rural (0-1)"
              tooltip={PARAMETER_TOOLTIPS.urbanRural}
            >
              <input
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={scenario.demographics.urban_rural}
                onChange={(e) => updateScenario('demographics.urban_rural', parseFloat(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </FieldWithTooltip>
            <FieldWithTooltip
              label="Education Level (1-5)"
              tooltip={PARAMETER_TOOLTIPS.educationLevel}
            >
              <select
                value={scenario.demographics.education_level}
                onChange={(e) => updateScenario('demographics.education_level', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={1}>Elementary</option>
                <option value={2}>High School</option>
                <option value={3}>College</option>
                <option value={4}>Bachelor's</option>
                <option value={5}>Graduate</option>
              </select>
            </FieldWithTooltip>
          </div>
        </div>

        {/* Influencer Configuration */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Influencer Configuration</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <FieldWithTooltip
              label=""
              tooltip={PARAMETER_TOOLTIPS.enableInfluencers}
            >
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={scenario.influencers.enable_influencers}
                  onChange={(e) => updateScenario('influencers.enable_influencers', e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm font-medium text-gray-700">Enable Influencers</span>
              </label>
            </FieldWithTooltip>
            <FieldWithTooltip
              label="Influencer Ratio (0-0.1)"
              tooltip={PARAMETER_TOOLTIPS.influencerRatio}
            >
              <input
                type="number"
                min="0"
                max="0.1"
                step="0.001"
                value={scenario.influencers.influencer_ratio}
                onChange={(e) => updateScenario('influencers.influencer_ratio', parseFloat(e.target.value))}
                disabled={!scenario.influencers.enable_influencers}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              />
            </FieldWithTooltip>
            <FieldWithTooltip
              label="Influence Multiplier (1-10)"
              tooltip={PARAMETER_TOOLTIPS.influenceMultiplier}
            >
              <input
                type="number"
                min="1"
                max="10"
                step="0.1"
                value={scenario.influencers.influence_multiplier}
                onChange={(e) => updateScenario('influencers.influence_multiplier', parseFloat(e.target.value))}
                disabled={!scenario.influencers.enable_influencers}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              />
            </FieldWithTooltip>
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