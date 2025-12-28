# Analytical Subsystem for Automated News Analysis

A comprehensive analytical platform for exploring and analyzing news data through an event-centric knowledge graph built on Neo4j. This system provides structured insights, event monitoring, entity intelligence, storyline discovery, and fact-backed question answering.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)
![React](https://img.shields.io/badge/React-18.2+-blue.svg)
![Neo4j](https://img.shields.io/badge/Neo4j-5.16+-green.svg)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Knowledge Graph Schema](#knowledge-graph-schema)
- [Deployment](#deployment)
- [Contributing](#contributing)

## 🎯 Overview

The Analytical Subsystem operates on a pre-built event knowledge graph with the structure:

**Article → Event → Entity**

It provides:
- Event monitoring and trend analysis
- Entity profiling and relationship discovery
- Multi-step storyline exploration
- Automated alert generation for anomalies
- Fact-backed question answering

**This system does NOT handle data ingestion or NLP processing** - it operates exclusively on an existing knowledge graph.

## ✨ Features

### 1. **Event Monitor**
- Real-time event feed with filtering
- Event trends and time-series analysis
- Top actor identification
- Spike detection in event activity
- Evidence tracking for each event

### 2. **Entity Intelligence**
- Comprehensive entity profiles
- Historical timeline of entity involvement
- Relationship network visualization (k-hop subgraph)
- Source perspective analysis
- Event distribution by entity

### 3. **Storyline Explorer**
- Pattern-based event chain discovery
- Temporal constraint support
- Bridge actor identification
- Event transition analysis
- Multi-hop storyline tracking

### 4. **Alerts & Early Warning System**
Four types of automated alerts:
- **Spike Alerts**: Sudden increase in event frequency
- **Escalation Alerts**: Transition from diplomatic to conflict events
- **Novelty Alerts**: New actors in established event clusters
- **Evidence Alerts**: High-confidence events with limited sources

### 5. **Fact-backed Q&A**
- Natural language query processing
- Evidence-backed responses
- Explicit source attribution
- Support for complex analytical queries

### 6. **Statistics & Analytics**
- Overall knowledge graph statistics
- Event type distribution
- Temporal trends
- Aggregations and visualizations

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  Dashboard | Events | Entities | Storylines | Alerts | Q&A  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ REST API
                             │
┌────────────────────────────▼────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Event Monitor | Entity Intelligence | Storyline     │  │
│  │  Explorer | Alert System | QA System                 │  │
│  └──────────────────────────┬───────────────────────────┘  │
└─────────────────────────────┼──────────────────────────────┘
                              │
                              │ Bolt Protocol
                              │
┌─────────────────────────────▼──────────────────────────────┐
│                    Neo4j Graph Database                      │
│  Nodes: Article, Event, Entity                              │
│  Relationships: MENTIONS, HAS_EVENT, INVOLVES               │
└──────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**
- FastAPI (Python web framework)
- Neo4j Python Driver
- Pydantic (data validation)
- Pandas (data processing)

**Frontend:**
- React 18
- Material-UI (UI components)
- Recharts (visualizations)
- React Router (navigation)
- Axios (API client)

**Database:**
- Neo4j 5.16+

## 📦 Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Neo4j 5.16+** (or Docker)
- **Docker & Docker Compose** (optional, for containerized deployment)

## 🚀 Installation

### Option 1: Automated Setup (Recommended)

**Linux/macOS:**
```bash
./setup.sh
```

**Windows:**
```bash
setup.bat
```

The setup script will:
1. Check system requirements
2. Create Python virtual environment
3. Install backend dependencies
4. Install frontend dependencies
5. Create environment configuration files

### Option 2: Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your Neo4j credentials
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

#### Neo4j Setup

**Using Docker:**
```bash
docker-compose up -d neo4j
```

**Manual Installation:**
1. Download Neo4j from https://neo4j.com/download/
2. Start Neo4j server
3. Access Neo4j Browser at http://localhost:7474
4. Set initial password

### Option 3: Docker Compose (All Services)

```bash
# Edit docker-compose.yml with your settings
docker-compose up
```

## 🎮 Usage

### Starting the Application

#### Development Mode (Manual)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

#### Production Mode (Docker)

```bash
docker-compose up -d
```

### Accessing the Application

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474

### Initial Configuration

1. **Configure Backend** (`backend/.env`):
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here
API_HOST=0.0.0.0
API_PORT=8000
```

2. **Initialize Neo4j Schema**:
The schema is automatically initialized on first startup, creating:
- Unique constraints for IDs
- Indexes for common queries

## 📚 API Documentation

### Event Monitor Endpoints

```
POST   /analytics/events              # Get filtered events
GET    /analytics/events/trends       # Get event trends
GET    /analytics/events/top-actors   # Get top actors
GET    /analytics/events/{id}/evidence # Get event evidence
GET    /analytics/events/spikes       # Detect event spikes
```

### Entity Intelligence Endpoints

```
POST   /analytics/entities/search              # Search entities
GET    /analytics/entities/{id}/overview       # Entity overview
GET    /analytics/entities/{id}/timeline       # Entity timeline
GET    /analytics/entities/{id}/network        # Entity network
GET    /analytics/entities/{id}/sources        # Source analysis
```

### Storyline Explorer Endpoints

```
POST   /analytics/storylines/find              # Find event chains
GET    /analytics/bridge-actors                # Find bridge actors
GET    /analytics/storylines/entity/{id}/chains # Entity chains
GET    /analytics/storylines/transitions       # Event transitions
```

### Alerts Endpoints

```
GET    /analytics/alerts              # Get all alerts
POST   /analytics/alerts/config       # Configure alerts
```

### Q&A Endpoints

```
POST   /analytics/qa                  # Ask a question
```

### Statistics Endpoints

```
GET    /analytics/stats/overview      # Overall statistics
GET    /analytics/stats/event-types   # Event type distribution
```

### Example API Calls

**Get Events:**
```bash
curl -X POST http://localhost:8000/analytics/events \
  -H "Content-Type: application/json" \
  -d '{
    "event_types": ["Conflict", "Diplomacy"],
    "min_confidence": 0.7,
    "limit": 50
  }'
```

**Search Entities:**
```bash
curl -X POST http://localhost:8000/analytics/entities/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Russia",
    "limit": 20
  }'
```

**Ask a Question:**
```bash
curl -X POST http://localhost:8000/analytics/qa \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What events involve China and USA?"
  }'
```

For full interactive API documentation, visit: http://localhost:8000/docs

## 🗄️ Knowledge Graph Schema

### Node Types

**Article**
- `article_id` (unique)
- `title`
- `published_date`
- `source`
- `link`

**Event**
- `event_id` (unique)
- `type` (e.g., "Conflict.Attack", "Diplomacy.Sanction")
- `trigger_word`
- `confidence` (0.0-1.0)
- `article_id`

**Entity**
- `entity_id` (unique)
- `text`
- `label` (GPE, ORG, PERSON, DATE, etc.)

### Relationships

- `Article → MENTIONS → Entity`
- `Article → HAS_EVENT → Event`
- `Event → INVOLVES → Entity`

### Example Cypher Queries

**Find all events involving a specific entity:**
```cypher
MATCH (ent:Entity {text: "Russia"})<-[:INVOLVES]-(e:Event)<-[:HAS_EVENT]-(a:Article)
RETURN e, a
ORDER BY a.published_date DESC
LIMIT 10
```

**Find event chains:**
```cypher
MATCH (e1:Event)-[:INVOLVES]->(ent:Entity)<-[:INVOLVES]-(e2:Event)
WHERE e1.type STARTS WITH 'Conflict' AND e2.type STARTS WITH 'Diplomacy'
RETURN e1, ent, e2
```

## 🔍 Frontend Features

### Dashboard
- Real-time statistics
- Event type distribution chart
- Event trends visualization
- Quick overview of knowledge graph

### Event Monitor
- Filterable event feed
- Top actors sidebar
- Event details with evidence
- Date range filtering

### Entity Intelligence
- Entity search
- Comprehensive entity profiles
- Timeline visualization
- Network graph of connections

### Storyline Explorer
- Pattern-based chain discovery
- Bridge actor identification
- Visual storyline representation
- Temporal relationship analysis

### Alerts Page
- Categorized alert display
- Severity-based filtering
- Detailed alert explanations
- Evidence and source links

### Q&A Interface
- Natural language queries
- Evidence-backed responses
- Related entities and events
- Query history

## 🚢 Deployment

### Production Deployment with Docker

1. **Configure environment:**
```bash
# Edit docker-compose.yml
# Set secure passwords
# Configure resource limits
```

2. **Build and start:**
```bash
docker-compose up -d
```

3. **Scale services:**
```bash
docker-compose up -d --scale backend=3
```

### Security Considerations

- Change default Neo4j password
- Use environment variables for secrets
- Configure CORS properly for production
- Enable HTTPS/TLS
- Set up authentication/authorization
- Use secure network configurations

### Performance Optimization

- Configure Neo4j memory settings
- Add database indexes for frequent queries
- Enable caching in backend
- Use CDN for frontend assets
- Implement rate limiting

## 📊 Sample Data Requirements

For the system to work, your Neo4j database should contain:

1. **Article nodes** with published dates, sources, titles
2. **Event nodes** with types, confidence scores, trigger words
3. **Entity nodes** with text and labels
4. **Proper relationships** connecting these nodes

### Data Schema Validation

Run this Cypher query to verify your data:

```cypher
MATCH (a:Article)
WITH count(a) as articles
MATCH (e:Event)
WITH articles, count(e) as events
MATCH (ent:Entity)
RETURN articles, events, count(ent) as entities
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/
```

### Frontend Tests

```bash
cd frontend
npm run test
```

## 🐛 Troubleshooting

### Common Issues

**Neo4j Connection Failed:**
- Verify Neo4j is running: `docker ps` or check Neo4j Desktop
- Check connection URI in `.env`
- Verify credentials
- Ensure port 7687 is not blocked

**Frontend Can't Connect to Backend:**
- Verify backend is running on port 8000
- Check CORS configuration
- Verify API_URL in frontend environment

**No Data Displayed:**
- Verify Neo4j database has data
- Check API responses in browser DevTools
- Review backend logs for errors

**Performance Issues:**
- Increase Neo4j memory allocation
- Add database indexes
- Reduce query result limits
- Check network latency

## 📝 Development

### Project Structure

```
Analitical_system/
├── backend/
│   ├── analytics/          # Analytics modules
│   │   ├── alerts.py
│   │   ├── entity_intelligence.py
│   │   ├── event_monitor.py
│   │   ├── storyline_explorer.py
│   │   └── qa_system.py
│   ├── database/           # Database connectors
│   │   └── neo4j_connector.py
│   ├── models/             # Data models
│   │   └── schemas.py
│   ├── config.py           # Configuration
│   ├── main.py             # FastAPI application
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml
├── setup.sh
├── setup.bat
└── README.md
```

### Adding New Features

1. **Backend**: Add new modules in `backend/analytics/`
2. **Frontend**: Add new pages in `frontend/src/pages/`
3. **API**: Update `backend/main.py` with new endpoints
4. **Documentation**: Update this README

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 👥 Authors

- Analytical Subsystem Development Team

## 🙏 Acknowledgments

- Neo4j for the graph database
- FastAPI framework
- React and Material-UI teams
- Open source community

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation
- Review API documentation at `/docs`

---

**Built with ❤️ for news analysis and knowledge discovery**

