import React, { useEffect, useRef, useState } from 'react';
import { Network } from 'vis-network/standalone/esm/vis-network';
import { NetworkConfig } from '../types';
import { apiClient } from '../api/client';

interface Props {
  networkConfig: NetworkConfig;
}

export const NetworkPreview: React.FC<Props> = ({ networkConfig }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const networkRef = useRef<Network | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadNetworkPreview = async () => {
      if (!containerRef.current) return;

      setIsLoading(true);
      setError(null);

      try {
        const preview = await apiClient.previewNetwork(networkConfig);
        
        // Clean up existing network
        if (networkRef.current) {
          networkRef.current.destroy();
        }

        // Create new network
        const data = {
          nodes: preview.nodes,
          edges: preview.edges,
        };

        const options = {
          nodes: {
            shape: 'dot',
            size: 8,
            font: {
              size: 10,
              color: '#333',
            },
            borderWidth: 1,
            color: {
              border: '#333',
            },
          },
          edges: {
            width: 1,
            color: '#848484',
            smooth: {
              enabled: true,
              type: 'continuous',
              roundness: 0.5,
            },
          },
          layout: {
            improvedLayout: false,
          },
          physics: {
            enabled: true,
            stabilization: { iterations: 100 },
            barnesHut: {
              gravitationalConstant: -2000,
              centralGravity: 0.3,
              springLength: 95,
              springConstant: 0.04,
              damping: 0.09,
            },
          },
          interaction: {
            dragNodes: true,
            dragView: true,
            zoomView: true,
          },
        };

        networkRef.current = new Network(containerRef.current, data, options);
        
        // Auto-fit after stabilization
        networkRef.current.once('stabilizationIterationsDone', () => {
          networkRef.current?.fit();
        });

      } catch (err) {
        setError('Failed to load network preview');
        console.error('Network preview error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadNetworkPreview();

    // Cleanup
    return () => {
      if (networkRef.current) {
        networkRef.current.destroy();
        networkRef.current = null;
      }
    };
  }, [networkConfig]);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Network Preview</h2>
        <div className="text-sm text-gray-500">
          {networkConfig.n.toLocaleString()} nodes, avg degree {networkConfig.k}
        </div>
      </div>

      <div className="bg-gray-50 rounded-lg border-2 border-dashed border-gray-200 relative">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75 z-10 rounded-lg">
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              <span className="text-gray-600">Generating network preview...</span>
            </div>
          </div>
        )}

        {error && (
          <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75 z-10 rounded-lg">
            <div className="text-center">
              <div className="text-red-600 font-medium">{error}</div>
              <button
                onClick={() => window.location.reload()}
                className="mt-2 text-blue-600 hover:text-blue-800"
              >
                Retry
              </button>
            </div>
          </div>
        )}

        <div
          ref={containerRef}
          className="w-full h-96 rounded-lg"
          style={{ minHeight: '24rem' }}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="font-medium text-blue-900">Network Type</div>
          <div className="text-blue-700">
            {networkConfig.type === 'er' && 'Erdős-Rényi'}
            {networkConfig.type === 'ws' && 'Watts-Strogatz'}  
            {networkConfig.type === 'ba' && 'Barabási-Albert'}
          </div>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="font-medium text-green-900">Scale</div>
          <div className="text-green-700">
            {networkConfig.n >= 1000 
              ? `${(networkConfig.n / 1000).toFixed(1)}K nodes`
              : `${networkConfig.n} nodes`
            }
          </div>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg">
          <div className="font-medium text-purple-900">Connectivity</div>
          <div className="text-purple-700">
            Avg degree: {networkConfig.k}
            {networkConfig.type === 'ws' && networkConfig.beta && (
              <div>β: {networkConfig.beta}</div>
            )}
          </div>
        </div>
      </div>

      <div className="text-xs text-gray-500">
        Preview shows a sample of the network structure for visualization purposes. 
        Large networks are downsampled to maintain performance.
      </div>
    </div>
  );
};