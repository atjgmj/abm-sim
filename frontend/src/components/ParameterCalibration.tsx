import React, { useState, useEffect } from 'react';
import { Globe, TrendingUp, RefreshCw, Target, AlertCircle, Brain, Database } from 'lucide-react';
import { ScenarioRequest } from '../types';
import { apiClient } from '../api/client';
import { Tooltip } from './Tooltip';
import { PARAMETER_TOOLTIPS } from '../utils/tooltips';

interface Props {
  scenario: ScenarioRequest;
  onCalibratedScenario: (calibrated: ScenarioRequest) => void;
}

interface TrendingTopic {
  keyword: string;
  volume: number;
  sentiment: number;
  growth_rate: number;
}

interface CalibrationResult {
  original_params: any;
  calibrated_params: any;
  data_sources: string[];
  confidence_score: number;
  calibration_notes: string[];
}

interface OptimizationResult {
  optimization_result: {
    best_params: any;
    best_score: number;
    improvement: number;
    confidence: number;
    method_used: string;
    training_samples: number;
  };
  optimized_scenario: any;
  recommendations: string[];
}

interface TrainingDataStatus {
  total_simulations: number;
  suitable_for_training: boolean;
  recommended_minimum: number;
  data_quality: string;
}

export const ParameterCalibration: React.FC<Props> = ({ scenario, onCalibratedScenario }) => {
  const [keywords, setKeywords] = useState<string>('');
  const [trends, setTrends] = useState<TrendingTopic[]>([]);
  const [isCalibrating, setIsCalibrating] = useState(false);
  const [isFetchingTrends, setIsFetchingTrends] = useState(false);
  const [calibrationResult, setCalibrationResult] = useState<CalibrationResult | null>(null);
  const [optimizationResult, setOptimizationResult] = useState<OptimizationResult | null>(null);
  const [trainingDataStatus, setTrainingDataStatus] = useState<TrainingDataStatus | null>(null);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [activeMethod, setActiveMethod] = useState<'external' | 'ml'>('external');

  useEffect(() => {
    fetchTrendingTopics();
    fetchTrainingDataStatus();
  }, []);

  const fetchTrainingDataStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/training-data-status');
      const data = await response.json();
      setTrainingDataStatus(data);
    } catch (error) {
      console.error('Failed to fetch training data status:', error);
    }
  };

  const fetchTrendingTopics = async () => {
    setIsFetchingTrends(true);
    try {
      const response = await fetch('http://localhost:8000/api/trending');
      const data = await response.json();
      setTrends(data.trends);
    } catch (error) {
      console.error('Failed to fetch trending topics:', error);
    } finally {
      setIsFetchingTrends(false);
    }
  };

  const handleCalibrate = async () => {
    if (!keywords.trim()) {
      alert('Please enter campaign keywords');
      return;
    }

    setIsCalibrating(true);
    try {
      const keywordList = keywords.split(',').map(k => k.trim()).filter(k => k);
      
      const response = await fetch('http://localhost:8000/api/calibrate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          campaign_keywords: keywordList,
          baseline_scenario: scenario,
          api_keys: null // For demo purposes, using synthetic data
        })
      });

      if (!response.ok) {
        throw new Error('Calibration failed');
      }

      const result: CalibrationResult = await response.json();
      setCalibrationResult(result);
      
      // Apply calibrated parameters to scenario
      const calibratedScenario = {
        ...scenario,
        ...result.calibrated_params
      };
      
      onCalibratedScenario(calibratedScenario);
      
    } catch (error) {
      console.error('Calibration error:', error);
      alert('Failed to calibrate parameters. Please try again.');
    } finally {
      setIsCalibrating(false);
    }
  };

  const handleOptimizeML = async () => {
    setIsOptimizing(true);
    try {
      const response = await fetch('http://localhost:8000/api/optimize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          base_scenario: scenario,
          optimization_targets: [
            { kpi: 'awareness', target_value: 5000, weight: 0.6 },
            { kpi: 'intent', target_value: 1000, weight: 0.4 }
          ],
          n_trials: 30
        })
      });

      if (!response.ok) {
        throw new Error('ML optimization failed');
      }

      const result: OptimizationResult = await response.json();
      setOptimizationResult(result);
      
      // Apply optimized scenario
      const optimizedScenario = {
        ...scenario,
        ...result.optimized_scenario
      };
      
      onCalibratedScenario(optimizedScenario);
      
    } catch (error) {
      console.error('ML optimization error:', error);
      alert('Failed to optimize parameters with ML. Please try again.');
    } finally {
      setIsOptimizing(false);
    }
  };

  const addTrendingKeyword = (keyword: string) => {
    const currentKeywords = keywords.split(',').map(k => k.trim()).filter(k => k);
    if (!currentKeywords.includes(keyword)) {
      setKeywords(currentKeywords.concat(keyword).join(', '));
    }
  };

  const getSentimentColor = (sentiment: number) => {
    if (sentiment > 0.1) return 'text-green-600';
    if (sentiment < -0.1) return 'text-red-600';
    return 'text-gray-600';
  };

  const getConfidenceColor = (score: number) => {
    if (score > 0.7) return 'text-green-600';
    if (score > 0.4) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Globe className="h-6 w-6 text-blue-600" />
          <h3 className="text-xl font-bold text-gray-900">Smart Parameter Calibration</h3>
          <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">BETA</span>
        </div>
        
        {/* Method Selection */}
        <div className="flex space-x-2 bg-gray-100 p-1 rounded-md">
          <button
            onClick={() => setActiveMethod('external')}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              activeMethod === 'external'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <Globe className="h-4 w-4 inline mr-1" />
            External Data
          </button>
          <button
            onClick={() => setActiveMethod('ml')}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              activeMethod === 'ml'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <Brain className="h-4 w-4 inline mr-1" />
            ML Optimization
          </button>
        </div>
      </div>

      {/* External Data Method */}
      {activeMethod === 'external' && (
        <>
          {/* Trending Topics */}
          <div className="bg-white p-4 rounded-lg border">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <TrendingUp className="h-5 w-5 text-green-600" />
            <h4 className="font-medium text-gray-900">Trending Topics</h4>
            <Tooltip content={PARAMETER_TOOLTIPS.trendingTopics} position="right" />
          </div>
          <button
            onClick={fetchTrendingTopics}
            disabled={isFetchingTrends}
            className="p-1 text-gray-500 hover:text-gray-700 disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${isFetchingTrends ? 'animate-spin' : ''}`} />
          </button>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
          {trends.map((trend, index) => (
            <button
              key={index}
              onClick={() => addTrendingKeyword(trend.keyword)}
              className="p-2 text-left border rounded-md hover:bg-gray-50 transition-colors"
            >
              <div className="text-sm font-medium text-gray-900">{trend.keyword}</div>
              <div className="text-xs text-gray-500">
                {(trend.volume / 1000).toFixed(0)}k mentions
              </div>
              <div className={`text-xs ${getSentimentColor(trend.sentiment)}`}>
                {trend.sentiment > 0 ? '↗' : trend.sentiment < 0 ? '↘' : '→'} 
                {(trend.growth_rate * 100).toFixed(0)}%
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Campaign Keywords Input */}
      <div className="bg-white p-4 rounded-lg border">
        <div className="flex items-center space-x-2 mb-3">
          <h4 className="font-medium text-gray-900">Campaign Keywords</h4>
          <Tooltip content={PARAMETER_TOOLTIPS.campaignKeywords} position="right" />
        </div>
        <div className="space-y-3">
          <textarea
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
            placeholder="Enter campaign keywords separated by commas (e.g., sustainability, green energy, eco-friendly)"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={3}
          />
          <button
            onClick={handleCalibrate}
            disabled={isCalibrating || !keywords.trim()}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Target className="h-4 w-4 mr-2" />
            {isCalibrating ? 'Calibrating...' : 'Calibrate Parameters'}
          </button>
        </div>
      </div>

      {/* Calibration Results */}
      {calibrationResult && (
        <div className="bg-white p-4 rounded-lg border">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-medium text-gray-900">Calibration Results</h4>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">Confidence:</span>
              <span className={`font-medium ${getConfidenceColor(calibrationResult.confidence_score)}`}>
                {(calibrationResult.confidence_score * 100).toFixed(0)}%
              </span>
            </div>
          </div>

          <div className="space-y-4">
            {/* Data Sources */}
            <div>
              <span className="text-sm font-medium text-gray-700">Data Sources: </span>
              <span className="text-sm text-gray-600">
                {calibrationResult.data_sources.join(', ')}
              </span>
            </div>

            {/* Calibration Notes */}
            <div>
              <h5 className="text-sm font-medium text-gray-700 mb-2">Applied Adjustments:</h5>
              <ul className="space-y-1">
                {calibrationResult.calibration_notes.map((note, index) => (
                  <li key={index} className="text-sm text-gray-600 flex items-start">
                    <span className="text-blue-600 mr-2">•</span>
                    {note}
                  </li>
                ))}
              </ul>
            </div>

            {/* Show Advanced Details Toggle */}
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              {showAdvanced ? 'Hide' : 'Show'} parameter changes
            </button>

            {/* Advanced Parameter Comparison */}
            {showAdvanced && (
              <div className="mt-4 p-3 bg-gray-50 rounded-md">
                <h5 className="text-sm font-medium text-gray-700 mb-2">Parameter Changes:</h5>
                <div className="text-xs space-y-1">
                  {Object.entries(calibrationResult.calibrated_params).map(([key, value]) => {
                    if (typeof value === 'object' && value !== null) {
                      return (
                        <div key={key} className="text-gray-600">
                          <strong>{key}:</strong> {JSON.stringify(value, null, 2)}
                        </div>
                      );
                    }
                    return null;
                  })}
                </div>
              </div>
            )}

            {/* Warning for synthetic data */}
            {calibrationResult.confidence_score < 0.6 && (
              <div className="flex items-start space-x-2 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                <AlertCircle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                <div className="text-sm text-yellow-700">
                  <strong>Demo Mode:</strong> Using synthetic data for calibration. 
                  Connect real API keys for production accuracy.
                </div>
              </div>
            )}
          </div>
        </div>
      )}
      </>
      )}

      {/* ML Optimization Method */}
      {activeMethod === 'ml' && (
        <>
          {/* Training Data Status */}
          {trainingDataStatus && (
            <div className="bg-white p-4 rounded-lg border">
              <div className="flex items-center space-x-2 mb-3">
                <Database className="h-5 w-5 text-purple-600" />
                <h4 className="font-medium text-gray-900">Training Data Status</h4>
                <Tooltip content={PARAMETER_TOOLTIPS.trainingData} position="right" />
              </div>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Available Simulations:</span>
                  <span className="font-medium">{trainingDataStatus.total_simulations}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Data Quality:</span>
                  <span className={`font-medium ${
                    trainingDataStatus.data_quality === 'Good' ? 'text-green-600' :
                    trainingDataStatus.data_quality === 'Limited' ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {trainingDataStatus.data_quality}
                  </span>
                </div>
                
                <div className="text-xs text-gray-500">
                  Recommended minimum: {trainingDataStatus.recommended_minimum} simulations
                </div>
                
                {!trainingDataStatus.suitable_for_training && (
                  <div className="flex items-start space-x-2 p-3 bg-orange-50 border border-orange-200 rounded-md">
                    <AlertCircle className="h-5 w-5 text-orange-600 flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-orange-700">
                      <strong>Insufficient Data:</strong> Run more simulations to improve ML optimization accuracy.
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
          
          {/* ML Optimization Controls */}
          <div className="bg-white p-4 rounded-lg border">
            <h4 className="font-medium text-gray-900 mb-3">Machine Learning Optimization</h4>
            <div className="space-y-3">
              <p className="text-sm text-gray-600">
                Uses historical simulation data to optimize parameters for maximum campaign effectiveness.
              </p>
              
              <button
                onClick={handleOptimizeML}
                disabled={isOptimizing}
                className="inline-flex items-center px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Brain className="h-4 w-4 mr-2" />
                {isOptimizing ? 'Optimizing...' : 'Optimize with ML'}
              </button>
              
              {trainingDataStatus && !trainingDataStatus.suitable_for_training && (
                <p className="text-xs text-gray-500">
                  Note: Will use fallback random search due to insufficient training data
                </p>
              )}
            </div>
          </div>
          
          {/* ML Optimization Results */}
          {optimizationResult && (
            <div className="bg-white p-4 rounded-lg border">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-gray-900">ML Optimization Results</h4>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">Confidence:</span>
                  <span className={`font-medium ${getConfidenceColor(optimizationResult.optimization_result.confidence)}`}>
                    {(optimizationResult.optimization_result.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              </div>

              <div className="space-y-4">
                {/* Method and Performance */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm font-medium text-gray-700">Method:</span>
                    <div className="text-sm text-gray-600">{optimizationResult.optimization_result.method_used}</div>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-700">Training Samples:</span>
                    <div className="text-sm text-gray-600">{optimizationResult.optimization_result.training_samples}</div>
                  </div>
                </div>
                
                <div>
                  <span className="text-sm font-medium text-gray-700">Expected Improvement:</span>
                  <div className={`text-sm font-medium ${
                    optimizationResult.optimization_result.improvement > 10 ? 'text-green-600' :
                    optimizationResult.optimization_result.improvement > 0 ? 'text-blue-600' : 'text-gray-600'
                  }`}>
                    {optimizationResult.optimization_result.improvement > 0 ? '+' : ''}{optimizationResult.optimization_result.improvement.toFixed(1)}%
                  </div>
                </div>

                {/* Recommendations */}
                <div>
                  <h5 className="text-sm font-medium text-gray-700 mb-2">Recommendations:</h5>
                  <ul className="space-y-1">
                    {optimizationResult.recommendations.map((rec, index) => (
                      <li key={index} className="text-sm text-gray-600 flex items-start">
                        <span className="text-purple-600 mr-2">•</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};