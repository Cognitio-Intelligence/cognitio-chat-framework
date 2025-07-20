import { getWebLLMService, WebLLMResponse } from './webllmService';

interface WebLLMSubmitResponse {
  request_id: string;
  content?: string;
  error?: string;
  usage?: WebLLMResponse['usage'];
  done?: boolean;
}

export class WebLLMBridgeService {
  private webllmInitialized = false;

  constructor() {
    this.initializeWebLLM();
  }

  private async initializeWebLLM(): Promise<void> {
    try {
      console.log("🔄 Initializing WebLLM for bridge service...");
      const webllmService = getWebLLMService((progress) => {
        console.log(`WebLLM Bridge Init: ${progress.text} (${Math.round(progress.progress * 100)}%)`);
      });
      
      await webllmService.initialize();
      this.webllmInitialized = true;
      console.log("✅ WebLLM initialized for bridge service");
    } catch (error) {
      console.error("❌ Failed to initialize WebLLM for bridge:", error);
      this.webllmInitialized = false;
      // Retry after 5 seconds
      setTimeout(() => {
        this.initializeWebLLM();
      }, 5000);
    }
  }

  public getStatus(): { isInitialized: boolean } {
    return {
      isInitialized: this.webllmInitialized,
    };
  }

  public async chat(prompt: string, modelId: string): Promise<WebLLMResponse> {
    // Ensure WebLLM is initialized
    if (!this.webllmInitialized) {
      await this.initializeWebLLM();
    }

    const webllmService = getWebLLMService();
    
    // Switch model if different from current
    if (webllmService.getCurrentModel() !== modelId) {
      console.log(`🔄 Bridge switching to model: ${modelId}`);
      await webllmService.switchModel(modelId);
    }
    
    if (!webllmService.isModelReady()) {
      await webllmService.initialize();
      if (!webllmService.isModelReady()) {
        throw new Error('WebLLM model is not ready. Please wait for initialization to complete.');
      }
    }

    // Use generateDirectResponse for immediate response
    const response = await webllmService.generateDirectResponse(
      'You are a helpful AI assistant.',
      prompt,
      modelId
    );
    return response;
  }

  public async interrupt(): Promise<void> {
    const webllmService = getWebLLMService();
    await webllmService.interrupt();
  }
}

let bridgeServiceInstance: WebLLMBridgeService | null = null;

export function getWebLLMBridgeService(): WebLLMBridgeService {
  if (!bridgeServiceInstance) {
    bridgeServiceInstance = new WebLLMBridgeService();
  }
  return bridgeServiceInstance;
}

export function initializeWebLLMBridge(): WebLLMBridgeService {
  console.log('🚀 Initializing WebLLM Bridge Service...');
  const service = getWebLLMBridgeService();
  console.log('✅ WebLLM Bridge Service initialized');
  return service;
}