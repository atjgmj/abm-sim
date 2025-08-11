import axios from 'axios';
import {
  ScenarioRequest,
  ScenarioResponse,
  RunRequest,
  RunResponse,
  RunStatusResponse,
  ResultsResponse,
  NetworkConfig,
  NetworkPreviewResponse,
} from '../types';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

export const apiClient = {
  // Scenario management
  async createScenario(scenario: ScenarioRequest): Promise<ScenarioResponse> {
    const response = await api.post('/scenario', scenario);
    return response.data;
  },

  async listScenarios(): Promise<any[]> {
    const response = await api.get('/scenarios');
    return response.data;
  },

  // Run management
  async createRun(request: RunRequest): Promise<RunResponse> {
    const response = await api.post('/run', request);
    return response.data;
  },

  async getRunStatus(runId: string): Promise<RunStatusResponse> {
    const response = await api.get(`/run/${runId}/status`);
    return response.data;
  },

  async getResults(runId: string): Promise<ResultsResponse> {
    const response = await api.get(`/run/${runId}/results`);
    return response.data;
  },

  // Network preview
  async previewNetwork(config: NetworkConfig): Promise<NetworkPreviewResponse> {
    const response = await api.post('/network/preview', config);
    return response.data;
  },

  // Export
  async exportResultsCSV(runId: string): Promise<Blob> {
    const response = await api.get(`/run/${runId}/export/csv`, {
      responseType: 'blob',
    });
    return response.data;
  },
};