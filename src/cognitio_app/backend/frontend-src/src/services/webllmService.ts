import { CreateMLCEngine, MLCEngineInterface } from "@mlc-ai/web-llm";
import { config } from '../config';

export interface WebLLMMessage {
  role: "system" | "user" | "assistant";
  content: string;
}

export interface WebLLMResponse {
  content: string;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

export class WebLLMService {
  private engine: MLCEngineInterface | null = null;
  private isInitializing = false;
  private isReady = false;
  private modelName = "Llama-3.2-1B-Instruct-q4f16_1-MLC";
  private allowedModels = [
    "Llama-3.2-1B-Instruct-q4f16_1-MLC",
    "Llama-3.2-3B-Instruct-q4f16_1-MLC", 
    "Phi-3.5-mini-instruct-q4f16_1-MLC",
    "Qwen2.5-0.5B-Instruct-q4f16_1-MLC",
    "Qwen2.5-1.5B-Instruct-q4f16_1-MLC"
  ];
  private modelDisplayNames = {
    "Llama-3.2-1B-Instruct-q4f16_1-MLC": "Llama-3.2-1B-Instruct",
    "Llama-3.2-3B-Instruct-q4f16_1-MLC": "Llama-3.2-3B-Instruct",
    "Phi-3.5-mini-instruct-q4f16_1-MLC": "Phi-3.5-mini-instruct",
    "Qwen2.5-0.5B-Instruct-q4f16_1-MLC": "Qwen2.5-0.5B-Instruct",
    "Qwen2.5-1.5B-Instruct-q4f16_1-MLC": "Qwen2.5-1.5B-Instruct"
  };
  private initializationPromise: Promise<void> | null = null;
  private progressCallback: ((progress: { text: string; progress: number }) => void) | null = null;

  constructor(progressCallback?: (progress: { text: string; progress: number }) => void) {
    this.progressCallback = progressCallback || null;
    // Auto-initialize on construction
    this.initialize().catch(error => {
      console.error("Failed to auto-initialize WebLLM:", error);
    });
  }

  /**
   * Switch to a different model
   */
  async switchModel(modelName: string): Promise<void> {
    // Convert display name to full model name
    const fullModelName = this.getFullModelName(modelName);
    
    if (!this.allowedModels.includes(fullModelName)) {
      const availableModels = Object.values(this.modelDisplayNames).join(', ');
      throw new Error(`Model ${modelName} is not available. Available models: ${availableModels}`);
    }

    if (this.modelName === fullModelName && this.isReady) {
      console.log(`Model ${fullModelName} is already loaded and ready`);
      return;
    }

    console.log(`🔄 Switching from ${this.modelName} to ${fullModelName}`);
    
    // Clean up current engine
    await this.cleanup();
    
    // Set new model and reinitialize
    this.modelName = fullModelName;
    await this.initialize();
  }

  /**
   * Get the full model name from display name
   */
  private getFullModelName(displayName: string): string {
    // If it's already a full name, return it
    if (displayName.includes('-q4f16_1-MLC')) {
      return displayName;
    }
    
    // Find the full name from display name
    for (const [fullName, display] of Object.entries(this.modelDisplayNames)) {
      if (display === displayName) {
        return fullName;
      }
    }
    
    // Default fallback
    return `${displayName}-q4f16_1-MLC`;
  }

  /**
   * Get the current model name (display name for UI)
   */
  getCurrentModel(): string {
    return this.modelDisplayNames[this.modelName as keyof typeof this.modelDisplayNames] || 
           this.modelName.replace('-q4f16_1-MLC', '');
  }

  /**
   * Get available models for UI
   */
  getAvailableModels(): Array<{value: string, label: string}> {
    return Object.entries(this.modelDisplayNames).map(([fullName, displayName]) => ({
      value: displayName,
      label: displayName
    }));
  }

  /**
   * Initialize the WebLLM engine with the specified model
   */
  async initialize(): Promise<void> {
    if (this.isReady) {
      return;
    }

    if (this.isInitializing && this.initializationPromise) {
      return this.initializationPromise;
    }

    this.isInitializing = true;
    this.initializationPromise = this.doInitialize();
    
    try {
      await this.initializationPromise;
    } finally {
      this.isInitializing = false;
    }
  }

