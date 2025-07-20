import React from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { initializeWebLLMBridge } from './services/webllmBridgeService';
import { getWebLLMService } from './services/webllmService';
import Chat from './components/Chat/Chat';
import { NotificationProvider } from './components/UI/NotificationSystem';

// Error Boundary Component
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('App Error Boundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
            <h2 className="text-xl font-bold text-red-600 mb-4">Application Error</h2>
            <p className="text-gray-700 mb-4">Something went wrong. Please check the console for details.</p>
            <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">
              {this.state.error?.toString()}
            </pre>
            <button 
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Reload App
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Create a query client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  // Initialize WebLLM model when app starts (bridge service disabled to avoid duplicate requests)
  React.useEffect(() => {
    console.log('🚀 Initializing WebLLM Service...');
    try {
      // DISABLED: Bridge service to avoid duplicate chat requests
      // const bridgeService = initializeWebLLMBridge();
      // console.log('✅ WebLLM Bridge Service initialized successfully');
      
      // Initialize WebLLM model in background
      const initWebLLMInBackground = async () => {
        try {
          console.log('🤖 Initializing WebLLM model in background...');
          const webllmService = getWebLLMService((progress) => {
            if (progress.progress === 1) {
              console.log(`✅ WebLLM initialization complete: ${progress.text}`);
            }
          });
          
          if (!webllmService.isModelReady()) {
            await webllmService.initialize();
            console.log('✅ WebLLM model initialized successfully in background');
          }
        } catch (error) {
          console.error('❌ Failed to initialize WebLLM model in background:', error);
        }
      };
      
      // Initialize WebLLM in background (non-blocking)
      initWebLLMInBackground();
      
      // Cleanup on unmount - no bridge service to clean up
      return () => {
        console.log('🧹 App cleanup complete');
      };
    } catch (error) {
      console.error('❌ Failed to initialize WebLLM Service:', error);
    }
  }, []);

  console.log('🚀 Rendering main app content');

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <NotificationProvider>
          <Chat />
        </NotificationProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App; 