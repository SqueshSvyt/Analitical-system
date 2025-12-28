"""
Analytics module for Fact-backed News QA.
Answers analytical queries using facts from the knowledge graph.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from database.neo4j_connector import neo4j_connector
from models.schemas import QAResponse


class QASystem:
    """Handles fact-backed question answering using the knowledge graph."""
    
    @staticmethod
    def answer_query(
        query: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> QAResponse:
        """
        Answer a user query by retrieving relevant facts from the knowledge graph.
        """
        # Parse query to understand intent
        query_type, params = QASystem._parse_query(query)
        
        # Route to appropriate handler
        if query_type == "events_by_entity":
            return QASystem._answer_events_by_entity(query, params, start_date, end_date)
        elif query_type == "entity_relationships":
            return QASystem._answer_entity_relationships(query, params, start_date, end_date)
        elif query_type == "event_count":
            return QASystem._answer_event_count(query, params, start_date, end_date)
        elif query_type == "escalation":
            return QASystem._answer_escalation(query, params, start_date, end_date)
        elif query_type == "top_actors":
            return QASystem._answer_top_actors(query, params, start_date, end_date)
        else:
            # General fallback query
            return QASystem._answer_general(query, start_date, end_date)
    
    @staticmethod
    def _parse_query(query: str) -> tuple:
        """
        Parse natural language query to determine intent and extract parameters.
        """
        query_lower = query.lower()
        params = {}
        
        # Extract entity names (capitalized words or phrases in quotes)
        entity_matches = re.findall(r'"([^"]+)"', query)
        if entity_matches:
            params["entity"] = entity_matches[0]
        else:
            # Try to find capitalized sequences
            cap_matches = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', query)
            if cap_matches:
                params["entity"] = cap_matches[0]
        
        # Extract event types
        event_types = [
            "conflict", "attack", "diplomacy", "sanction", "meeting",
            "protest", "election", "treaty", "war", "peace"
        ]
        for event_type in event_types:
            if event_type in query_lower:
                params["event_type"] = event_type.capitalize()
        
        # Determine query type
        if any(word in query_lower for word in ["what events", "which events", "events involving"]):
            return "events_by_entity", params
        elif any(word in query_lower for word in ["relationship", "connected", "related to"]):
            return "entity_relationships", params
        elif any(word in query_lower for word in ["how many", "count", "number of"]):
            return "event_count", params
        elif any(word in query_lower for word in ["escalation", "escalated", "tension"]):
            return "escalation", params
        elif any(word in query_lower for word in ["top", "most", "frequent", "main actors"]):
            return "top_actors", params
        else:
            return "general", params
    
    @staticmethod
    def _answer_events_by_entity(
        query: str,
        params: Dict[str, Any],
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> QAResponse:
        """
        Answer queries about events involving a specific entity.
        """
        entity_name = params.get("entity")
        event_type = params.get("event_type")
        
        if not entity_name:
            return QAResponse(
                query=query,
                answer="I couldn't identify a specific entity in your query. Please specify an entity name.",
                evidence=[],
                related_entities=[],
                related_events=[]
            )
        
        # Build query
        cypher_params = {"entity_name": f"(?i).*{entity_name}.*"}
        where_clauses = ["ent.text =~ $entity_name"]
        
        if event_type:
            where_clauses.append("e.type STARTS WITH $event_type")
            cypher_params["event_type"] = event_type
        
        if start_date:
            where_clauses.append("a.published_date >= $start_date")
            cypher_params["start_date"] = start_date.isoformat()
        
        if end_date:
            where_clauses.append("a.published_date <= $end_date")
            cypher_params["end_date"] = end_date.isoformat()
        
        where_clause = " AND ".join(where_clauses)
        
        cypher_query = f"""
            MATCH (ent:Entity)<-[:INVOLVES]-(e:Event)<-[:HAS_EVENT]-(a:Article)
            WHERE {where_clause}
            WITH ent, e, a
            ORDER BY a.published_date DESC
            LIMIT 20
            RETURN ent.entity_id AS entity_id,
                   ent.text AS entity_text,
                   e.event_id AS event_id,
                   e.type AS event_type,
                   e.trigger_word AS trigger_word,
                   e.confidence AS confidence,
                   a.article_id AS article_id,
                   a.title AS article_title,
                   a.published_date AS published_date,
                   a.source AS source,
                   a.link AS link
        """
        
        results = neo4j_connector.execute_read(cypher_query, cypher_params)
        
        if not results:
            answer = f"No events found involving '{entity_name}'"
            if event_type:
                answer += f" of type '{event_type}'"
            answer += " in the specified time period."
            
            return QAResponse(
                query=query,
                answer=answer,
                evidence=[],
                related_entities=[],
                related_events=[]
            )
        
        # Build answer
        entity_text = results[0]["entity_text"]
        event_count = len(results)
        event_types_found = list(set(r["event_type"] for r in results))
        
        answer = f"Found {event_count} events involving '{entity_text}'. "
        answer += f"Event types include: {', '.join(event_types_found[:5])}. "
        
        if event_count > 5:
            answer += f"The most recent events are:\n"
            for r in results[:5]:
                answer += f"- {r['event_type']} on {r['published_date'].strftime('%Y-%m-%d')}: \"{r['article_title']}\"\n"
        else:
            answer += "Events:\n"
            for r in results:
                answer += f"- {r['event_type']} on {r['published_date'].strftime('%Y-%m-%d')}: \"{r['article_title']}\"\n"
        
        # Build evidence
        evidence = [
            {
                "event_id": r["event_id"],
                "event_type": r["event_type"],
                "trigger_word": r["trigger_word"],
                "confidence": r["confidence"],
                "article": {
                    "article_id": r["article_id"],
                    "title": r["article_title"],
                    "published_date": r["published_date"],
                    "source": r["source"],
                    "link": r["link"]
                }
            }
            for r in results
        ]
        
        return QAResponse(
            query=query,
            answer=answer,
            evidence=evidence,
            related_entities=[results[0]["entity_id"]],
            related_events=[r["event_id"] for r in results]
        )
    
    @staticmethod
    def _answer_entity_relationships(
        query: str,
        params: Dict[str, Any],
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> QAResponse:
        """
        Answer queries about relationships between entities.
        """
        entity_name = params.get("entity")
        
        if not entity_name:
            return QAResponse(
                query=query,
                answer="Please specify an entity to find relationships for.",
                evidence=[],
                related_entities=[],
                related_events=[]
            )
        
        cypher_params = {"entity_name": f"(?i).*{entity_name}.*", "limit": 10}
        date_filters = []
        
        if start_date:
            date_filters.append("a.published_date >= $start_date")
            cypher_params["start_date"] = start_date.isoformat()
        
        if end_date:
            date_filters.append("a.published_date <= $end_date")
            cypher_params["end_date"] = end_date.isoformat()
        
        date_filter_str = " AND " + " AND ".join(date_filters) if date_filters else ""
        
        cypher_query = f"""
            MATCH (ent1:Entity)<-[:INVOLVES]-(e:Event)-[:INVOLVES]->(ent2:Entity)
            MATCH (a:Article)-[:HAS_EVENT]->(e)
            WHERE ent1.text =~ $entity_name
              AND ent1 <> ent2
              {date_filter_str}
            WITH ent1, ent2, COUNT(DISTINCT e) AS shared_events,
                 COLLECT(DISTINCT e.type)[..5] AS event_types,
                 COLLECT(DISTINCT e.event_id)[..5] AS event_ids
            RETURN ent1.text AS entity1,
                   ent1.entity_id AS entity1_id,
                   ent2.text AS entity2,
                   ent2.entity_id AS entity2_id,
                   shared_events,
                   event_types,
                   event_ids
            ORDER BY shared_events DESC
            LIMIT $limit
        """
        
        results = neo4j_connector.execute_read(cypher_query, cypher_params)
        
        if not results:
            return QAResponse(
                query=query,
                answer=f"No relationships found for '{entity_name}' in the specified time period.",
                evidence=[],
                related_entities=[],
                related_events=[]
            )
        
        # Build answer
        entity1 = results[0]["entity1"]
        answer = f"'{entity1}' is connected to {len(results)} other entities through shared events:\n\n"
        
        for r in results[:5]:
            answer += f"- '{r['entity2']}': {r['shared_events']} shared events "
            answer += f"({', '.join(r['event_types'][:3])})\n"
        
        # Build evidence
        evidence = [
            {
                "related_entity": r["entity2"],
                "shared_events": r["shared_events"],
                "event_types": r["event_types"],
                "event_ids": r["event_ids"]
            }
            for r in results
        ]
        
        return QAResponse(
            query=query,
            answer=answer,
            evidence=evidence,
            related_entities=[r["entity2_id"] for r in results],
            related_events=[eid for r in results for eid in r["event_ids"]]
        )
    
    @staticmethod
    def _answer_event_count(
        query: str,
        params: Dict[str, Any],
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> QAResponse:
        """
        Answer queries about event counts.
        """
        event_type = params.get("event_type")
        entity_name = params.get("entity")
        
        cypher_params = {}
        where_clauses = []
        
        if event_type:
            where_clauses.append("e.type STARTS WITH $event_type")
            cypher_params["event_type"] = event_type
        
        if entity_name:
            where_clauses.append("ent.text =~ $entity_name")
            cypher_params["entity_name"] = f"(?i).*{entity_name}.*"
        
        if start_date:
            where_clauses.append("a.published_date >= $start_date")
            cypher_params["start_date"] = start_date.isoformat()
        
        if end_date:
            where_clauses.append("a.published_date <= $end_date")
            cypher_params["end_date"] = end_date.isoformat()
        
        if entity_name:
            match_clause = "MATCH (ent:Entity)<-[:INVOLVES]-(e:Event)<-[:HAS_EVENT]-(a:Article)"
        else:
            match_clause = "MATCH (a:Article)-[:HAS_EVENT]->(e:Event)"
        
        where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        cypher_query = f"""
            {match_clause}
            {where_clause}
            WITH e.type AS event_type, COUNT(*) AS count
            RETURN event_type, count
            ORDER BY count DESC
        """
        
        results = neo4j_connector.execute_read(cypher_query, cypher_params)
        
        if not results:
            return QAResponse(
                query=query,
                answer="No events found matching the specified criteria.",
                evidence=[],
                related_entities=[],
                related_events=[]
            )
        
        total_count = sum(r["count"] for r in results)
        answer = f"Found {total_count} events"
        
        if event_type:
            answer += f" of type '{event_type}'"
        if entity_name:
            answer += f" involving '{entity_name}'"
        
        answer += ".\n\nBreakdown by event type:\n"
        for r in results[:10]:
            answer += f"- {r['event_type']}: {r['count']} events\n"
        
        evidence = [
            {
                "event_type": r["event_type"],
                "count": r["count"]
            }
            for r in results
        ]
        
        return QAResponse(
            query=query,
            answer=answer,
            evidence=evidence,
            related_entities=[],
            related_events=[]
        )
    
    @staticmethod
    def _answer_escalation(
        query: str,
        params: Dict[str, Any],
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> QAResponse:
        """
        Answer queries about escalations or tensions.
        """
        entity_name = params.get("entity")
        
        cypher_params = {}
        entity_filter = ""
        
        if entity_name:
            entity_filter = "AND ent.text =~ $entity_name"
            cypher_params["entity_name"] = f"(?i).*{entity_name}.*"
        
        if start_date:
            cypher_params["start_date"] = start_date.isoformat()
            start_filter = "AND a1.published_date >= datetime($start_date)"
        else:
            start_filter = ""
        
        if end_date:
            cypher_params["end_date"] = end_date.isoformat()
            end_filter = "AND a2.published_date <= datetime($end_date)"
        else:
            end_filter = ""
        
        cypher_query = f"""
            MATCH (a1:Article)-[:HAS_EVENT]->(e1:Event)-[:INVOLVES]->(ent:Entity)
                  <-[:INVOLVES]-(e2:Event)<-[:HAS_EVENT]-(a2:Article)
            WHERE (e1.type STARTS WITH 'Diplomacy' OR e1.type STARTS WITH 'Peace')
              AND (e2.type STARTS WITH 'Conflict' OR e2.type STARTS WITH 'War')
              AND a2.published_date > a1.published_date
              AND duration.inDays(a1.published_date, a2.published_date).days <= 30
              {entity_filter}
              {start_filter}
              {end_filter}
            WITH ent,
                 COLLECT(DISTINCT {{
                     from_type: e1.type,
                     to_type: e2.type,
                     from_date: a1.published_date,
                     to_date: a2.published_date,
                     from_event_id: e1.event_id,
                     to_event_id: e2.event_id,
                     from_title: a1.title,
                     to_title: a2.title
                 }})[..5] AS escalations
            RETURN ent.entity_id AS entity_id,
                   ent.text AS entity_text,
                   SIZE(escalations) AS escalation_count,
                   escalations
            ORDER BY escalation_count DESC
            LIMIT 10
        """
        
        results = neo4j_connector.execute_read(cypher_query, cypher_params)
        
        if not results:
            answer = "No escalation patterns detected"
            if entity_name:
                answer += f" involving '{entity_name}'"
            answer += " in the specified time period."
            
            return QAResponse(
                query=query,
                answer=answer,
                evidence=[],
                related_entities=[],
                related_events=[]
            )
        
        # Build answer
        answer = f"Detected escalation patterns involving {len(results)} entities:\n\n"
        
        for r in results[:3]:
            entity = r["entity_text"]
            count = r["escalation_count"]
            answer += f"**{entity}**: {count} escalation pattern(s)\n"
            
            for esc in r["escalations"][:2]:
                days_between = (esc["to_date"] - esc["from_date"]).days
                answer += f"  - {esc['from_type']} → {esc['to_type']} "
                answer += f"({days_between} days apart)\n"
                answer += f"    From: \"{esc['from_title']}\"\n"
                answer += f"    To: \"{esc['to_title']}\"\n"
            answer += "\n"
        
        # Build evidence
        evidence = []
        for r in results:
            for esc in r["escalations"]:
                evidence.append({
                    "entity": r["entity_text"],
                    "from_event": {
                        "event_id": esc["from_event_id"],
                        "type": esc["from_type"],
                        "date": esc["from_date"],
                        "title": esc["from_title"]
                    },
                    "to_event": {
                        "event_id": esc["to_event_id"],
                        "type": esc["to_type"],
                        "date": esc["to_date"],
                        "title": esc["to_title"]
                    }
                })
        
        return QAResponse(
            query=query,
            answer=answer,
            evidence=evidence,
            related_entities=[r["entity_id"] for r in results],
            related_events=[esc["from_event_id"] for r in results for esc in r["escalations"]] +
                          [esc["to_event_id"] for r in results for esc in r["escalations"]]
        )
    
    @staticmethod
    def _answer_top_actors(
        query: str,
        params: Dict[str, Any],
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> QAResponse:
        """
        Answer queries about top/most frequent actors.
        """
        event_type = params.get("event_type")
        
        cypher_params = {"limit": 10}
        where_clauses = []
        
        if event_type:
            where_clauses.append("e.type STARTS WITH $event_type")
            cypher_params["event_type"] = event_type
        
        if start_date:
            where_clauses.append("a.published_date >= $start_date")
            cypher_params["start_date"] = start_date.isoformat()
        
        if end_date:
            where_clauses.append("a.published_date <= $end_date")
            cypher_params["end_date"] = end_date.isoformat()
        
        where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        cypher_query = f"""
            MATCH (a:Article)-[:HAS_EVENT]->(e:Event)-[:INVOLVES]->(ent:Entity)
            {where_clause}
            WITH ent, COUNT(DISTINCT e) AS event_count, COLLECT(DISTINCT e.type)[..5] AS event_types
            RETURN ent.entity_id AS entity_id,
                   ent.text AS entity_text,
                   ent.label AS entity_label,
                   event_count,
                   event_types
            ORDER BY event_count DESC
            LIMIT $limit
        """
        
        results = neo4j_connector.execute_read(cypher_query, cypher_params)
        
        if not results:
            return QAResponse(
                query=query,
                answer="No actors found matching the specified criteria.",
                evidence=[],
                related_entities=[],
                related_events=[]
            )
        
        answer = f"Top {len(results)} actors"
        if event_type:
            answer += f" in '{event_type}' events"
        answer += ":\n\n"
        
        for i, r in enumerate(results, 1):
            answer += f"{i}. {r['entity_text']} ({r['entity_label']}): {r['event_count']} events\n"
            answer += f"   Event types: {', '.join(r['event_types'][:3])}\n"
        
        evidence = [
            {
                "entity_id": r["entity_id"],
                "entity_text": r["entity_text"],
                "entity_label": r["entity_label"],
                "event_count": r["event_count"],
                "event_types": r["event_types"]
            }
            for r in results
        ]
        
        return QAResponse(
            query=query,
            answer=answer,
            evidence=evidence,
            related_entities=[r["entity_id"] for r in results],
            related_events=[]
        )
    
    @staticmethod
    def _answer_general(
        query: str,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> QAResponse:
        """
        Provide a general response with overall statistics.
        """
        cypher_params = {}
        date_filters = []
        
        if start_date:
            date_filters.append("a.published_date >= $start_date")
            cypher_params["start_date"] = start_date.isoformat()
        
        if end_date:
            date_filters.append("a.published_date <= $end_date")
            cypher_params["end_date"] = end_date.isoformat()
        
        date_filter_str = " AND " + " AND ".join(date_filters) if date_filters else ""
        
        cypher_query = f"""
            MATCH (a:Article)-[:HAS_EVENT]->(e:Event)
            WHERE TRUE {date_filter_str}
            WITH COUNT(DISTINCT a) AS article_count,
                 COUNT(DISTINCT e) AS event_count,
                 COLLECT(DISTINCT e.type) AS event_types
            MATCH (ent:Entity)<-[:INVOLVES]-(ev:Event)
            WHERE TRUE {date_filter_str.replace('a.', 'a2.')}
            OPTIONAL MATCH (a2:Article)-[:HAS_EVENT]->(ev)
            WITH article_count, event_count, event_types, COUNT(DISTINCT ent) AS entity_count
            RETURN article_count, event_count, SIZE(event_types) AS event_type_count, entity_count
        """
        
        results = neo4j_connector.execute_read(cypher_query, cypher_params)
        
        if results and results[0]:
            r = results[0]
            answer = f"Here's a summary of the knowledge graph"
            if start_date or end_date:
                answer += " for the specified period"
            answer += ":\n\n"
            answer += f"- Articles: {r.get('article_count', 0)}\n"
            answer += f"- Events: {r.get('event_count', 0)}\n"
            answer += f"- Event Types: {r.get('event_type_count', 0)}\n"
            answer += f"- Entities: {r.get('entity_count', 0)}\n\n"
            answer += "You can ask more specific questions about events, entities, or relationships."
        else:
            answer = "I understand you're asking about the knowledge graph, but I need more specific information. "
            answer += "Try asking about:\n"
            answer += "- Events involving a specific entity\n"
            answer += "- Relationships between entities\n"
            answer += "- Event counts by type\n"
            answer += "- Escalation patterns\n"
            answer += "- Top actors in specific events"
        
        return QAResponse(
            query=query,
            answer=answer,
            evidence=[],
            related_entities=[],
            related_events=[]
        )

