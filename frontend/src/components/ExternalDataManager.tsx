import React, { useState, useEffect } from 'react';
import {
  Database,
  Upload,
  Settings,
  CheckCircle,
  AlertCircle,
  XCircle,
  RefreshCw,
  Key,
  FileText,
  BarChart3,
  Cloud,
  Upload as UploadIcon
} from 'lucide-react';

interface DataSource {
  type: string;
  status: 'connected' | 'error' | 'disabled' | 'rate_limited';
  last_sync: string | null;
  error_message: string | null;
  records_count: number;
  data_freshness: string | null;
}

interface ExternalDataStatus {
  summary: {
    total_sources: number;
    connected_sources: number;
    error_sources: number;
    disabled_sources: number;
    connection_rate: number;
    latest_sync: string | null;
    total_records: number;
  };
  sources: DataSource[];
  recommendations: string[];
}

interface APIConfig {
  source_type: string;
  api_key?: string;
  api_secret?: string;
  access_token?: string;
  enabled: boolean;
}

const ExternalDataManager: React.FC = () => {
  const [status, setStatus] = useState<ExternalDataStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedSource, setSelectedSource] = useState<string | null>(null);
  const [showConfig, setShowConfig] = useState(false);
  const [configData, setConfigData] = useState<APIConfig>({
    source_type: '',
    enabled: false
  });
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadResult, setUploadResult] = useState<any>(null);

  useEffect(() => {
    fetchExternalDataStatus();
  }, []);

  const fetchExternalDataStatus = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/external-data/status');
      const data = await response.json();
      setStatus(data);
    } catch (error) {
      console.error('Failed to fetch external data status:', error);
    } finally {
      setLoading(false);
    }
  };

  const testConnection = async (sourceType: string) => {
    try {
      const response = await fetch('/api/external-data/test-connection', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ source_type: sourceType }),
      });
      const result = await response.json();
      
      // Refresh status after test
      await fetchExternalDataStatus();
      
      return result;
    } catch (error) {
      console.error('Connection test failed:', error);
    }
  };

  const updateConfiguration = async () => {
    try {
      const response = await fetch('/api/external-data/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          source_type: configData.source_type,
          config: configData,
        }),
      });
      
      if (response.ok) {
        setShowConfig(false);
        await fetchExternalDataStatus();
      }
    } catch (error) {
      console.error('Failed to update configuration:', error);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/external-data/upload', {
        method: 'POST',
        body: formData,
      });
      
      const result = await response.json();
      setUploadResult(result);
      setUploadedFile(file);
      
      // Refresh status
      await fetchExternalDataStatus();
    } catch (error) {
      console.error('File upload failed:', error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'rate_limited':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      default:
        return <XCircle className="w-5 h-5 text-gray-400" />;
    }
  };

  const getSourceTypeIcon = (type: string) => {
    switch (type) {
      case 'twitter_api':
      case 'facebook_api':
      case 'instagram_api':
        return <Cloud className="w-5 h-5 text-blue-500" />;
      case 'csv_file':
      case 'excel_file':
        return <FileText className="w-5 h-5 text-green-500" />;
      case 'demo_data':
        return <BarChart3 className="w-5 h-5 text-purple-500" />;
      default:
        return <Database className="w-5 h-5 text-gray-500" />;
    }
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <RefreshCw className="w-6 h-6 animate-spin text-blue-500" />
        <span className="ml-2">Loading external data status...</span>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="p-6">
        <div className="text-red-500">Failed to load external data status</div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">外部データ管理</h1>
        <p className="text-gray-600">外部APIとファイルアップロードによるデータ連携の管理</p>
      </div>

      {/* Summary Card */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="flex items-center">
            <Database className="w-8 h-8 text-blue-500" />
            <div className="ml-3">
              <p className="text-sm text-gray-600">データソース</p>
              <p className="text-xl font-semibold">{status.summary.total_sources}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="flex items-center">
            <CheckCircle className="w-8 h-8 text-green-500" />
            <div className="ml-3">
              <p className="text-sm text-gray-600">接続済み</p>
              <p className="text-xl font-semibold">{status.summary.connected_sources}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="flex items-center">
            <BarChart3 className="w-8 h-8 text-purple-500" />
            <div className="ml-3">
              <p className="text-sm text-gray-600">総レコード数</p>
              <p className="text-xl font-semibold">{status.summary.total_records.toLocaleString()}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="flex items-center">
            <RefreshCw className="w-8 h-8 text-indigo-500" />
            <div className="ml-3">
              <p className="text-sm text-gray-600">接続率</p>
              <p className="text-xl font-semibold">{(status.summary.connection_rate * 100).toFixed(0)}%</p>
            </div>
          </div>
        </div>
      </div>

      {/* File Upload Section */}
      <div className="bg-white p-6 rounded-lg shadow border mb-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center">
          <UploadIcon className="w-5 h-5 mr-2" />
          ファイルアップロード
        </h2>
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
          <input
            type="file"
            accept=".csv,.xlsx,.xls,.json"
            onChange={handleFileUpload}
            className="hidden"
            id="file-upload"
          />
          <label
            htmlFor="file-upload"
            className="cursor-pointer inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Upload className="w-4 h-4 mr-2" />
            ファイルを選択
          </label>
          <p className="text-sm text-gray-600 mt-2">
            CSV, Excel, JSONファイルに対応
          </p>
        </div>
        
        {uploadResult && (
          <div className="mt-4 p-4 bg-green-50 rounded-lg">
            <h3 className="font-medium text-green-800">アップロード完了</h3>
            <p className="text-sm text-green-700">
              ファイル: {uploadResult.file_info?.filename} ({uploadResult.file_info?.size} bytes)
            </p>
            {uploadResult.upload_result?.analysis && (
              <p className="text-sm text-green-700">
                {uploadResult.upload_result.analysis.rows}行, {uploadResult.upload_result.analysis.columns?.length}列
              </p>
            )}
          </div>
        )}
      </div>

      {/* Data Sources List */}
      <div className="bg-white rounded-lg shadow border">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">データソース一覧</h2>
            <button
              onClick={fetchExternalDataStatus}
              className="inline-flex items-center px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              更新
            </button>
          </div>
        </div>

        <div className="divide-y divide-gray-200">
          {status.sources.map((source) => (
            <div key={source.type} className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  {getSourceTypeIcon(source.type)}
                  {getStatusIcon(source.status)}
                  <div>
                    <h3 className="font-medium text-gray-900">
                      {source.type.replace('_', ' ').toUpperCase()}
                    </h3>
                    <p className="text-sm text-gray-600">
                      ステータス: {source.status} | レコード数: {source.records_count}
                    </p>
                    {source.last_sync && (
                      <p className="text-xs text-gray-500">
                        最終同期: {new Date(source.last_sync).toLocaleString('ja-JP')}
                      </p>
                    )}
                    {source.error_message && (
                      <p className="text-xs text-red-600">
                        エラー: {source.error_message}
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => testConnection(source.type)}
                    className="inline-flex items-center px-3 py-2 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    テスト
                  </button>
                  
                  <button
                    onClick={() => {
                      setSelectedSource(source.type);
                      setConfigData({
                        source_type: source.type,
                        enabled: source.status !== 'disabled'
                      });
                      setShowConfig(true);
                    }}
                    className="inline-flex items-center px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    <Settings className="w-4 h-4 mr-2" />
                    設定
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recommendations */}
      {status.recommendations.length > 0 && (
        <div className="mt-6 bg-blue-50 p-4 rounded-lg border border-blue-200">
          <h3 className="font-medium text-blue-900 mb-2">推奨事項</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            {status.recommendations.map((rec, index) => (
              <li key={index}>• {rec}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Configuration Modal */}
      {showConfig && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">
              {selectedSource?.replace('_', ' ').toUpperCase()} 設定
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={configData.enabled}
                    onChange={(e) => setConfigData({
                      ...configData,
                      enabled: e.target.checked
                    })}
                    className="mr-2"
                  />
                  有効にする
                </label>
              </div>

              {selectedSource?.includes('api') && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      API Key
                    </label>
                    <input
                      type="password"
                      value={configData.api_key || ''}
                      onChange={(e) => setConfigData({
                        ...configData,
                        api_key: e.target.value
                      })}
                      className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="APIキーを入力"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      API Secret
                    </label>
                    <input
                      type="password"
                      value={configData.api_secret || ''}
                      onChange={(e) => setConfigData({
                        ...configData,
                        api_secret: e.target.value
                      })}
                      className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="APIシークレットを入力"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Access Token
                    </label>
                    <input
                      type="password"
                      value={configData.access_token || ''}
                      onChange={(e) => setConfigData({
                        ...configData,
                        access_token: e.target.value
                      })}
                      className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="アクセストークンを入力"
                    />
                  </div>
                </>
              )}
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowConfig(false)}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                キャンセル
              </button>
              <button
                onClick={updateConfiguration}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                保存
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExternalDataManager;