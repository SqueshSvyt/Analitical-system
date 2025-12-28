"""
Main FastAPI application for the Analytical Subsystem.
Provides REST API endpoints for news knowledge graph analytics.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
import logging

from config import config
from models.schemas import (
    EventFilterRequest,
    EventResponse,
    EventTrendPoint,
    EntitySearchRequest,
    EntityOverviewResponse,
    EntityTimelineEvent,
    EntityNetworkResponse,
    StorylineRequest,
    StorylineChain,
    Alert,
    QARequest,
    QAResponse,
    AlertConfigRequest
)
from analytics.event_monitor import EventMonitor
from analytics.entity_intelligence import EntityIntelligence
from analytics.storyline_explorer import StorylineExplorer
from analytics.alerts import AlertSystem
from analytics.qa_system import QASystem
from database.neo4j_connector import neo4j_connector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Analytical Subsystem API",
    description="REST API for news knowledge graph analytics, event monitoring, and insights",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Health Check ==============

@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": "Analytical Subsystem API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test Neo4j connection
        neo4j_connector.execute_read("RETURN 1 AS test")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


# ============== Event Monitor Endpoints ==============

@app.post("/analytics/events", response_model=List[EventResponse])
async def get_events(request: EventFilterRequest):
    """
    Get filtered list of events with their details.
    Supports filtering by date, event type, entities, sources, and confidence.
    """
    try:
        logger.info(f"Fetching events with filters: {request}")
        events = EventMonitor.get_event_feed(request)
        return events
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/events/trends", response_model=List[EventTrendPoint])
async def get_event_trends(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    event_types: Optional[List[str]] = Query(None),
    granularity: str = Query("day", regex="^(day|week|month)$")
):
    """
    Get time series of events by type.
    Useful for detecting trends and patterns over time.
    """
    try:
        logger.info(f"Fetching event trends: {start_date} to {end_date}, granularity={granularity}")
        trends = EventMonitor.get_event_trends(
            start_date=start_date,
            end_date=end_date,
            event_types=event_types,
            granularity=granularity
        )
        return trends
    except Exception as e:
        logger.error(f"Error fetching event trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/events/top-actors")
async def get_top_actors(
    event_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get most frequent entities (actors) involved in events.
    """
    try:
        logger.info(f"Fetching top actors for event_type={event_type}")
        actors = EventMonitor.get_top_actors(
            event_type=event_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        return actors
    except Exception as e:
        logger.error(f"Error fetching top actors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/events/{event_id}/evidence")
async def get_event_evidence(event_id: str):
    """
    Get all articles that support/mention a specific event.
    """
    try:
        logger.info(f"Fetching evidence for event {event_id}")
        evidence = EventMonitor.get_event_evidence(event_id)
        if not evidence:
            raise HTTPException(status_code=404, detail="Event not found")
        return evidence
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching event evidence: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/events/spikes")
async def detect_event_spikes(
    event_types: Optional[List[str]] = Query(None),
    window_days: int = Query(7, ge=1, le=30),
    threshold_multiplier: float = Query(2.0, ge=1.0, le=10.0)
):
    """
    Detect abnormal spikes in event activity.
    """
    try:
        logger.info(f"Detecting spikes with window={window_days} days")
        spikes = EventMonitor.detect_spikes(
            event_types=event_types,
            window_days=window_days,
            threshold_multiplier=threshold_multiplier
        )
        return spikes
    except Exception as e:
        logger.error(f"Error detecting spikes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Entity Intelligence Endpoints ==============

@app.post("/analytics/entities/search")
async def search_entities(request: EntitySearchRequest):
    """
    Search for entities by text pattern.
    """
    try:
        logger.info(f"Searching entities: {request.query}")
        entities = EntityIntelligence.search_entities(
            query=request.query,
            label=request.label,
            limit=request.limit
        )
        return entities
    except Exception as e:
        logger.error(f"Error searching entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/entities/{entity_id}/overview", response_model=EntityOverviewResponse)
async def get_entity_overview(entity_id: str):
    """
    Get comprehensive overview of an entity including event statistics.
    """
    try:
        logger.info(f"Fetching overview for entity {entity_id}")
        overview = EntityIntelligence.get_entity_overview(entity_id)
        if not overview:
            raise HTTPException(status_code=404, detail="Entity not found")
        return overview
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching entity overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/entities/{entity_id}/timeline", response_model=List[EntityTimelineEvent])
async def get_entity_timeline(
    entity_id: str,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=500)
):
    """
    Get chronological timeline of events involving the entity.
    """
    try:
        logger.info(f"Fetching timeline for entity {entity_id}")
        timeline = EntityIntelligence.get_entity_timeline(
            entity_id=entity_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        return timeline
    except Exception as e:
        logger.error(f"Error fetching entity timeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/entities/{entity_id}/network", response_model=EntityNetworkResponse)
async def get_entity_network(
    entity_id: str,
    k_hops: int = Query(2, ge=1, le=3),
    limit: int = Query(50, ge=1, le=200)
):
    """
    Get k-hop network of related entities connected through events.
    """
    try:
        logger.info(f"Fetching network for entity {entity_id}, k_hops={k_hops}")
        network = EntityIntelligence.get_entity_network(
            entity_id=entity_id,
            k_hops=k_hops,
            limit=limit
        )
        return network
    except Exception as e:
        logger.error(f"Error fetching entity network: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/entities/{entity_id}/sources")
async def get_entity_sources(
    entity_id: str,
    limit: int = Query(20, ge=1, le=100)
):
    """
    Analyze news sources mentioning the entity.
    """
    try:
        logger.info(f"Fetching source perspective for entity {entity_id}")
        sources = EntityIntelligence.get_source_perspective(entity_id, limit)
        return sources
    except Exception as e:
        logger.error(f"Error fetching entity sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Storyline Explorer Endpoints ==============

@app.post("/analytics/storylines/find", response_model=List[StorylineChain])
async def find_storylines(request: StorylineRequest):
    """
    Find event chains matching a specific pattern.
    Example pattern: ["Conflict.Attack", "Diplomacy.Sanction", "Diplomacy.Meeting"]
    """
    try:
        logger.info(f"Finding storylines with pattern: {request.event_pattern}")
        storylines = StorylineExplorer.find_storylines(
            event_pattern=request.event_pattern,
            start_date=request.start_date,
            end_date=request.end_date,
            max_days_between_events=request.max_days_between_events,
            limit=request.limit
        )
        return storylines
    except Exception as e:
        logger.error(f"Error finding storylines: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/bridge-actors")
async def get_bridge_actors(
    event_type1: str = Query(...),
    event_type2: str = Query(...),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Find entities that act as bridges between two different event types.
    """
    try:
        logger.info(f"Finding bridge actors between {event_type1} and {event_type2}")
        actors = StorylineExplorer.find_bridge_actors(
            event_type1=event_type1,
            event_type2=event_type2,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        return actors
    except Exception as e:
        logger.error(f"Error finding bridge actors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/storylines/entity/{entity_id}/chains")
async def get_entity_chains(
    entity_id: str,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get temporal event chains for a specific entity.
    """
    try:
        logger.info(f"Fetching event chains for entity {entity_id}")
        chains = StorylineExplorer.get_temporal_chains(
            entity_id=entity_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        return chains
    except Exception as e:
        logger.error(f"Error fetching entity chains: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/storylines/transitions")
async def analyze_event_transitions(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    min_occurrences: int = Query(3, ge=1, le=20)
):
    """
    Analyze common event type transitions.
    Shows which event types commonly follow others.
    """
    try:
        logger.info("Analyzing event transitions")
        transitions = StorylineExplorer.analyze_event_transitions(
            start_date=start_date,
            end_date=end_date,
            min_occurrences=min_occurrences
        )
        return transitions
    except Exception as e:
        logger.error(f"Error analyzing transitions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Alerts Endpoints ==============

@app.get("/analytics/alerts", response_model=List[Alert])
async def get_alerts(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    alert_type: Optional[str] = Query(None, regex="^(spike|escalation|novelty|evidence)$")
):
    """
    Get all alerts for a given time period.
    Supports filtering by alert type.
    """
    try:
        logger.info(f"Fetching alerts from {start_date} to {end_date}")
        
        if alert_type:
            # Get specific alert type
            if alert_type == "spike":
                alerts = AlertSystem.detect_spike_alerts(start_date, end_date)
            elif alert_type == "escalation":
                alerts = AlertSystem.detect_escalation_alerts(start_date, end_date)
            elif alert_type == "novelty":
                alerts = AlertSystem.detect_novelty_alerts(start_date, end_date)
            elif alert_type == "evidence":
                alerts = AlertSystem.detect_evidence_alerts(start_date, end_date)
        else:
            # Get all alerts
            alerts = AlertSystem.generate_all_alerts(start_date, end_date)
        
        return alerts
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analytics/alerts/config")
async def configure_alerts(request: AlertConfigRequest):
    """
    Configure alert parameters and thresholds.
    (This is a placeholder for future alert configuration storage)
    """
    try:
        logger.info(f"Configuring alert: {request}")
        # In a full implementation, this would store alert configurations
        return {
            "status": "configured",
            "alert_type": request.alert_type,
            "message": "Alert configuration saved successfully"
        }
    except Exception as e:
        logger.error(f"Error configuring alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== QA Endpoints ==============

@app.post("/analytics/qa", response_model=QAResponse)
async def answer_question(request: QARequest):
    """
    Answer analytical queries using facts from the knowledge graph.
    Provides evidence-backed responses with explicit sources.
    """
    try:
        logger.info(f"Processing QA query: {request.query}")
        response = QASystem.answer_query(
            query=request.query,
            start_date=request.start_date,
            end_date=request.end_date
        )
        return response
    except Exception as e:
        logger.error(f"Error processing QA query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Statistics Endpoints ==============

@app.get("/analytics/stats/overview")
async def get_statistics_overview():
    """
    Get overall statistics about the knowledge graph.
    """
    try:
        query = """
            MATCH (a:Article)
            WITH COUNT(DISTINCT a) AS article_count
            MATCH (e:Event)
            WITH article_count, COUNT(DISTINCT e) AS event_count
            MATCH (ent:Entity)
            WITH article_count, event_count, COUNT(DISTINCT ent) AS entity_count
            MATCH (a:Article)
            WITH article_count, event_count, entity_count,
                 MIN(a.published_date) AS earliest_article,
                 MAX(a.published_date) AS latest_article
            RETURN article_count, event_count, entity_count, earliest_article, latest_article
        """
        result = neo4j_connector.execute_read(query)
        
        if result:
            stats = result[0]
            return {
                "total_articles": stats.get("article_count", 0),
                "total_events": stats.get("event_count", 0),
                "total_entities": stats.get("entity_count", 0),
                "date_range": {
                    "earliest": stats.get("earliest_article"),
                    "latest": stats.get("latest_article")
                }
            }
        return {}
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/stats/event-types")
async def get_event_type_distribution():
    """
    Get distribution of event types in the knowledge graph.
    """
    try:
        query = """
            MATCH (e:Event)
            WITH e.type AS event_type, COUNT(*) AS count
            RETURN event_type, count
            ORDER BY count DESC
            LIMIT 50
        """
        results = neo4j_connector.execute_read(query)
        return results
    except Exception as e:
        logger.error(f"Error fetching event type distribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Startup & Shutdown Events ==============

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting Analytical Subsystem API")
    logger.info(f"Neo4j URI: {config.NEO4J_URI}")
    
    # Initialize schema
    try:
        neo4j_connector.initialize_schema()
        logger.info("Database schema initialized")
    except Exception as e:
        logger.error(f"Failed to initialize schema: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down Analytical Subsystem API")
    neo4j_connector.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )

