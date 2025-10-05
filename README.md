#  BizGenie - AI-Powered Market Intelligence Platform

> **Your AI Business Consultant** - Transform market research and business intelligence with the power of AI agents, real-time data analysis, and intelligent insights.

BizGenie is an innovative AI-powered platform that combines advanced market intelligence, CSV data analysis, and multi-agent orchestration to help entrepreneurs, business analysts, and decision-makers make data-driven business decisions with confidence.

---

## 🌟 Key Features

### 🔍 **Market Intelligence & Research Agent**

- **Real-time Market Analysis**: Leverages SearchAPI integration for live market data
- **Competitor Discovery**: Identifies and analyzes competitors using Google Maps data
- **Trend Analysis**: Tracks market trends and consumer behavior patterns
- **Business Opportunity Detection**: AI-powered identification of market gaps and opportunities
- **Location-based Insights**: Geographic market analysis for strategic expansion

### 📊 **CSV Data Analysis Agent**

- **Natural Language Queries**: Ask questions about your data in plain English
- **Intelligent Data Summaries**: Automatic statistical analysis and insights
- **Interactive Visualizations**: Generate charts and graphs on-demand
- **Data Type Detection**: Smart recognition of numeric, categorical, and date columns
- **Cerebras-Powered**: Ultra-fast inference using Cerebras Cloud SDK

### 🧠 **Multi-Agent Architecture**

- **Research Agent**: Conducts comprehensive market research
- **Structured Analysis Agent**: Processes and structures raw data
- **Business Discovery Agent**: Identifies business opportunities
- **Evaluation Agent**: Assesses viability and provides recommendations

### 💾 **Unified Memory System**

- **Cross-Agent Memory**: Persistent context sharing across all agents
- **User Session Management**: Personalized experience with memory retention
- **Research History**: Track and retrieve past analyses
- **Data Persistence**: Secure storage of user interactions and insights

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js Frontend (Port 3000)              │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐     │
│  │   Landing   │  │  Dashboard   │  │  Analytics    │     │
│  │    Page     │  │     UI       │  │    Views      │     │
│  └─────────────┘  └──────────────┘  └───────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴────────────────┐
         │                                │
┌────────▼─────────────┐      ┌──────────▼──────────────┐
│  Research Agent      │      │   CSV Analysis Agent    │
│  Backend (Port 8000) │      │   Backend (Port 8001)   │
│                      │      │                         │
│  ┌────────────────┐ │      │  ┌──────────────────┐  │
│  │ LangGraph      │ │      │  │ Cerebras AI      │  │
│  │ Multi-Agents   │ │      │  │ Engine           │  │
│  └────────────────┘ │      │  └──────────────────┘  │
│                      │      │                         │
│  ┌────────────────┐ │      │  ┌──────────────────┐  │
│  │ SearchAPI      │ │      │  │ Pandas Analysis  │  │
│  │ Integration    │ │      │  │ Engine           │  │
│  └────────────────┘ │      │  └──────────────────┘  │
└──────────────────────┘      └─────────────────────────┘
         │                                │
         └───────────────┬────────────────┘
                         │
              ┌──────────▼──────────┐
              │  Unified Memory     │
              │  Management System  │
              │  (JSON Storage)     │
              └─────────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18+ and npm/yarn/pnpm