  private async doInitialize(): Promise<void> {
    try {
      console.log("🚀 Initializing WebLLM with model:", this.modelName);
      
      this.engine = await CreateMLCEngine(
        this.modelName,
        {
          initProgressCallback: (progress: { text: string; progress: number }) => {
            console.log(`WebLLM Init: ${progress.text} (${Math.round(progress.progress * 100)}%)`);
            if (this.progressCallback) {
              this.progressCallback({
                text: progress.text,
                progress: progress.progress || 0
              });
            }
          }
        }
      );

      this.isReady = true;
      console.log("✅ WebLLM initialized successfully");
    } catch (error) {
      console.error("❌ Failed to initialize WebLLM:", error);
      this.isReady = false;
      this.engine = null;
      throw error;
    }
  }

  /**
   * Check if the WebLLM engine is ready
   */
  isModelReady(): boolean {
    return this.isReady && this.engine !== null;
  }

  /**
   * Get the initialization status
   */
  getStatus(): { isInitializing: boolean; isReady: boolean } {
    return {
      isInitializing: this.isInitializing,
      isReady: this.isReady
    };
  }

  /**
   * Generate a response using the WebLLM model
   */
  async generateInsight(systemPrompt: string, userQuestion: string, model?: string): Promise<WebLLMResponse> {
    // Switch model if requested
    if (model && model !== this.getCurrentModel()) {
      await this.switchModel(model);
    }

    if (!this.isModelReady()) {
      throw new Error("WebLLM engine is not ready. Please initialize first.");
    }

    try {
      const response = await fetch('/api/v1/webllm/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCookie('csrftoken')
        },
        body: JSON.stringify({
          system_prompt: systemPrompt,
          content: userQuestion,
          model: this.getCurrentModel(),
          temperature: 0.7,
          max_tokens: 4096,
          stream: false
        })
      });

      if (!response.ok) {
        throw new Error(`Backend request failed: ${response.statusText}`);
      }

      const result = await response.json();
      
      // Log the chat message to backend
      await this.logChatMessage({
        role: "user",
        content: userQuestion,
        model: this.modelName
      });

      if (result.content) {
        await this.logChatMessage({
          role: "assistant",
          content: result.content,
          model: this.modelName
        });
      }

