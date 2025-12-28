from neo4j import GraphDatabase
from neo4j.time import DateTime as Neo4jDateTime
from typing import List, Dict, Any, Optional
import logging
from config import config

logger = logging.getLogger(__name__)


def convert_neo4j_types(obj):
    """Convert Neo4j types to Python native types"""
    if isinstance(obj, Neo4jDateTime):
        return obj.to_native()
    elif isinstance(obj, dict):
        return {k: convert_neo4j_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_neo4j_types(item) for item in obj]
    return obj


class Neo4jConnector:
    """Manages connection to Neo4j database and provides query execution methods."""
    
    def __init__(self):
        self.driver = None
        self.connect()
    
    def connect(self):
        """Establish connection to Neo4j database."""
        try:
            self.driver = GraphDatabase.driver(
                config.NEO4J_URI,
                auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("Successfully connected to Neo4j database")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    def close(self):
        """Close database connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    def execute_read(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a read query and return results."""
        if parameters is None:
            parameters = {}
        
        with self.driver.session() as session:
            result = session.run(query, parameters)
            # Convert Neo4j types to Python native types
            return [convert_neo4j_types(dict(record)) for record in result]
    
    def execute_write(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a write query and return results."""
        if parameters is None:
            parameters = {}
        
        with self.driver.session() as session:
            result = session.run(query, parameters)
            # Convert Neo4j types to Python native types
            return [convert_neo4j_types(dict(record)) for record in result]
    
    def initialize_schema(self):
        """Initialize database schema with constraints and indexes."""
        schema_queries = [
            # Constraints for unique IDs
            "CREATE CONSTRAINT article_id IF NOT EXISTS FOR (a:Article) REQUIRE a.article_id IS UNIQUE",
            "CREATE CONSTRAINT event_id IF NOT EXISTS FOR (e:Event) REQUIRE e.event_id IS UNIQUE",
            "CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (ent:Entity) REQUIRE ent.entity_id IS UNIQUE",
            
            # Indexes for common queries
            "CREATE INDEX article_date IF NOT EXISTS FOR (a:Article) ON (a.published_date)",
            "CREATE INDEX event_type IF NOT EXISTS FOR (e:Event) ON (e.type)",
            "CREATE INDEX entity_label IF NOT EXISTS FOR (ent:Entity) ON (ent.label)",
            "CREATE INDEX entity_text IF NOT EXISTS FOR (ent:Entity) ON (ent.text)",
        ]
        
        for query in schema_queries:
            try:
                self.execute_write(query)
                logger.info(f"Executed schema query: {query[:50]}...")
            except Exception as e:
                logger.warning(f"Schema query failed (may already exist): {e}")


# Global connector instance
neo4j_connector = Neo4jConnector()

