"""
Analytics module for Alerts & Early Warning System.
Detects spikes, escalations, novelty events, and evidence-based alerts.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import uuid
from database.neo4j_connector import neo4j_connector
from models.schemas import Alert


class AlertSystem:
    """Handles automatic detection of important or anomalous situations."""
    
    @staticmethod
    def generate_all_alerts(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Alert]:
        """
        Generate all types of alerts for a given time period.
        """
        alerts = []
        
        # Generate spike alerts
        spike_alerts = AlertSystem.detect_spike_alerts(start_date, end_date)
        alerts.extend(spike_alerts)
        
        # Generate escalation alerts
        escalation_alerts = AlertSystem.detect_escalation_alerts(start_date, end_date)
        alerts.extend(escalation_alerts)
        
        # Generate novelty alerts
        novelty_alerts = AlertSystem.detect_novelty_alerts(start_date, end_date)
        alerts.extend(novelty_alerts)
        
        # Generate evidence alerts
        evidence_alerts = AlertSystem.detect_evidence_alerts(start_date, end_date)
        alerts.extend(evidence_alerts)
        
        # Sort by severity and time
        severity_order = {"high": 0, "medium": 1, "low": 2}
        alerts.sort(key=lambda x: (severity_order.get(x.severity, 3), x.triggered_at), reverse=True)
        
        return alerts
    
    @staticmethod
    def detect_spike_alerts(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        threshold_multiplier: float = 2.5
    ) -> List[Alert]:
        """
        Detect sudden increases in event frequency.
        """
        # Look back 30 days for baseline
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=7)
        
        baseline_start = start_date - timedelta(days=30)
        
        params = {
            "baseline_start": baseline_start.isoformat(),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
        query = """
            MATCH (a:Article)-[:HAS_EVENT]->(e:Event)
            WHERE a.published_date >= datetime($baseline_start)
              AND a.published_date <= datetime($end_date)
            WITH date(a.published_date) AS day,
                 e.type AS event_type,
                 CASE
                     WHEN a.published_date >= datetime($start_date) THEN 'recent'
                     ELSE 'baseline'
                 END AS period
            WITH event_type, period, COUNT(*) AS count
            WITH event_type,
                 SUM(CASE WHEN period = 'recent' THEN count ELSE 0 END) AS recent_count,
                 SUM(CASE WHEN period = 'baseline' THEN count ELSE 0 END) AS baseline_count
            WHERE baseline_count > 0
              AND recent_count > baseline_count * $threshold
            RETURN event_type,
                   recent_count,
                   baseline_count,
                   round(toFloat(recent_count) / baseline_count, 2) AS spike_ratio
            ORDER BY spike_ratio DESC
            LIMIT 10
        """
        
        params["threshold"] = threshold_multiplier
        results = neo4j_connector.execute_read(query, params)
        
        alerts = []
        for r in results:
            # Get sample events
            sample_query = """
                MATCH (a:Article)-[:HAS_EVENT]->(e:Event)
                WHERE e.type = $event_type
                  AND a.published_date >= datetime($start_date)
                  AND a.published_date <= datetime($end_date)
                RETURN e.event_id AS event_id, a.article_id AS article_id
                LIMIT 5
            """
            sample_results = neo4j_connector.execute_read(sample_query, {
                "event_type": r["event_type"],
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            })
            
            severity = "high" if r["spike_ratio"] >= 5 else "medium" if r["spike_ratio"] >= 3 else "low"
            
            alerts.append(Alert(
                alert_id=str(uuid.uuid4()),
                alert_type="spike",
                severity=severity,
                title=f"Spike in {r['event_type']} events",
                description=f"Detected {r['spike_ratio']}x increase in {r['event_type']} events. "
                           f"Recent count: {r['recent_count']}, Baseline: {r['baseline_count']}",
                triggered_at=end_date,
                related_events=[s["event_id"] for s in sample_results],
                related_entities=[],
                supporting_articles=[s["article_id"] for s in sample_results]
            ))
        
        return alerts
    
    @staticmethod
    def detect_escalation_alerts(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Alert]:
        """
        Detect transitions from diplomatic to conflict events.
        """
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=14)
        
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
        # Find entities involved in both diplomatic and conflict events
        query = """
            MATCH (a1:Article)-[:HAS_EVENT]->(e1:Event)-[:INVOLVES]->(ent:Entity)
                  <-[:INVOLVES]-(e2:Event)<-[:HAS_EVENT]-(a2:Article)
            WHERE e1.type STARTS WITH 'Diplomacy'
              AND e2.type STARTS WITH 'Conflict'
              AND a1.published_date >= datetime($start_date)
              AND a1.published_date <= datetime($end_date)
              AND a2.published_date >= datetime($start_date)
              AND a2.published_date <= datetime($end_date)
              AND a2.published_date > a1.published_date
              AND duration.inDays(a1.published_date, a2.published_date).days <= 14
            WITH ent,
                 COUNT(DISTINCT e1) AS diplomatic_events,
                 COUNT(DISTINCT e2) AS conflict_events,
                 COLLECT(DISTINCT e1.event_id)[..3] AS diplomatic_event_ids,
                 COLLECT(DISTINCT e2.event_id)[..3] AS conflict_event_ids,
                 MAX(a2.published_date) AS latest_conflict
            WHERE conflict_events >= 1 AND diplomatic_events >= 1
            RETURN ent.entity_id AS entity_id,
                   ent.text AS entity_text,
                   diplomatic_events,
                   conflict_events,
                   diplomatic_event_ids,
                   conflict_event_ids,
                   latest_conflict
            ORDER BY conflict_events DESC
            LIMIT 10
        """
        
        results = neo4j_connector.execute_read(query, params)
        
        alerts = []
        for r in results:
            alerts.append(Alert(
                alert_id=str(uuid.uuid4()),
                alert_type="escalation",
                severity="high",
                title=f"Escalation detected: {r['entity_text']}",
                description=f"Entity '{r['entity_text']}' transitioned from diplomatic ({r['diplomatic_events']} events) "
                           f"to conflict events ({r['conflict_events']} events) within 14 days.",
                triggered_at=r["latest_conflict"],
                related_events=r["diplomatic_event_ids"] + r["conflict_event_ids"],
                related_entities=[r["entity_id"]],
                supporting_articles=[]
            ))
        
        return alerts
    
    @staticmethod
    def detect_novelty_alerts(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Alert]:
        """
        Detect new actors appearing in established event clusters.
        """
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=7)
        
        lookback_date = start_date - timedelta(days=90)
        
        params = {
            "lookback_date": lookback_date.isoformat(),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
        # Find entities that appear in recent events but not in historical events
        query = """
            MATCH (a:Article)-[:HAS_EVENT]->(e:Event)-[:INVOLVES]->(ent:Entity)
            WHERE a.published_date >= datetime($start_date)
              AND a.published_date <= datetime($end_date)
            WITH DISTINCT ent, e.type AS event_type, COLLECT(DISTINCT e.event_id)[..3] AS recent_events
            
            // Check if entity was NOT active in this event type before
            OPTIONAL MATCH (ent)<-[:INVOLVES]-(e_old:Event)<-[:HAS_EVENT]-(a_old:Article)
            WHERE a_old.published_date >= datetime($lookback_date)
              AND a_old.published_date < datetime($start_date)
              AND e_old.type = event_type
            WITH ent, event_type, recent_events, COUNT(e_old) AS old_count
            WHERE old_count = 0
            
            RETURN ent.entity_id AS entity_id,
                   ent.text AS entity_text,
                   ent.label AS entity_label,
                   event_type,
                   recent_events
            LIMIT 15
        """
        
        results = neo4j_connector.execute_read(query, params)
        
        alerts = []
        for r in results:
            alerts.append(Alert(
                alert_id=str(uuid.uuid4()),
                alert_type="novelty",
                severity="medium",
                title=f"New actor in {r['event_type']}: {r['entity_text']}",
                description=f"Entity '{r['entity_text']}' ({r['entity_label']}) appeared in {r['event_type']} events "
                           f"for the first time in 90 days.",
                triggered_at=end_date,
                related_events=r["recent_events"],
                related_entities=[r["entity_id"]],
                supporting_articles=[]
            ))
        
        return alerts
    
    @staticmethod
    def detect_evidence_alerts(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_confidence: float = 0.8,
        max_sources: int = 2
    ) -> List[Alert]:
        """
        Detect high-confidence events supported by limited sources.
        These may indicate exclusive reporting or potential misinformation.
        """
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=7)
        
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "min_confidence": min_confidence,
            "max_sources": max_sources
        }
        
        query = """
            MATCH (a:Article)-[:HAS_EVENT]->(e:Event)
            WHERE a.published_date >= datetime($start_date)
              AND a.published_date <= datetime($end_date)
              AND e.confidence >= $min_confidence
            WITH e,
                 COLLECT(DISTINCT a.source) AS sources,
                 COLLECT(DISTINCT a.article_id) AS articles,
                 MAX(a.published_date) AS latest_article
            WHERE SIZE(sources) <= $max_sources
            
            // Get involved entities
            OPTIONAL MATCH (e)-[:INVOLVES]->(ent:Entity)
            WITH e, sources, articles, latest_article, COLLECT(DISTINCT ent.entity_id) AS entities
            
            RETURN e.event_id AS event_id,
                   e.type AS event_type,
                   e.confidence AS confidence,
                   sources,
                   articles,
                   entities,
                   latest_article
            ORDER BY e.confidence DESC
            LIMIT 10
        """
        
        results = neo4j_connector.execute_read(query, params)
        
        alerts = []
        for r in results:
            source_count = len(r["sources"])
            severity = "high" if source_count == 1 else "medium"
            
            alerts.append(Alert(
                alert_id=str(uuid.uuid4()),
                alert_type="evidence",
                severity=severity,
                title=f"High-confidence event with limited sources: {r['event_type']}",
                description=f"Event {r['event_id']} has high confidence ({r['confidence']:.2f}) "
                           f"but is only reported by {source_count} source(s): {', '.join(r['sources'])}. "
                           f"This warrants verification.",
                triggered_at=r["latest_article"],
                related_events=[r["event_id"]],
                related_entities=r["entities"],
                supporting_articles=r["articles"]
            ))
        
        return alerts
    
    @staticmethod
    def get_alert_details(alert_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific alert.
        """
        # This would retrieve stored alert details from a database
        # For now, we'll return None as alerts are generated on-the-fly
        return None

