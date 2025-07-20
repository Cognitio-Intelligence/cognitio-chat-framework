# Cognitio Chat Framework

A privacy-first desktop chat application framework built with Django, React, and WebLLM. This framework provides a complete foundation for building local AI chat applications with modern web technologies and cross-platform desktop packaging via BeeWare.

## ⚠️ Development Disclaimer

This project was developed with assistance from AI-powered coding tools ("vibe coding"). While the codebase has been thoroughly tested and reviewed, users should:

- **Review all code** before using in production environments
- **Test thoroughly** on their specific hardware and software configurations
- **Understand the implications** of running local AI models on their systems
- **Be aware** that AI-assisted development may introduce patterns or approaches that require human validation
- **Consider security implications** when deploying in sensitive environments

The developers recommend a thorough code review and testing process before any production deployment.

## 📋 Project Summary

**Cognitio Chat Framework** is a complete desktop application framework that enables privacy-focused AI chat experiences. Key highlights:

- **🔒 Privacy-First**: All AI processing happens locally on your device - no data transmission to external servers
- **🖥️ Cross-Platform Desktop**: Native desktop applications for macOS, Windows, and Linux via BeeWare/Briefcase
- **⚡ Modern Architecture**: Django REST API backend paired with React TypeScript frontend
- **🤖 Multiple AI Models**: Support for various WebLLM models (Llama, Phi, Qwen) with on-the-fly switching
- **📊 Real-Time Monitoring**: Backend performance tracking and analytics for WebLLM processing
- **🎨 Responsive UI**: Clean, modern chat interface with streaming responses
- **🔧 Developer-Friendly**: Comprehensive setup guides, code protection features, and customization options
- **📦 Distribution Ready**: Built-in code protection script for secure deployment

The framework is designed for developers who want to create local AI chat applications without compromising user privacy or requiring internet connectivity for AI processing.

## 🚀 Features

- **Local WebLLM Integration**: Chat with AI models running entirely on your device
- **Privacy-First**: No data leaves your machine - all processing happens locally
- **Modern Tech Stack**: Django REST API backend with React TypeScript frontend
- **Cross-Platform**: Desktop applications for macOS, Windows, and Linux via BeeWare
- **Real-time Streaming**: Direct WebLLM integration with live response streaming
- **Multiple Model Support**: Switch between different WebLLM models on-the-fly
- **Processing Monitoring**: Backend tracking of WebLLM performance and usage
- **Responsive UI**: Modern, clean chat interface with model switching
- **Open Source**: MIT licensed and fully customizable

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend│    │  Django Backend  │    │   WebLLM Model  │
│   (TypeScript)  │◄──►│   (REST API)     │    │   (Local GPU)   │
│                 │    │                  │    │                 │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ Available Models│
│ │ WebLLM      │ │    │ │ Processing   │ │    │ • Llama-3.2-1B  │
│ │ Service     │◄┼────┤ │ Monitor      │ │    │ • Llama-3.2-3B  │
│ │             │ │    │ │              │ │    │ • Phi-3.5-mini  │
│ └─────────────┘ │    │ └──────────────┘ │    │ • Qwen2.5       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                       ┌────────▼────────┐
                       │  SQLite Database │
                       │  (Chat History)  │
                       └─────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **Django 4.2+**: Web framework and REST API
- **Django REST Framework**: API endpoints
- **SQLite**: Local database for chat history
- **WebLLM Processing Monitor**: Real-time processing analytics

### Frontend
- **React 18+**: UI framework
- **TypeScript**: Type-safe JavaScript
- **Styled Components**: CSS-in-JS styling
- **React Markdown**: Message rendering
- **Heroicons**: UI icons
- **WebLLM Service**: Direct model integration

### Desktop Packaging
- **BeeWare/Briefcase**: Cross-platform desktop packaging
- **Toga**: Native desktop UI toolkit

## 📦 Installation

### Prerequisites
- Python 3.9+
- Node.js 16+
- npm or yarn
- Modern GPU with WebGPU support (recommended)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/webllm/webllm-chat.git
   cd webllm-chat
   ```

2. **Backend Setup**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements_backend.txt
   
   # Run migrations
   python manage.py migrate
   
   # Start Django server
   python manage.py runserver
   ```

3. **Frontend Setup**
   ```bash
   cd src/cognitio_app/backend/frontend-src
   
   # Install dependencies
   npm install
   
   # Start development server
   npm run dev
   ```

4. **Desktop App (Optional)**
   ```bash
   # Install BeeWare
   pip install briefcase
   
   # Create desktop app
   briefcase create
   
   # Run in dev mode
   briefcase dev
   ```

## 🚀 Usage

### Starting the Application

1. **Development Mode**
   ```bash
   # Terminal 1: Start Django backend
   python manage.py runserver
   
   # Terminal 2: Start React frontend
   cd src/cognitio_app/backend/frontend-src
   npm run dev
   ```

2. **Desktop App**
   ```bash
   briefcase dev
   ```

3. **Production Build**
   ```bash
   # Build frontend
   cd src/cognitio_app/backend/frontend-src
   npm run build
   
   # Package desktop app
   briefcase build
   briefcase package
   ```

### WebLLM Integration

The framework includes a direct WebLLM service that handles local AI model processing:

```typescript
// Frontend WebLLM service
import { getWebLLMService } from './services/webllmService';

const webllmService = getWebLLMService();
await webllmService.initialize();

// Switch models on-the-fly
await webllmService.switchModel('Llama-3.2-3B-Instruct');

// Generate streaming response
const response = await webllmService.generateDirectResponse(
  'You are a helpful assistant',
  'Hello, how are you?',
  'Llama-3.2-1B-Instruct',
  (chunk) => {
    console.log('Streaming chunk:', chunk);
  }
);
```

### Backend Processing Monitor

The backend receives real-time updates about WebLLM processing:

```python
# Django view receiving WebLLM updates
@api_view(['POST'])
def webllm_processing(request):
    session_id = request.data.get('session_id')
    status = request.data.get('status')  # 'started', 'streaming', 'completed', 'error'
    model = request.data.get('model')
    
    if status == 'completed':
        processing_time = request.data.get('processing_time_ms')
        chunks_processed = request.data.get('chunks_processed')
        usage = request.data.get('usage')
        logger.info(f"WebLLM completed: {processing_time}ms, {chunks_processed} chunks")
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Django settings
DEBUG=True
SECRET_KEY=your-secret-key-here

# WebLLM settings
WEBLLM_DEFAULT_MODEL=Llama-3.2-1B-Instruct
WEBLLM_TIMEOUT=180

# Optional: Performance monitoring
WEBLLM_ENABLE_ANALYTICS=True
```

### WebLLM Models

Supported models (auto-detected from WebLLM):
- `Llama-3.2-1B-Instruct` (default, fastest)
- `Llama-3.2-3B-Instruct` (better quality)
- `Phi-3.5-mini-instruct` (balanced)
- `Qwen2.5-0.5B-Instruct` (ultra-fast)
- `Qwen2.5-1.5B-Instruct` (good balance)

**Note**: Models are automatically downloaded and cached on first use.

## 🏗️ Project Structure

```
webllm-chat/
├── src/cognitio_app/
│   ├── __main__.py                 # BeeWare entry point
│   ├── backend/
│   │   ├── api/
│   │   │   ├── models/            # Database models
│   │   │   │   └── chat.py        # Chat session & message models
│   │   │   ├── views/             # API endpoints
│   │   │   │   ├── chat_views.py  # Chat session management
│   │   │   │   └── webllm_views.py # WebLLM processing monitor
│   │   │   └── urls.py            # URL routing
│   │   ├── frontend-src/          # React frontend
│   │   │   ├── src/
│   │   │   │   ├── components/
│   │   │   │   │   └── Chat/      # Chat interface
│   │   │   │   ├── services/
│   │   │   │   │   ├── webllmService.ts      # Direct WebLLM integration
│   │   │   │   │   ├── webllmBridgeService.ts # Simplified bridge
│   │   │   │   │   └── api.ts     # Backend API client
│   │   │   │   └── utils/         # Utilities
│   │   │   └── package.json
│   │   ├── settings.py            # Django settings
│   │   └── urls.py                # Main URL config
│   └── resources/                 # App icons/assets
├── pyproject.toml                 # BeeWare configuration
├── manage.py                      # Django management
└── README.md
```

## 🎨 Customization

### Adding New Models

Models are auto-detected from WebLLM, but you can customize the available list:

```typescript
// src/services/webllmService.ts
private allowedModels = [
  "Llama-3.2-1B-Instruct-q4f16_1-MLC",
  "Your-Custom-Model-q4f16_1-MLC", // Add your model here
];
```

### UI Customization

The React frontend uses styled-components for theming:

```typescript
// src/components/Chat/Chat.tsx
const Container = styled.div`
  background: #FFFFFF;
  color: #1F2937;
  // Customize styling here
`;
```

### Backend Analytics

Monitor WebLLM performance by extending the processing endpoint:

```python
# Add custom analytics to webllm_views.py
@api_view(['POST'])
def webllm_processing(request):
    # Custom performance tracking
    if request.data.get('status') == 'completed':
        save_performance_metrics({
            'model': request.data.get('model'),
            'processing_time': request.data.get('processing_time_ms'),
            'tokens': request.data.get('usage', {}).get('total_tokens', 0)
        })
```

## 🧪 Testing

```bash
# Backend tests
python manage.py test

# Frontend tests
cd src/cognitio_app/backend/frontend-src
npm test

# Desktop app testing
briefcase dev
```

