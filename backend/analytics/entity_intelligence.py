"""
Analytics module for Entity Intelligence.
Provides comprehensive analysis of entities (countries, organizations, persons).
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from database.neo4j_connector import neo4j_connector
from models.schemas import (
    EntityOverviewResponse,
    EntityTimelineEvent,
    EntityNetworkNode,
    EntityNetworkResponse
)


class EntityIntelligence:
    """Handles entity profiling, timeline analysis, and network discovery."""
    
    @staticmethod
    def search_entities(query: str, label: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search for entities by text pattern.
        """
        params = {"query": f"(?i).*{query}.*", "limit": limit}
        
        where_clauses = ["ent.text =~ $query"]
        
        if label:
            where_clauses.append("ent.label = $label")
            params["label"] = label
        
        where_clause = " AND ".join(where_clauses)
        
        query_str = f"""
            MATCH (ent:Entity)
            WHERE {where_clause}
            OPTIONAL MATCH (ent)<-[:INVOLVES]-(e:Event)
            WITH ent, COUNT(DISTINCT e) AS event_count
            RETURN ent.entity_id AS entity_id,
                   ent.text AS text,
                   ent.label AS label,
                   event_count
            ORDER BY event_count DESC
            LIMIT $limit
        """
        
        results = neo4j_connector.execute_read(query_str, params)
        
        return [
            {
                "entity_id": r["entity_id"],
                "text": r["text"],
                "label": r["label"],
                "event_count": r["event_count"]
            }
            for r in results
        ]
    
    @staticmethod
    def get_entity_overview(entity_id: str) -> Optional[EntityOverviewResponse]:
        """
        Get comprehensive overview of an entity including event statistics.
        """
        query = """
            MATCH (ent:Entity {entity_id: $entity_id})
            OPTIONAL MATCH (ent)<-[:INVOLVES]-(e:Event)<-[:HAS_EVENT]-(a:Article)
            WITH ent,
                 COUNT(DISTINCT e) AS total_events,
                 COLLECT(DISTINCT e.type) AS event_types,
                 MIN(a.published_date) AS first_seen,
                 MAX(a.published_date) AS last_seen,
                 e
            WITH ent, total_events, first_seen, last_seen,
                 [type IN event_types | {type: type, count: SIZE([ev IN COLLECT(e) WHERE ev.type = type])}] AS distribution
            RETURN ent.entity_id AS entity_id,
                   ent.text AS text,
                   ent.label AS label,
                   total_events,
                   distribution,
                   first_seen,
                   last_seen
        """
        
        results = neo4j_connector.execute_read(query, {"entity_id": entity_id})
        
        if not results:
            return None
        
        r = results[0]
        
        # Process distribution
        event_distribution = {}
        if r.get("distribution"):
            # Get actual type counts
            dist_query = """
                MATCH (ent:Entity {entity_id: $entity_id})<-[:INVOLVES]-(e:Event)
                WITH e.type AS event_type, COUNT(*) AS count
                RETURN event_type, count
            """
            dist_results = neo4j_connector.execute_read(dist_query, {"entity_id": entity_id})
            event_distribution = {dr["event_type"]: dr["count"] for dr in dist_results}
        
        return EntityOverviewResponse(
            entity_id=r["entity_id"],
            text=r["text"],
            label=r["label"],
            total_events=r["total_events"] or 0,
            event_distribution=event_distribution,
            first_seen=r.get("first_seen"),
            last_seen=r.get("last_seen")
        )
    
    @staticmethod
    def get_entity_timeline(
        entity_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[EntityTimelineEvent]:
        """
        Get chronological timeline of events involving the entity.
        """
        params = {"entity_id": entity_id, "limit": limit}
        where_clauses = []
        
        if start_date:
            where_clauses.append("a.published_date >= $start_date")
            params["start_date"] = start_date.isoformat()
        
        if end_date:
            where_clauses.append("a.published_date <= $end_date")
            params["end_date"] = end_date.isoformat()
        
        where_clause = "AND " + " AND ".join(where_clauses) if where_clauses else ""
        
        query = f"""
            MATCH (ent:Entity {{entity_id: $entity_id}})<-[:INVOLVES]-(e:Event)<-[:HAS_EVENT]-(a:Article)
            WHERE TRUE {where_clause}
            RETURN e.event_id AS event_id,
                   e.type AS event_type,
                   a.published_date AS date,
                   a.title AS article_title,
                   e.confidence AS confidence
            ORDER BY a.published_date DESC
            LIMIT $limit
        """
        
        results = neo4j_connector.execute_read(query, params)
        
        return [
            EntityTimelineEvent(
                event_id=r["event_id"],
                event_type=r["event_type"],
                date=r["date"],
                article_title=r["article_title"],
                confidence=r["confidence"]
            )
            for r in results
        ]
    
    @staticmethod
    def get_entity_network(entity_id: str, k_hops: int = 2, limit: int = 50) -> EntityNetworkResponse:
        """
        Get k-hop network of related entities connected through events.
        Returns Entity ↔ Event ↔ Entity relationships.
        """
        if k_hops == 1:
            # Direct connections through events
            query = """
                MATCH (ent1:Entity {entity_id: $entity_id})<-[:INVOLVES]-(e:Event)-[:INVOLVES]->(ent2:Entity)
                WHERE ent1 <> ent2
                WITH ent2, COUNT(DISTINCT e) AS connection_count
                RETURN ent2.entity_id AS entity_id,
                       ent2.text AS text,
                       ent2.label AS label,
                       connection_count
                ORDER BY connection_count DESC
                LIMIT $limit
            """
        else:
            # 2-hop connections
            query = """
                MATCH path = (ent1:Entity {entity_id: $entity_id})<-[:INVOLVES]-(e1:Event)
                             -[:INVOLVES]->(bridge:Entity)<-[:INVOLVES]-(e2:Event)
                             -[:INVOLVES]->(ent2:Entity)
                WHERE ent1 <> bridge AND bridge <> ent2 AND ent1 <> ent2
                WITH ent2, COUNT(DISTINCT path) AS connection_count
                RETURN ent2.entity_id AS entity_id,
                       ent2.text AS text,
                       ent2.label AS label,
                       connection_count
                ORDER BY connection_count DESC
                LIMIT $limit
            """
        
        params = {"entity_id": entity_id, "limit": limit}
        results = neo4j_connector.execute_read(query, params)
        
        nodes = [
            EntityNetworkNode(
                entity_id=r["entity_id"],
                text=r["text"],
                label=r["label"],
                connection_count=r["connection_count"]
            )
            for r in results
        ]
        
        # Get edges (shared events)
        edges = []
        for node in nodes:
            edge_query = """
                MATCH (ent1:Entity {entity_id: $entity_id})<-[:INVOLVES]-(e:Event)-[:INVOLVES]->(ent2:Entity {entity_id: $target_id})
                RETURN e.event_id AS event_id,
                       e.type AS event_type,
                       COUNT(*) AS weight
                LIMIT 5
            """
            edge_results = neo4j_connector.execute_read(
                edge_query,
                {"entity_id": entity_id, "target_id": node.entity_id}
            )
            
            for er in edge_results:
                edges.append({
                    "source": entity_id,
                    "target": node.entity_id,
                    "event_id": er["event_id"],
                    "event_type": er["event_type"],
                    "weight": er["weight"]
                })
        
        return EntityNetworkResponse(nodes=nodes, edges=edges)
    
    @staticmethod
    def get_source_perspective(entity_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Analyze news sources mentioning the entity.
        Shows which sources report on this entity most frequently.
        """
        query = """
            MATCH (ent:Entity {entity_id: $entity_id})<-[:INVOLVES]-(e:Event)<-[:HAS_EVENT]-(a:Article)
            WITH a.source AS source,
                 COUNT(DISTINCT a) AS article_count,
                 COUNT(DISTINCT e) AS event_count,
                 COLLECT(DISTINCT e.type) AS event_types
            RETURN source,
                   article_count,
                   event_count,
                   event_types
            ORDER BY article_count DESC
            LIMIT $limit
        """
        
        results = neo4j_connector.execute_read(query, {"entity_id": entity_id, "limit": limit})
        
        return [
            {
                "source": r["source"],
                "article_count": r["article_count"],
                "event_count": r["event_count"],
                "event_types": r["event_types"]
            }
            for r in results
        ]

