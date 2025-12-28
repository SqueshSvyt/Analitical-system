"""
Analytics module for Event Monitoring.
Provides functionality for event feeds, trends, top actors, and evidence views.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd
from database.neo4j_connector import neo4j_connector
from models.schemas import EventFilterRequest, EventResponse, EventTrendPoint


class EventMonitor:
    """Handles event monitoring, trends analysis, and actor identification."""
    
    @staticmethod
    def get_event_feed(request: EventFilterRequest) -> List[EventResponse]:
        """
        Get filtered list of events with their details and involved entities.
        """
        query_parts = ["MATCH (a:Article)-[:HAS_EVENT]->(e:Event)"]
        where_clauses = []
        params = {}
        
        # Date filters
        if request.start_date:
            where_clauses.append("a.published_date >= $start_date")
            params["start_date"] = request.start_date.isoformat()
        
        if request.end_date:
            where_clauses.append("a.published_date <= $end_date")
            params["end_date"] = request.end_date.isoformat()
        
        # Event type filter
        if request.event_types:
            where_clauses.append("e.type IN $event_types")
            params["event_types"] = request.event_types
        
        # Confidence filter
        where_clauses.append("e.confidence >= $min_confidence")
        params["min_confidence"] = request.min_confidence
        
        # Source filter
        if request.sources:
            where_clauses.append("a.source IN $sources")
            params["sources"] = request.sources
        
        # Entity filter (if specified)
        if request.entities:
            query_parts.append("MATCH (e)-[:INVOLVES]->(ent:Entity)")
            where_clauses.append("ent.text IN $entities")
            params["entities"] = request.entities
        
        # Combine WHERE clauses
        if where_clauses:
            query_parts.append("WHERE " + " AND ".join(where_clauses))
        
        # Get entities involved in events
        query_parts.append("""
            OPTIONAL MATCH (e)-[:INVOLVES]->(entity:Entity)
            WITH e, a, COLLECT(DISTINCT entity.text) AS entities
            RETURN e.event_id AS event_id,
                   e.type AS type,
                   e.trigger_word AS trigger_word,
                   e.confidence AS confidence,
                   e.article_id AS article_id,
                   a.title AS article_title,
                   a.published_date AS published_date,
                   entities
            ORDER BY a.published_date DESC
            LIMIT $limit
        """)
        
        params["limit"] = request.limit
        
        query = "\n".join(query_parts)
        results = neo4j_connector.execute_read(query, params)
        
        return [
            EventResponse(
                event_id=r["event_id"],
                type=r["type"],
                trigger_word=r["trigger_word"],
                confidence=r["confidence"],
                article_id=r["article_id"],
                article_title=r.get("article_title"),
                published_date=r.get("published_date"),
                entities=r.get("entities", [])
            )
            for r in results
        ]
    
    @staticmethod
    def get_event_trends(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_types: Optional[List[str]] = None,
        granularity: str = "day"
    ) -> List[EventTrendPoint]:
        """
        Get time series of events by type.
        Detects trends and patterns over time.
        """
        params = {}
        where_clauses = []
        
        if start_date:
            where_clauses.append("a.published_date >= $start_date")
            params["start_date"] = start_date.isoformat()
        
        if end_date:
            where_clauses.append("a.published_date <= $end_date")
            params["end_date"] = end_date.isoformat()
        
        if event_types:
            where_clauses.append("e.type IN $event_types")
            params["event_types"] = event_types
        
        where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        # Determine date format based on granularity
        date_format = {
            "day": "date(a.published_date)",
            "week": "date(a.published_date) - duration({days: date(a.published_date).dayOfWeek})",
            "month": "date(datetime({year: a.published_date.year, month: a.published_date.month, day: 1}))"
        }.get(granularity, "date(a.published_date)")
        
        query = f"""
            MATCH (a:Article)-[:HAS_EVENT]->(e:Event)
            {where_clause}
            WITH {date_format} AS period, e.type AS event_type
            RETURN toString(period) AS date,
                   event_type,
                   COUNT(*) AS count
            ORDER BY date, event_type
        """
        
        results = neo4j_connector.execute_read(query, params)
        
        return [
            EventTrendPoint(
                date=r["date"],
                event_type=r["event_type"],
                count=r["count"]
            )
            for r in results
        ]
    
    @staticmethod
    def get_top_actors(
        event_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get most frequent entities involved in events.
        Returns actors ranked by their event participation.
        """
        params = {"limit": limit}
        where_clauses = []
        
        if event_type:
            where_clauses.append("e.type = $event_type OR e.type STARTS WITH $event_type_prefix")
            params["event_type"] = event_type
            params["event_type_prefix"] = event_type + "."
        
        if start_date:
            where_clauses.append("a.published_date >= $start_date")
            params["start_date"] = start_date.isoformat()
        
        if end_date:
            where_clauses.append("a.published_date <= $end_date")
            params["end_date"] = end_date.isoformat()
        
        where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        query = f"""
            MATCH (a:Article)-[:HAS_EVENT]->(e:Event)-[:INVOLVES]->(ent:Entity)
            {where_clause}
            WITH ent, COUNT(DISTINCT e) AS event_count, COLLECT(DISTINCT e.type) AS event_types
            RETURN ent.entity_id AS entity_id,
                   ent.text AS text,
                   ent.label AS label,
                   event_count,
                   event_types
            ORDER BY event_count DESC
            LIMIT $limit
        """
        
        results = neo4j_connector.execute_read(query, params)
        
        return [
            {
                "entity_id": r["entity_id"],
                "text": r["text"],
                "label": r["label"],
                "event_count": r["event_count"],
                "event_types": r["event_types"]
            }
            for r in results
        ]
    
    @staticmethod
    def get_event_evidence(event_id: str) -> List[Dict[str, Any]]:
        """
        Get all articles that support/mention a specific event.
        """
        query = """
            MATCH (a:Article)-[:HAS_EVENT]->(e:Event {event_id: $event_id})
            RETURN a.article_id AS article_id,
                   a.title AS title,
                   a.published_date AS published_date,
                   a.source AS source,
                   a.link AS link
            ORDER BY a.published_date DESC
        """
        
        results = neo4j_connector.execute_read(query, {"event_id": event_id})
        
        return [
            {
                "article_id": r["article_id"],
                "title": r["title"],
                "published_date": r["published_date"],
                "source": r["source"],
                "link": r["link"]
            }
            for r in results
        ]
    
    @staticmethod
    def detect_spikes(
        event_types: Optional[List[str]] = None,
        window_days: int = 7,
        threshold_multiplier: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Detect abnormal spikes in event activity.
        Returns events where recent activity exceeds historical average.
        """
        query = """
            MATCH (a:Article)-[:HAS_EVENT]->(e:Event)
            WHERE a.published_date > datetime() - duration({days: $total_days})
        """
        
        if event_types:
            query += " AND e.type IN $event_types"
        
        query += """
            WITH date(a.published_date) AS day, e.type AS event_type, COUNT(*) AS daily_count
            WITH event_type,
                 COLLECT({day: day, count: daily_count}) AS daily_data
            RETURN event_type, daily_data
        """
        
        params = {
            "total_days": window_days * 4,  # Look back 4 windows for baseline
            "event_types": event_types or []
        }
        
        results = neo4j_connector.execute_read(query, params)
        
        spikes = []
        for r in results:
            event_type = r["event_type"]
            daily_data = r["daily_data"]
            
            if len(daily_data) < window_days * 2:
                continue
            
            # Calculate recent vs historical average
            recent = daily_data[-window_days:]
            historical = daily_data[:-window_days]
            
            recent_avg = sum(d["count"] for d in recent) / len(recent)
            historical_avg = sum(d["count"] for d in historical) / len(historical)
            
            if historical_avg > 0 and recent_avg / historical_avg >= threshold_multiplier:
                spikes.append({
                    "event_type": event_type,
                    "recent_average": round(recent_avg, 2),
                    "historical_average": round(historical_avg, 2),
                    "spike_ratio": round(recent_avg / historical_avg, 2)
                })
        
        return sorted(spikes, key=lambda x: x["spike_ratio"], reverse=True)