## 📊 Performance Monitoring

The framework includes built-in performance monitoring:

### Backend Logs
```
🚀 WebLLM processing started - Session: abc123, Model: Llama-3.2-1B-Instruct
📡 WebLLM streaming - Chunk: 5, Content preview...
✅ WebLLM completed - Time: 1250ms, Chunks: 15, Tokens: 45
```

### Frontend Console
```
🔄 Starting WebLLM direct streaming with model: Llama-3.2-1B-Instruct
✅ WebLLM streaming completed (15 chunks, 1250ms)
```

### API Endpoints
- `POST /api/v1/webllm/processing/` - Real-time processing updates
- `GET /api/v1/chat/sessions/` - Chat session management
- `POST /api/v1/chat/sessions/{id}/send/` - Message storage

## 📱 Platform Support

### Desktop Platforms
- **macOS**: Native .app bundle with WebGPU support
- **Windows**: MSI installer with DirectML backend
- **Linux**: AppImage with CUDA/ROCm support

### Build Commands
```bash
# macOS
briefcase build macOS
briefcase package macOS

# Windows (ensure Visual Studio tools)
briefcase build windows
briefcase package windows

# Linux (with GPU support)
briefcase build linux
briefcase package linux
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Resources

- [WebLLM Documentation](https://webllm.mlc.ai/)
- [WebLLM Model List](https://mlc.ai/models)
- [BeeWare Documentation](https://beeware.org/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://react.dev/)


## 🚀 What's New

### Recent Updates
- ✅ **Direct WebLLM Integration**: Removed bridge polling for better performance
- ✅ **Real-time Model Switching**: Change models without restart
- ✅ **Processing Analytics**: Backend monitoring of WebLLM performance
- ✅ **Streaming Optimization**: Live chunk updates with minimal latency
- ✅ **Error Handling**: Comprehensive error tracking and recovery

### Performance Improvements
- **Faster Initialization**: Models load on-demand
- **Memory Optimization**: Efficient model switching
- **Network Reduction**: Direct frontend-to-WebLLM communication
- **Real-time Updates**: Live streaming without polling overhead

## Code Protection for Distribution

The Cognitio Chat Framework includes an advanced code protection script with multiple protection methods for secure distribution. This helps protect your source code while maintaining functionality.

### Protection Methods Available

The `protect_code.py` script offers four different protection levels:

#### 1. PyArmor Protection (Recommended)
```bash
# Advanced obfuscation with PyArmor (best balance of security and performance)
python protect_code.py --method pyarmor
# or simply
python protect_code.py
```

#### 2. Nuitka Compilation 
```bash
# Compile to native machine code (strongest protection, slower build)
python protect_code.py --method nuitka
```

#### 3. Bytecode Compilation
```bash
# Compile to Python bytecode (fastest protection method)
python protect_code.py --method bytecode
```

#### 4. String Obfuscation
```bash
# Obfuscate sensitive strings and constants
python protect_code.py --method strings
```

### Basic Usage

```bash
# Use recommended PyArmor protection
python protect_code.py

# Restore original source files
python protect_code.py --restore
```

### What Gets Protected

**PyArmor Method** (targets sensitive files):
- `backend/api/services/auth_service.py`
- `backend/api/services/embedding_service.py`
- `backend/api/services/rag_chat_service.py`
- `backend/api/services/data_service.py`
- `backend/api/models.py`
- `backend/settings.py`
- `backend/authentication/cloud_auth.py`

**Bytecode Method** (all Python files):
- Model definitions and view implementations
- Business logic and utility functions
- API serializers and service layers
- Excludes test files and `__init__.py` files

**Nuitka Method** (key modules):
- Authentication services
- Embedding and data services
- Core API components

### Safety Features

- **🔄 Automatic Backup**: Creates `cognitio_app_backup` before any changes
- **📦 Easy Restoration**: Simple restore command to revert changes
- **🛡️ Intelligent Protection**: Preserves essential framework files
- **🎯 Targeted Security**: Focuses on sensitive business logic

### Integration with BeeWare Briefcase

For distribution, run the protection script before packaging:

```bash
# 1. Protect your code (choose your method)
python protect_code.py --method pyarmor    # Recommended
python protect_code.py --method nuitka     # Strongest
python protect_code.py --method bytecode   # Fastest

# 2. Package with Briefcase
briefcase create
briefcase build
briefcase package

# 3. Your protected app will be in dist/
```

### Example Production Workflow

```bash
# 1. Protect code with PyArmor (recommended)
python protect_code.py

# 2. Build and package
briefcase create
briefcase build
briefcase package

# 3. If needed, restore for development
python protect_code.py --restore
```

This ensures your Cognitio Chat Framework is properly protected while maintaining all functionality for end users.

