import React, { useEffect, useRef, useState } from 'react';
import styled from 'styled-components';
import ReactMarkdown from 'react-markdown';
import { 
  PaperAirplaneIcon,
  UserIcon,
  CpuChipIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline';
import { useNotifications } from '../UI/NotificationSystem';
import { ApiService } from '../../services/api';
import { getWebLLMService } from '../../services/webllmService';
import { getWebLLMBridgeService } from '../../services/webllmBridgeService';

const Container = styled.div<{ isProcessing?: boolean }>`
  background: #FFFFFF;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  
  /* Mobile first - account for top bar height */
  flex: 1;
  width: 100%;
  height: calc(100vh - 60px);
  min-height: calc(100vh - 60px);
  
  /* Tablet and up - adjust for larger top bar */
  @media (min-width: 768px) {
    height: calc(100vh - 70px);
    min-height: calc(100vh - 70px);
  }
  
  /* Desktop and up - adjust for largest top bar */
  @media (min-width: 1024px) {
    height: calc(100vh - 80px);
    min-height: calc(100vh - 80px);
  }

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #8F4ACF, #7C3AED, #6366F1);
    transform: translateX(-100%);
    opacity: ${props => props.isProcessing ? 1 : 0};
    transition: opacity 0.3s ease;
    animation: ${props => props.isProcessing ? 'slide-progress 2s ease-in-out infinite' : 'none'};
    z-index: 10;
  }

  @keyframes slide-progress {
    0% {
      transform: translateX(-100%);
    }
    50% {
      transform: translateX(0%);
    }
    100% {
      transform: translateX(100%);
    }
  }
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: #F7F7FF;
    border-radius: 8px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #ECEAFF;
    border-radius: 8px;
    
    &:hover {
      background: #8F4ACF;
    }
  }
`;

const Message = styled.div<{ isUser?: boolean }>`
  display: flex;
  align-items: flex-start;
  margin-bottom: 24px;
  gap: 12px;
  
  ${props => props.isUser && `
    flex-direction: row-reverse;
  `}
`;

const MessageIcon = styled.div<{ isUser?: boolean }>`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  
  ${props => props.isUser ? `
    background: #8F4ACF;
    color: white;
  ` : `
    background: #F3F4F6;
    color: #6B7280;
  `}
`;

const MessageContent = styled.div<{ isUser?: boolean }>`
  flex: 1;
  background: ${props => props.isUser ? '#8F4ACF' : '#F8F9FA'};
  color: ${props => props.isUser ? 'white' : '#1F2937'};
  padding: 16px;
  border-radius: 16px;
  max-width: 80%;
  
  ${props => props.isUser ? `
    border-bottom-right-radius: 4px;
  ` : `
    border-bottom-left-radius: 4px;
  `}
  
  p {
    margin: 0 0 8px 0;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  pre {
    background: ${props => props.isUser ? 'rgba(255, 255, 255, 0.1)' : '#F1F5F9'};
    padding: 12px;
    border-radius: 8px;
    overflow-x: auto;
    font-size: 14px;
    margin: 8px 0;
  }
  
  code {
    background: ${props => props.isUser ? 'rgba(255, 255, 255, 0.1)' : '#F1F5F9'};
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 14px;
  }
`;

const InputContainer = styled.div`
  padding: 20px;
  border-top: 1px solid #E5E7EB;
  background: #FFFFFF;
`;

const InputWrapper = styled.div`
  display: flex;
  gap: 12px;
  align-items: flex-end;
  max-width: 1200px;
  margin: 0 auto;
`;

const TextArea = styled.textarea`
  flex: 1;
  min-height: 44px;
  max-height: 120px;
  padding: 12px 16px;
  border: 2px solid #E5E7EB;
  border-radius: 12px;
  font-size: 16px;
  resize: none;
  outline: none;
  font-family: inherit;
  
  &:focus {
    border-color: #8F4ACF;
  }
  
  &::placeholder {
    color: #9CA3AF;
  }
`;

const SendButton = styled.button`
  width: 44px;
  height: 44px;
  background: #8F4ACF;
  color: white;
  border: none;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover:not(:disabled) {
    background: #7C3AED;
    transform: translateY(-1px);
  }
  
  &:disabled {
    background: #D1D5DB;
    cursor: not-allowed;
    transform: none;
  }
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: #6B7280;
  
  h3 {
    margin: 16px 0 8px 0;
    color: #1F2937;
  }
  
  p {
    margin: 0;
    max-width: 400px;
  }
`;

const LoadingDots = styled.div`
  display: flex;
  gap: 4px;
  align-items: center;
  
  span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #6B7280;
    animation: loading-dots 1.4s infinite ease-in-out;
    
    &:nth-child(1) { animation-delay: -0.32s; }
    &:nth-child(2) { animation-delay: -0.16s; }
    &:nth-child(3) { animation-delay: 0s; }
  }
  
  @keyframes loading-dots {
    0%, 80%, 100% {
      transform: scale(0);
    }
    40% {
      transform: scale(1);
    }
  }
`;

interface Message {
  id: string;
  message_type: 'user' | 'assistant' | 'system' | 'error';
  content: string;
  processing_time_ms?: number;
  tokens_used?: number;
  metadata?: any;
  created_at: string;
}

interface ChatSession {
  id: string;
  title: string;
  message_count: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_message_preview: string;
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isBotTyping, setIsBotTyping] = useState(false);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [selectedModel, setSelectedModel] = useState('Llama-3.2-1B-Instruct');
  const [isModelSwitching, setIsModelSwitching] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { showError, showSuccess } = useNotifications();
  const webllmService = getWebLLMService();
  const bridgeService = getWebLLMBridgeService();
  
  // Get available models from WebLLM service
  const modelOptions = webllmService.getAvailableModels();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Create a new session when component mounts
    createNewSession();
  }, []);

  const createNewSession = async () => {
    try {
      const response = await ApiService.post('/chat/sessions/create/', {
        title: 'New Chat Session'
      });
      
      if (response.success) {
        setCurrentSession(response.session);
        setMessages([]);
      } else {
        showError(response.error || 'Failed to create chat session');
      }
    } catch (error) {
      console.error('Error creating session:', error);
      showError('Failed to create chat session');
    }
  };

  const handleModelChange = async (newModel: string) => {
    if (newModel === selectedModel || isModelSwitching) return;
    
    setIsModelSwitching(true);
    console.log(`🔄 User selected model: ${newModel}`);
    
    try {
      // Switch the WebLLM model
      await webllmService.switchModel(newModel);
      setSelectedModel(newModel);
      showSuccess(`Switched to model: ${newModel}`);
      console.log(`✅ Successfully switched to model: ${newModel}`);
    } catch (error) {
      console.error('❌ Error switching model:', error);
      showError(`Failed to switch to model ${newModel}: ${error instanceof Error ? error.message : 'Unknown error'}`);
      
      // Reset to previous working model if switch failed
      const currentModel = webllmService.getCurrentModel();
      if (currentModel !== selectedModel) {
        setSelectedModel(currentModel);
      }
    } finally {
      setIsModelSwitching(false);
    }
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || isProcessing || !currentSession) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    setIsProcessing(true);
    setIsBotTyping(true);

    // Create temporary user message
    const tempUserMessage: Message = {
      id: Date.now().toString(),
      message_type: 'user',
      content: userMessage,
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMessage]);

    try {
      // First, save the user message to the session via backend
      await ApiService.post(`/chat/sessions/${currentSession.id}/send/`, {
        content: userMessage,
        message_type: 'user',
        metadata: {
          model: selectedModel
        }
      });

      // Create initial bot message
      let botMessage: Message = {
        id: (Date.now() + 1).toString(),
        message_type: 'assistant',
        content: '',
        created_at: new Date().toISOString(),
      };
      setMessages(prev => [...prev, botMessage]);

      // Use direct WebLLM service for real-time streaming with proper model
      console.log(`🔄 Starting WebLLM direct streaming with model: ${selectedModel}`);
      
      // Ensure WebLLM is initialized with the correct model
      if (!webllmService.isModelReady() || webllmService.getCurrentModel() !== selectedModel) {
        console.log(`⏳ Initializing WebLLM with model: ${selectedModel}`);
        await webllmService.switchModel(selectedModel);
      }

      // Send processing start notification to backend
      await ApiService.post('/webllm/processing/', {
        session_id: currentSession.id,
        user_message: userMessage,
        model: selectedModel,
        status: 'started'
      });

      let chunkCount = 0;
      const startTime = Date.now();

      // Generate response with real-time streaming
      const webllmResponse = await webllmService.generateDirectResponse(
        'You are a helpful AI assistant.',
        userMessage,
        selectedModel,
        async (chunk: string) => {
          botMessage.content += chunk;
          setMessages(prev => [...prev.slice(0, -1), { ...botMessage }]);
          
          chunkCount++;
          
          // Send chunk to backend every 5 chunks or if it's substantial content
          if (chunkCount % 5 === 0 || chunk.length > 10) {
            try {
              await ApiService.post('/webllm/processing/', {
                session_id: currentSession.id,
                model: selectedModel,
                status: 'streaming',
                chunk: chunk,
                chunk_count: chunkCount,
                partial_content: botMessage.content.substring(0, 200) + '...' // First 200 chars for monitoring
              });
            } catch (error) {
              console.warn('Failed to send chunk update to backend:', error);
            }
          }
        }
      );

      const processingTime = Date.now() - startTime;

      // Save the assistant response to the session via backend
      await ApiService.post(`/chat/sessions/${currentSession.id}/send/`, {
        content: botMessage.content,
        message_type: 'assistant',
        processing_time_ms: processingTime,
        tokens_used: webllmResponse.usage?.total_tokens || 0,
        metadata: {
          model: selectedModel,
          usage: webllmResponse.usage,
          chunks_processed: chunkCount,
          processing_time_ms: processingTime
        }
      });

      // Send completion notification to backend
      await ApiService.post('/webllm/processing/', {
        session_id: currentSession.id,
        model: selectedModel,
        status: 'completed',
        final_content: botMessage.content,
        processing_time_ms: processingTime,
        chunks_processed: chunkCount,
        usage: webllmResponse.usage
      });

      console.log(`✅ WebLLM streaming completed with model: ${selectedModel} (${chunkCount} chunks, ${processingTime}ms)`);

    } catch (error) {
      console.error('❌ Error sending message:', error);
      
      // Send error notification to backend
      try {
        await ApiService.post('/webllm/processing/', {
          session_id: currentSession.id,
          model: selectedModel,
          status: 'error',
          error_message: error instanceof Error ? error.message : 'Unknown error'
        });
      } catch (backendError) {
        console.warn('Failed to send error to backend:', backendError);
      }
      
      showError('Failed to send message: ' + (error instanceof Error ? error.message : 'Unknown error'));
      
      // Update bot message with error
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        message_type: 'error',
        content: 'Sorry, I encountered an error while processing your message. Please try again.',
        created_at: new Date().toISOString(),
      };
      setMessages(prev => [...prev.slice(0, -1), errorMessage]);
    } finally {
      setIsProcessing(false);
      setIsBotTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const renderMessage = (message: Message) => {
    const isUser = message.message_type === 'user';
    const isError = message.message_type === 'error';
    
    return (
      <Message key={message.id} isUser={isUser}>
        <MessageIcon isUser={isUser}>
          {isUser ? <UserIcon width={16} height={16} /> : <CpuChipIcon width={16} height={16} />}
        </MessageIcon>
        <MessageContent isUser={isUser}>
          <ReactMarkdown>
            {message.content}
          </ReactMarkdown>
          {message.processing_time_ms && (
            <div style={{ fontSize: '12px', opacity: 0.7, marginTop: '8px' }}>
              Processed in {message.processing_time_ms}ms
            </div>
          )}
        </MessageContent>
      </Message>
    );
  };

  return (
    <Container isProcessing={isProcessing}>
      <MessagesContainer>
        {messages.length === 0 ? (
          <EmptyState>
            <CpuChipIcon width={48} height={48} />
            <h3>Welcome to WebLLM Chat</h3>
            <p>Start a conversation with the local WebLLM model. Your messages are processed entirely on your device.</p>
          </EmptyState>
        ) : (
          messages.map(renderMessage)
        )}
        
        {isBotTyping && (
          <Message>
            <MessageIcon>
              <CpuChipIcon width={16} height={16} />
            </MessageIcon>
            <MessageContent>
              <LoadingDots>
                <span></span>
                <span></span>
                <span></span>
              </LoadingDots>
            </MessageContent>
          </Message>
        )}
        
        <div ref={messagesEndRef} />
      </MessagesContainer>
      
      <InputContainer>
        <div style={{ marginBottom: 12 }}>
          <label htmlFor="model-select" style={{ marginRight: 8 }}>Model:</label>
          <select
            id="model-select"
            value={selectedModel}
            onChange={e => handleModelChange(e.target.value)}
            style={{ 
              padding: '6px 12px', 
              borderRadius: 8, 
              border: '1px solid #E5E7EB', 
              fontSize: 16,
              opacity: isModelSwitching ? 0.6 : 1,
              cursor: isModelSwitching ? 'wait' : 'pointer'
            }}
            disabled={isProcessing || isModelSwitching}
          >
            {modelOptions.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
          {isModelSwitching && (
            <span style={{ marginLeft: 8, fontSize: 14, color: '#8F4ACF' }}>
              Loading model...
            </span>
          )}
        </div>
        <InputWrapper>
          <TextArea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={`Type your message... (Model: ${selectedModel})`}
            disabled={isProcessing || isModelSwitching}
          />
          <SendButton onClick={sendMessage} disabled={isProcessing || !inputValue.trim() || isModelSwitching}>
            {isProcessing ? (
              <ArrowPathIcon width={20} height={20} className="animate-spin" />
            ) : (
              <PaperAirplaneIcon width={20} height={20} />
            )}
          </SendButton>
        </InputWrapper>
      </InputContainer>
    </Container>
  );
};

export default Chat;