      return {
        content: result.content,
        usage: result.usage
      };
    } catch (error) {
      console.error("Error generating insight with WebLLM:", error);
      throw error;
    }
  }

  /**
   * Generate a streaming response using the WebLLM model
   */
  async generateInsightStream(
    systemPrompt: string, 
    userQuestion: string,
    onChunk: (chunk: string) => void
  ): Promise<WebLLMResponse> {
    if (!this.isModelReady()) {
      throw new Error("WebLLM engine is not ready. Please initialize first.");
    }

    try {
      // Log user message first
      await this.logChatMessage({
        role: "user",
        content: userQuestion,
        model: this.modelName
      });

      // Start streaming request
      const response = await fetch('/api/v1/webllm/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCookie('csrftoken')
        },
        body: JSON.stringify({
          system_prompt: systemPrompt,
          content: userQuestion,
          model: this.modelName,
          temperature: 0.7,
          max_tokens: 4096,
          stream: true
        })
      });

      if (!response.ok) {
        throw new Error(`Backend request failed: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error("Stream not available");
      }

      let fullContent = "";
      let finalUsage: any = null;
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        try {
          const data = JSON.parse(chunk);
          if (data.delta) {
            fullContent += data.delta;
            onChunk(data.delta);
          }
          if (data.usage) {
            finalUsage = data.usage;
          }
        } catch (e) {
          console.warn("Failed to parse chunk:", e);
        }
      }

      // Log assistant's complete response
      await this.logChatMessage({
        role: "assistant",
        content: fullContent,
        model: this.modelName
      });

      return {
        content: fullContent,
        usage: finalUsage ? {
          prompt_tokens: finalUsage.prompt_tokens,
          completion_tokens: finalUsage.completion_tokens,
          total_tokens: finalUsage.total_tokens
        } : undefined
      };
    } catch (error) {
      console.error("Error generating streaming insight with WebLLM:", error);
      throw error;
    }
  }

  /**
   * Generate a response using WebLLM engine directly (for bridge service)
   */
  async generateDirectResponse(
    systemPrompt: string,
    userMessage: string,
    model?: string,
    onChunk?: (chunk: string) => void
  ): Promise<WebLLMResponse> {
    // Switch model if requested
    if (model && model !== this.getCurrentModel()) {
      console.log(`🔄 Switching to model: ${model}`);
      await this.switchModel(model);
    }

    // Ensure WebLLM is initialized
    if (!this.isReady) {
      console.log("WebLLM not ready, initializing...");
      await this.initialize();
    }

    if (!this.isModelReady()) {
      throw new Error("WebLLM engine is not ready. Please wait for initialization to complete.");
    }

    try {
      const messages = [
        { role: "system" as const, content: systemPrompt },
        { role: "user" as const, content: userMessage }
      ];

      let fullContent = '';
      let totalTokens = 0;
      let promptTokens = 0;
      let completionTokens = 0;

      console.log(`🔄 Starting WebLLM chat completion with model: ${this.getCurrentModel()}`);

      const completion = await this.engine!.chat.completions.create({
        messages: messages,
        temperature: 0.7,
        max_tokens: 4096,
        stream: true
      });

      for await (const chunk of completion) {
        const delta = chunk.choices[0]?.delta?.content || '';
        if (delta) {
          fullContent += delta;
          if (onChunk) {
            onChunk(delta);
          }
        }
        
        if (chunk.usage) {
          totalTokens = chunk.usage.total_tokens || 0;
          promptTokens = chunk.usage.prompt_tokens || 0;
          completionTokens = chunk.usage.completion_tokens || 0;
        }
      }

      console.log(`✅ WebLLM completion finished: ${fullContent.length} chars with model ${this.getCurrentModel()}`);

      return {
        content: fullContent,
        usage: {
          prompt_tokens: promptTokens,
          completion_tokens: completionTokens,
          total_tokens: totalTokens
        }
      };
    } catch (error) {
      console.error("❌ Error generating direct WebLLM response:", error);
      throw error;
    }
  }

  /**
   * Call the backend endpoint with WebLLM-generated content
   */
  async callBackendEndpoint(content: string): Promise<any> {
    try {
      const response = await fetch('/api/v1/webllm/insights/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCookie('csrftoken')
        },
        body: JSON.stringify({
          content: content,
          model: this.modelName,
          timestamp: new Date().toISOString()
        })
      });

      if (!response.ok) {
        throw new Error(`Backend request failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Error calling backend endpoint:", error);
      throw error;
    }
  }

  /**
   * Utility method to get CSRF token from cookies
   */
  private getCookie(name: string): string {
    let cookieValue = '';
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  /**
   * Log a chat message to the backend
   */
  private async logChatMessage(message: {
    role: "system" | "user" | "assistant";
    content: string;
    model: string;
  }): Promise<void> {
    try {
      const response = await fetch('/api/v1/webllm/webllm-local-log/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCookie('csrftoken')
        },
        body: JSON.stringify({
          role: message.role,
          content: message.content,
          model: message.model,
          timestamp: new Date().toISOString()
        })
      });

      if (!response.ok) {
        console.error("Failed to log chat message:", response.statusText);
      }
    } catch (error) {
      console.error("Error logging chat message:", error);
    }
  }

  /**
   * Clean up resources
   */
  async cleanup(): Promise<void> {
    if (this.engine) {
      console.log("🧹 Cleaning up WebLLM engine");
      // Note: As of current version, there's no explicit cleanup method
      // The engine will be garbage collected when no longer referenced
      this.engine = null;
    }
    this.isReady = false;
    this.isInitializing = false;
    this.initializationPromise = null;
  }

  public async interrupt() {
    if (this.engine) {
      try {
        await fetch('/api/v1/webllm/interrupt/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCookie('csrftoken')
          }
        });
      } catch (error) {
        console.error("Error interrupting WebLLM:", error);
      }
    }
  }
}

// Global instance
let webLLMService: WebLLMService | null = null;

/**
 * Get the global WebLLM service instance
 */
export function getWebLLMService(progressCallback?: (progress: { text: string; progress: number }) => void): WebLLMService {
  if (!webLLMService) {
    webLLMService = new WebLLMService(progressCallback);
  }
  return webLLMService;
}

/**
 * Initialize WebLLM service on app startup
 */
export async function initializeWebLLMService(progressCallback?: (progress: { text: string; progress: number }) => void): Promise<WebLLMService> {
  console.log("🚀 Initializing WebLLM Service...");
  const service = getWebLLMService(progressCallback);
  await service.initialize();
  console.log("✅ WebLLM Service initialized");
  return service;
}