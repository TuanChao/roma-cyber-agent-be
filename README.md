# 🔐 Roma Security Cyber Agent System - Backend
## AI-Powered Security Monitoring API

[![Railway](https://img.shields.io/badge/Deployed%20on-Railway-000000?style=flat&logo=railway&logoColor=white)](https://web-production-dcd5c.up.railway.app)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)](https://python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5--turbo-412991?style=flat&logo=openai&logoColor=white)](https://openai.com/)

FastAPI backend for the Roma Security Cyber Agent System - providing AI-powered security analysis, real-time monitoring, and comprehensive threat detection.

## 🚀 Live API

**🌐 [API Documentation](https://web-production-dcd5c.up.railway.app/docs)**

## 📋 Features

### 🤖 **AI Security Analysis**
- OpenAI GPT-3.5-turbo integration
- Intelligent threat classification
- Risk assessment and scoring
- Security recommendations
- Multi-provider AI support (OpenAI/Gemini)

### 🔍 **Security Agents**
- **Network Monitor**: Real-time packet analysis
- **Attack Simulator**: Penetration testing tools
- **AI Coordinator**: Intelligent response coordination
- **Threat Analyzer**: Pattern recognition and analysis

### 🌐 **Real-time Communication**
- WebSocket connections for live updates
- Instant threat notifications
- Live agent status monitoring
- Real-time metrics streaming

### 📱 **Multi-Channel Notifications**
- Telegram Bot integration
- Discord webhook notifications
- Email alert system
- Custom notification rules

### 📊 **Comprehensive APIs**
- RESTful API endpoints
- Real-time WebSocket events
- Agent management
- Security reporting
- Dashboard analytics

## 🛠️ Tech Stack

### **Backend Framework**
- **Python 3.11+** - Modern Python with async support
- **FastAPI** - High-performance async web framework
- **Uvicorn** - ASGI server for production
- **Pydantic** - Data validation and serialization

### **AI Integration**
- **OpenAI API** - GPT-3.5-turbo for intelligent analysis
- **Google Gemini** - Alternative AI provider
- **Custom AI Service** - Multi-provider abstraction

### **Database & Caching**
- **MongoDB** - Document database for security data
- **Redis** - Caching and session management
- **Motor** - Async MongoDB driver

### **Security & Authentication**
- **JWT** - JSON Web Token authentication
- **CORS** - Cross-origin resource sharing
- **Rate Limiting** - API protection
- **Input Validation** - Pydantic models

### **Monitoring & Logging**
- **Loguru** - Advanced logging system
- **Health Checks** - System monitoring
- **Performance Metrics** - API analytics

## 🚦 Getting Started

### Prerequisites
- Python 3.11+
- MongoDB instance
- Redis instance
- OpenAI API key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/TuanChao/roma-cyber-agent-be.git
cd roma-cyber-agent-be
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
AI_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key
AI_MODEL=gpt-3.5-turbo
MONGODB_URL=mongodb://localhost:27017
REDIS_HOST=localhost
SECRET_KEY=your_secret_key
```

5. **Start the server**
```bash
python main.py
```

6. **Access API documentation**
```
http://localhost:8000/docs
```

## 📁 Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── agents/                # Security agent modules
│   ├── __init__.py
│   ├── base_agent.py      # Base agent class
│   ├── network_monitor.py # Network monitoring agent
│   ├── attack_simulator.py # Attack simulation agent
│   ├── ai_coordinator.py  # AI response coordinator
│   └── ai_service.py      # AI integration service
├── config/                # Configuration modules
│   ├── __init__.py
│   └── settings.py        # Application settings
├── utils/                 # Utility modules
│   ├── __init__.py
│   └── notifications.py   # Notification services
├── models/                # Data models
├── api/                   # API route modules
└── logs/                  # Application logs
```

## 🔧 Available Commands

```bash
# Development
python main.py              # Start development server
python -m pytest          # Run tests
python -m black .          # Format code
python -m flake8          # Lint code

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🌐 Environment Variables

### Required Variables
```env
# AI Configuration
AI_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key
AI_MODEL=gpt-3.5-turbo

# Database
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=security_monitoring

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Security
SECRET_KEY=your_secret_key_here
```

### Optional Variables
```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
ALLOWED_ORIGINS=*

# Notifications
TELEGRAM_BOT_TOKEN=your_telegram_token
TELEGRAM_CHAT_ID=your_chat_id
DISCORD_WEBHOOK_URL=your_discord_webhook

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/smas.log
```

## 🔌 API Endpoints

### **Health & Status**
```http
GET /                       # API health check
GET /api/agents/status      # Agent status overview
GET /api/agents/{agent}/health # Individual agent health
```

### **Network Monitoring**
```http
POST /api/network-monitor/start    # Start network monitoring
POST /api/network-monitor/stop     # Stop network monitoring
GET  /api/network-monitor/alerts   # Get network alerts
```

### **Attack Simulation**
```http
POST /api/attack-simulator/port-scan # Simulate port scan
POST /api/attack-simulator/ddos      # Simulate DDoS attack
GET  /api/attack-simulator/results   # Get simulation results
```

### **AI Analysis**
```http
POST /api/ai/chat          # Chat with AI assistant
POST /api/ai/analyze       # Analyze security incident
GET  /api/ai/recommendations # Get security recommendations
```

### **Dashboard**
```http
GET /api/dashboard/overview # Dashboard overview data
GET /api/dashboard/metrics  # Real-time metrics
GET /api/reports/security   # Security reports
```

### **WebSocket**
```http
WS /ws                     # Real-time updates connection
```

## 🤖 AI Integration

### **OpenAI Configuration**
```python
# AI Service supports multiple providers
AI_PROVIDER = "openai"
AI_MODEL = "gpt-3.5-turbo"  # or "gpt-4" with proper access
AI_TEMPERATURE = 0.7
AI_MAX_TOKENS = 1000
```

### **AI Capabilities**
- Threat analysis and classification
- Security incident assessment
- Risk scoring and recommendations
- Natural language security consulting
- Pattern recognition and prediction

## 🔒 Security Features

### **Authentication & Authorization**
- JWT-based authentication
- Role-based access control
- API key management
- Session security

### **Data Protection**
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- Rate limiting

### **Monitoring & Auditing**
- Request/response logging
- Security event tracking
- Performance monitoring
- Error handling and reporting

## 🚀 Deployment

### **Railway (Recommended)**
1. Connect GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push to main branch

### **Docker Deployment**
```bash
# Build Docker image
docker build -t roma-security-be .

# Run container
docker run -p 8000:8000 roma-security-be
```

### **Manual Deployment**
```bash
# Install production dependencies
pip install -r requirements.txt

# Start with Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📊 Agent System

### **Network Monitor Agent**
- Real-time packet capture and analysis
- Protocol breakdown and statistics
- Anomaly detection algorithms
- Performance metrics collection

### **Attack Simulator Agent**
- Port scanning simulation
- DDoS attack testing
- Vulnerability assessment
- Penetration testing tools

### **AI Coordinator Agent**
- Intelligent threat analysis
- Response recommendation
- Pattern recognition
- Predictive analytics

## 🔧 Configuration

### **FastAPI Configuration**
- CORS middleware setup
- Request/response middleware
- Error handling
- API documentation

### **Database Configuration**
- MongoDB connection pooling
- Redis caching strategy
- Data modeling and schemas
- Migration scripts

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- **Frontend Dashboard**: [roma-cyber-agent-fe](https://github.com/TuanChao/roma-cyber-agent-fe)
- **Main Repository**: [Roma-Security-cyber](https://github.com/TuanChao/Roma-Security-cyber)

## 📞 Support

- **Developer**: TuanChao
- **GitHub Issues**: [Report Issues](https://github.com/TuanChao/roma-cyber-agent-be/issues)
- **API Documentation**: [Live API Docs](https://web-production-dcd5c.up.railway.app/docs)

---

**Roma Security Backend** - *AI-powered FastAPI backend for enterprise security monitoring* 🚀