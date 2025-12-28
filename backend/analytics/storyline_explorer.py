"""
Analytics module for Storyline/Chain Explorer.
Discovers multi-step event chains and identifies bridge actors.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from database.neo4j_connector import neo4j_connector
from models.schemas import StorylineChain
import uuid


class StorylineExplorer:
    """Handles storyline discovery, event chain pattern matching, and bridge actor identification."""
    
    @staticmethod
    def find_storylines(
        event_pattern: List[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_days_between_events: int = 30,
        limit: int = 20
    ) -> List[StorylineChain]:
        """
        Find event chains matching a specific pattern.
        Example: ["Conflict.Attack", "Diplomacy.Sanction", "Diplomacy.Meeting"]
        """
        if len(event_pattern) < 2:
            return []
        
        # Build dynamic pattern matching query
        params = {
            "max_days": max_days_between_events,
            "limit": limit
        }
        
        # Add date filters
        date_filters = []
        if start_date:
            date_filters.append("a1.published_date >= $start_date")
            params["start_date"] = start_date.isoformat()
        if end_date:
            date_filters.append(f"a{len(event_pattern)}.published_date <= $end_date")
            params["end_date"] = end_date.isoformat()
        
        date_filter_str = " AND " + " AND ".join(date_filters) if date_filters else ""
        
        # Build pattern matching for 2 or 3 events
        if len(event_pattern) == 2:
            query = f"""
                MATCH (a1:Article)-[:HAS_EVENT]->(e1:Event)-[:INVOLVES]->(ent:Entity)
                      <-[:INVOLVES]-(e2:Event)<-[:HAS_EVENT]-(a2:Article)
                WHERE e1.type STARTS WITH $type1
                  AND e2.type STARTS WITH $type2
                  AND a2.published_date >= a1.published_date
                  AND a2.published_date <= a1.published_date + duration({{days: $max_days}})
                  {date_filter_str}
                WITH e1, e2, a1, a2, COLLECT(DISTINCT ent) AS entities
                RETURN e1, e2, a1, a2, entities,
                       duration.inDays(a1.published_date, a2.published_date).days AS time_span
                ORDER BY a1.published_date DESC
                LIMIT $limit
            """
            params["type1"] = event_pattern[0]
            params["type2"] = event_pattern[1]
            
        elif len(event_pattern) == 3:
            query = f"""
                MATCH (a1:Article)-[:HAS_EVENT]->(e1:Event)-[:INVOLVES]->(ent1:Entity)
                      <-[:INVOLVES]-(e2:Event)<-[:HAS_EVENT]-(a2:Article),
                      (e2)-[:INVOLVES]->(ent2:Entity)<-[:INVOLVES]-(e3:Event)<-[:HAS_EVENT]-(a3:Article)
                WHERE e1.type STARTS WITH $type1
                  AND e2.type STARTS WITH $type2
                  AND e3.type STARTS WITH $type3
                  AND a2.published_date >= a1.published_date
                  AND a2.published_date <= a1.published_date + duration({{days: $max_days}})
                  AND a3.published_date >= a2.published_date
                  AND a3.published_date <= a2.published_date + duration({{days: $max_days}})
                  {date_filter_str}
                WITH e1, e2, e3, a1, a2, a3,
                     COLLECT(DISTINCT ent1) + COLLECT(DISTINCT ent2) AS entities
                RETURN e1, e2, e3, a1, a2, a3, entities,
                       duration.inDays(a1.published_date, a3.published_date).days AS time_span
                ORDER BY a1.published_date DESC
                LIMIT $limit
            """
            params["type1"] = event_pattern[0]
            params["type2"] = event_pattern[1]
            params["type3"] = event_pattern[2]
        else:
            # For patterns with more than 3 events, use a more generic approach
            return StorylineExplorer._find_long_storylines(
                event_pattern, start_date, end_date, max_days_between_events, limit
            )
        
        results = neo4j_connector.execute_read(query, params)
        
        storylines = []
        for r in results:
            events = []
            entities_set = set()
            
            # Extract events based on pattern length
            for i in range(1, len(event_pattern) + 1):
                event_key = f"e{i}"
                article_key = f"a{i}"
                
                if event_key in r:
                    event_node = r[event_key]
                    article_node = r[article_key]
                    
                    events.append({
                        "event_id": event_node.get("event_id"),
                        "type": event_node.get("type"),
                        "trigger_word": event_node.get("trigger_word"),
                        "confidence": event_node.get("confidence"),
                        "date": article_node.get("published_date"),
                        "article_title": article_node.get("title"),
                        "article_id": article_node.get("article_id")
                    })
            
            # Extract entities
            if "entities" in r and r["entities"]:
                for ent in r["entities"]:
                    if hasattr(ent, 'get'):
                        entities_set.add(ent.get("text", ""))
                    elif isinstance(ent, str):
                        entities_set.add(ent)
            
            # Calculate average confidence
            avg_confidence = sum(e["confidence"] for e in events if e.get("confidence")) / len(events)
            
            storylines.append(StorylineChain(
                chain_id=str(uuid.uuid4()),
                events=events,
                entities=list(entities_set),
                confidence=round(avg_confidence, 3),
                time_span_days=r.get("time_span", 0)
            ))
        
        return storylines
    
    @staticmethod
    def _find_long_storylines(
        event_pattern: List[str],
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        max_days_between_events: int,
        limit: int
    ) -> List[StorylineChain]:
        """
        Handle patterns with more than 3 events using variable-length paths.
        """
        # This is a simplified version for longer chains
        params = {
            "event_types": event_pattern,
            "max_days": max_days_between_events,
            "limit": limit * 5  # Get more candidates for filtering
        }
        
        date_filters = []
        if start_date:
            date_filters.append("a.published_date >= $start_date")
            params["start_date"] = start_date.isoformat()
        if end_date:
            date_filters.append("a.published_date <= $end_date")
            params["end_date"] = end_date.isoformat()
        
        date_filter_str = " AND " + " AND ".join(date_filters) if date_filters else ""
        
        query = f"""
            MATCH path = (e1:Event)-[:INVOLVES]->(:Entity)<-[:INVOLVES]-(e2:Event)
            MATCH (a1:Article)-[:HAS_EVENT]->(e1)
            MATCH (a2:Article)-[:HAS_EVENT]->(e2)
            WHERE e1.type IN $event_types
              AND e2.type IN $event_types
              AND e1 <> e2
              {date_filter_str}
            RETURN e1, e2, a1, a2
            LIMIT $limit
        """
        
        results = neo4j_connector.execute_read(query, params)
        
        # Post-process results to build chains
        # This is a simplified version
        return []
    
    @staticmethod
    def find_bridge_actors(
        event_type1: str,
        event_type2: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Find entities that act as bridges between two different event types.
        These are actors involved in both event types.
        """
        params = {
            "type1": event_type1,
            "type2": event_type2,
            "limit": limit
        }
        
        date_filters = []
        if start_date:
            date_filters.append("a1.published_date >= $start_date AND a2.published_date >= $start_date")
            params["start_date"] = start_date.isoformat()
        if end_date:
            date_filters.append("a1.published_date <= $end_date AND a2.published_date <= $end_date")
            params["end_date"] = end_date.isoformat()
        
        date_filter_str = " AND " + " AND ".join(date_filters) if date_filters else ""
        
        query = f"""
            MATCH (a1:Article)-[:HAS_EVENT]->(e1:Event)-[:INVOLVES]->(ent:Entity)
                  <-[:INVOLVES]-(e2:Event)<-[:HAS_EVENT]-(a2:Article)
            WHERE (e1.type STARTS WITH $type1 AND e2.type STARTS WITH $type2)
               OR (e1.type STARTS WITH $type2 AND e2.type STARTS WITH $type1)
               {date_filter_str}
            WITH ent,
                 COUNT(DISTINCT e1) AS type1_events,
                 COUNT(DISTINCT e2) AS type2_events,
                 COUNT(DISTINCT e1) + COUNT(DISTINCT e2) AS total_events,
                 COLLECT(DISTINCT e1.type)[..5] AS type1_examples,
                 COLLECT(DISTINCT e2.type)[..5] AS type2_examples
            RETURN ent.entity_id AS entity_id,
                   ent.text AS text,
                   ent.label AS label,
                   type1_events,
                   type2_events,
                   total_events,
                   type1_examples,
                   type2_examples
            ORDER BY total_events DESC
            LIMIT $limit
        """
        
        results = neo4j_connector.execute_read(query, params)
        
        return [
            {
                "entity_id": r["entity_id"],
                "text": r["text"],
                "label": r["label"],
                "type1_events": r["type1_events"],
                "type2_events": r["type2_events"],
                "total_events": r["total_events"],
                "type1_examples": r["type1_examples"],
                "type2_examples": r["type2_examples"]
            }
            for r in results
        ]
    
    @staticmethod
    def get_temporal_chains(
        entity_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get temporal event chains for a specific entity.
        Shows sequence of events involving the entity over time.
        """
        params = {"entity_id": entity_id, "limit": limit}
        
        date_filters = []
        if start_date:
            date_filters.append("a.published_date >= $start_date")
            params["start_date"] = start_date.isoformat()
        if end_date:
            date_filters.append("a.published_date <= $end_date")
            params["end_date"] = end_date.isoformat()
        
        date_filter_str = " AND " + " AND ".join(date_filters) if date_filters else ""
        
        query = f"""
            MATCH (ent:Entity {{entity_id: $entity_id}})<-[:INVOLVES]-(e:Event)<-[:HAS_EVENT]-(a:Article)
            WHERE TRUE {date_filter_str}
            WITH e, a
            ORDER BY a.published_date
            RETURN COLLECT({{
                event_id: e.event_id,
                type: e.type,
                trigger_word: e.trigger_word,
                confidence: e.confidence,
                date: a.published_date,
                article_title: a.title
            }}) AS event_chain
            LIMIT $limit
        """
        
        results = neo4j_connector.execute_read(query, params)
        
        if results and "event_chain" in results[0]:
            return results[0]["event_chain"]
        return []
    
    @staticmethod
    def analyze_event_transitions(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_occurrences: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Analyze common event type transitions.
        Shows which event types commonly follow others.
        """
        params = {"min_occurrences": min_occurrences}
        
        date_filters = []
        if start_date:
            date_filters.append("a1.published_date >= $start_date")
            params["start_date"] = start_date.isoformat()
        if end_date:
            date_filters.append("a2.published_date <= $end_date")
            params["end_date"] = end_date.isoformat()
        
        date_filter_str = " AND " + " AND ".join(date_filters) if date_filters else ""
        
        query = f"""
            MATCH (a1:Article)-[:HAS_EVENT]->(e1:Event)-[:INVOLVES]->(ent:Entity)
                  <-[:INVOLVES]-(e2:Event)<-[:HAS_EVENT]-(a2:Article)
            WHERE a2.published_date > a1.published_date
              AND a2.published_date <= a1.published_date + duration({{days: 30}})
              {date_filter_str}
            WITH e1.type AS from_type,
                 e2.type AS to_type,
                 COUNT(*) AS occurrences,
                 AVG(duration.inDays(a1.published_date, a2.published_date).days) AS avg_days_between
            WHERE occurrences >= $min_occurrences
            RETURN from_type,
                   to_type,
                   occurrences,
                   round(avg_days_between) AS avg_days_between
            ORDER BY occurrences DESC
            LIMIT 50
        """
        
        results = neo4j_connector.execute_read(query, params)
        
        return [
            {
                "from_type": r["from_type"],
                "to_type": r["to_type"],
                "occurrences": r["occurrences"],
                "avg_days_between": r["avg_days_between"]
            }
            for r in results
        ]