- **Python** 3.10+
- **Git**
- **API Keys**:
  - Cerebras API Key ([Get one here](https://cloud.cerebras.ai/))
  - SearchAPI Key ([Get one here](https://www.searchapi.io/))
  - Groq API Key (Optional, for additional LLM support)

### Installation

#### 1️⃣ Clone the Repository

```bash
git clone https://github.com/akshatg887/We-make-devs.git
cd biz-genie
```

#### 2️⃣ Frontend Setup (Next.js)

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

#### 3️⃣ Research Agent Backend Setup

```bash
cd "Research Agent Backend"

# Create virtual environment
python -m venv my_env

# Activate virtual environment
# On Windows:
.\my_env\Scripts\activate
# On macOS/Linux:
source my_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API keys
echo "CEREBRAS_API_KEY=your_cerebras_api_key_here" > .env
echo "SEARCHAPI_KEY=your_searchapi_key_here" >> .env
echo "GROQ_API_KEY=your_groq_api_key_here" >> .env

# Run the server
uvicorn main:app --reload --port 8000
```

The Research Agent API will be available at `http://localhost:8000`

#### 4️⃣ CSV Agent Backend Setup

```bash
cd csv-agent

# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "CEREBRAS_API_KEY=your_cerebras_api_key_here" > .env
echo "CEREBRAS_MODEL=llama3.1-8b" >> .env

# Run the server
uvicorn app_analyze:app --reload --port 8001
```

The CSV Agent API will be available at `http://localhost:8001`

---

## 📖 Usage Guide

### Market Research Workflow

1. **Navigate to Research Dashboard**: Access the market intelligence interface
2. **Enter Business Details**:
   - Business type (e.g., "coffee shop", "bakery", "pharmacy")
   - Target location (e.g., "Delhi", "Pune")
3. **Generate Insights**: Click "Analyze Market" to trigger the multi-agent research
4. **Review Results**:
   - Competitor analysis with ratings and reviews
   - Market saturation levels
   - Trend data and growth projections
   - Identified opportunities and market gaps
5. **Export Reports**: Download comprehensive reports in JSON format

### CSV Analysis Workflow

1. **Upload CSV File**: Drag and drop or select your CSV file
2. **Automatic Analysis**: System generates statistical summaries automatically
3. **Ask Questions**: Use natural language to query your data
   - "What is the average sales by region?"
   - "Show me the top 5 products by revenue"
   - "Create a visualization of monthly trends"
4. **Generate Visualizations**: Request charts and graphs
5. **Download Insights**: Export analysis results and charts

---

## 🛠️ Technology Stack

### Frontend

- **Next.js 15.5** - React framework with Turbopack
- **React 19** - UI library
- **Tailwind CSS 4** - Utility-first CSS framework
- **Recharts** - Data visualization library
- **Lucide React** - Icon library
- **Framer Motion** - Animation library
- **Styled Components** - CSS-in-JS styling

### Backend - Research Agent

- **FastAPI** - Modern Python web framework
- **Cerebras Cloud SDK** - Ultra-fast LLM inference
- **SearchAPI** - Real-time web search and data
- **Pandas** - Data manipulation and analysis
- **Matplotlib & Seaborn** - Data visualization
- **Llama** - Additional LLM support

### Backend - CSV Agent

- **FastAPI** - High-performance API framework
- **Pandas & NumPy** - Data processing
- **Matplotlib** - Chart generation
- **Cerebras AI** - Natural language understanding
- **Python-multipart** - File upload handling

### Memory & Storage

- **JSON-based Storage** - Lightweight persistent storage
- **Unified Memory Manager** - Cross-agent context sharing

---

## 📁 Project Structure

```
biz-genie/
│
├── src/                          # Next.js frontend source
│   ├── app/                      # App router pages
│   │   ├── landing/             # Landing page
│   │   ├── root/                # Dashboard root
│   │   ├── layout.jsx           # Root layout
│   │   └── page.jsx             # Home page
│   ├── components/              # React components
│   │   ├── Hero.jsx             # Hero section
│   │   ├── Features.jsx         # Features showcase
│   │   ├── Demo.jsx             # Interactive demo
│   │   └── Navbar.jsx           # Navigation
│   └── services/                # API services
│
├── Research Agent Backend/      # Market intelligence backend
│   ├── agents/                  # Multi-agent system
│   │   ├── research_agent.py           # Main research orchestrator
│   │   ├── business_discovery_agent.py # Opportunity finder
│   │   ├── structured_analysis_agent.py # Data processor
│   │   └── evaluation_agent.py         # Viability assessor
│   ├── tools/                   # Utility tools
│   │   └── searchapi_client.py # SearchAPI integration
│   ├── config/                  # Configuration
│   │   └── models.py            # Pydantic models
│   ├── main.py                  # FastAPI application
│   └── requirements.txt         # Python dependencies
│
├── csv-agent/                   # CSV analysis backend
│   ├── app_analyze.py           # Main FastAPI app
│   ├── cerebras_csv_insights.py # Cerebras integration
│   ├── start_csv_agent.ps1      # Windows startup script
│   └── requirements.txt         # Python dependencies
│
├── shared/                      # Shared modules
│   └── unified_memory_manager.py # Cross-agent memory
│
├── memory/                      # Persistent storage
│   ├── csv_data/               # CSV session data
│   ├── research_data/          # Research results
│   └── users/                  # User profiles
│
├── memory_storage/             # Alternative storage location
│
├── public/                     # Static assets
│   ├── UI elements/           # UI components
│   └── [images]               # Brand assets
│
├── package.json               # Node.js dependencies
├── next.config.mjs            # Next.js configuration
├── tailwind.config.mjs        # Tailwind configuration
└── README.md                  # This file
```

---

## 🔑 Key APIs

### Research Agent Endpoints

```
POST   /research              - Conduct market research
GET    /health                - Health check
POST   /analyze/competitors   - Competitor analysis
POST   /analyze/trends        - Trend analysis
POST   /discover/business     - Business opportunity discovery
```

### CSV Agent Endpoints

```
POST   /upload_csv            - Upload and analyze CSV
POST   /chat                  - Chat with your data
GET    /summary/{session_id}  - Get data summary
POST   /visualize             - Generate visualizations
GET    /download/{session_id} - Download results
```

---

## 🎯 Use Cases

1. **Entrepreneurs**: Validate business ideas and identify market opportunities
2. **Business Analysts**: Conduct rapid market research and competitor analysis
3. **Data Scientists**: Quickly analyze and visualize CSV datasets
4. **Consultants**: Generate comprehensive market intelligence reports
5. **Investors**: Evaluate market potential for investment decisions
6. **Marketing Teams**: Understand market trends and consumer behavior

---

## 🔐 Environment Variables

Create `.env` files in the respective directories:

### Frontend (`/.env.local`)

```env
NEXT_PUBLIC_RESEARCH_API_URL=http://localhost:8000
NEXT_PUBLIC_CSV_API_URL=http://localhost:8001
```

### Research Agent Backend (`/Research Agent Backend/.env`)

```env
CEREBRAS_API_KEY=your_cerebras_api_key
SEARCHAPI_KEY=your_searchapi_key
GROQ_API_KEY=your_groq_api_key
```

### CSV Agent Backend (`/csv-agent/.env`)

```env
CEREBRAS_API_KEY=your_cerebras_api_key
CEREBRAS_MODEL=llama3.1-8b
```

---

## 🧪 Testing

### Test Research Agent

```bash
cd "Research Agent Backend"
my_env\Scripts\activate
uvicorn main:app --reload --port 8000 
```

### Test CSV Agent

```bash
cd csv-agent
venv\Scripts\activate
uvicorn app_analyze:app --reload --port 8001
```

### Frontend Tests

```bash
npm run test
```

---

---

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Contribution Guidelines

- Follow existing code style and conventions
- Write clear commit messages
- Add tests for new features
- Update documentation as needed

---

### Upcoming Features

- [ ] Real-time collaboration features
- [ ] Advanced visualization options
- [ ] Custom agent training
- [ ] Mobile-responsive dashboard improvements
- [ ] Export to PDF/Excel
- [ ] Integration with more data sources
- [ ] Multi-language support

---

## 📄 License

This project is developed for the **We Make Devs Future Stack 25 Hackathon**.

---
## 👥 Team

**Project Maintainer**: 

Atharva Jain

Niraj Patil

Heten Patil 

Akshat Gandhi

---

## 🙏 Acknowledgments

- **We Make Devs** for organizing Future Stack 25 Hackathon
- **Cerebras** for providing ultra-fast AI inference capabilities
- **SearchAPI** for real-time market data access
- **Next.js** for the amazing developer experience

---
---

## ⭐ Star this Repository

If you find BizGenie useful, please give it a star! It helps us reach more developers and entrepreneurs who can benefit from AI-powered market intelligence.

---

**Built with ❤️ for We Make Devs Future Stack 25 Hackathon**

