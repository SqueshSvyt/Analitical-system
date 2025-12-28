"""
Data Import Script for Analytical Subsystem
Imports CSV data into Neo4j database
"""

import csv
import os
from datetime import datetime
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "analytical_system_2024")

# Paths to CSV files
DATA_DIR = "graph_data"
NODE_FILES = {
    "articles": "nodes_articles.csv",
    "events": "nodes_events.csv",
    "entities": "nodes_entities.csv"
}
EDGE_FILES = {
    "has_event": "edges_has_event.csv",
    "involves": "edges_involves.csv",
    "mentions": "edges_mentions.csv"
}


class Neo4jDataImporter:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        print(f"Connected to Neo4j at {uri}")
    
    def close(self):
        self.driver.close()
        print("Connection closed")
    
    def clear_database(self):
        """Clear all data from the database (optional)"""
        with self.driver.session() as session:
            print("Clearing existing data...")
            session.run("MATCH (n) DETACH DELETE n")
            print("Database cleared")
    
    def create_constraints(self):
        """Create constraints and indexes"""
        with self.driver.session() as session:
            constraints = [
                "CREATE CONSTRAINT article_id IF NOT EXISTS FOR (a:Article) REQUIRE a.article_id IS UNIQUE",
                "CREATE CONSTRAINT event_id IF NOT EXISTS FOR (e:Event) REQUIRE e.event_id IS UNIQUE",
                "CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (ent:Entity) REQUIRE ent.entity_id IS UNIQUE",
            ]
            
            indexes = [
                "CREATE INDEX article_date IF NOT EXISTS FOR (a:Article) ON (a.published_date)",
                "CREATE INDEX event_type IF NOT EXISTS FOR (e:Event) ON (e.type)",
                "CREATE INDEX entity_label IF NOT EXISTS FOR (ent:Entity) ON (ent.label)",
                "CREATE INDEX entity_text IF NOT EXISTS FOR (ent:Entity) ON (ent.text)",
            ]
            
            print("Creating constraints and indexes...")
            for query in constraints + indexes:
                try:
                    session.run(query)
                    print(f"  ✓ {query[:50]}...")
                except Exception as e:
                    print(f"  ⚠ {str(e)[:80]}")
    
    def import_articles(self, file_path):
        """Import article nodes"""
        print(f"\nImporting articles from {file_path}...")
        count = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            batch = []
            
            for row in reader:
                # Parse date
                try:
                    pub_date = datetime.strptime(row['published_date'], '%Y-%m-%d %H:%M:%S')
                    date_str = pub_date.isoformat()
                except:
                    date_str = row['published_date']
                
                batch.append({
                    'article_id': row['article_id'],
                    'title': row['title'],
                    'published_date': date_str,
                    'source': row['source'],
                    'link': row['link']
                })
                
                # Import in batches of 500
                if len(batch) >= 500:
                    self._import_article_batch(batch)
                    count += len(batch)
                    print(f"  Imported {count} articles...")
                    batch = []
            
            # Import remaining
            if batch:
                self._import_article_batch(batch)
                count += len(batch)
        
        print(f"  ✓ Total articles imported: {count}")
        return count
    
    def _import_article_batch(self, batch):
        """Import a batch of articles"""
        with self.driver.session() as session:
            query = """
            UNWIND $batch AS row
            CREATE (a:Article {
                article_id: row.article_id,
                title: row.title,
                published_date: datetime(row.published_date),
                source: row.source,
                link: row.link
            })
            """
            session.run(query, batch=batch)
    
    def import_events(self, file_path):
        """Import event nodes"""
        print(f"\nImporting events from {file_path}...")
        count = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            batch = []
            
            for row in reader:
                batch.append({
                    'event_id': row['event_id'],
                    'article_id': row['article_id'],
                    'type': row['type'],
                    'trigger_word': row['trigger_word'],
                    'confidence': float(row['confidence'])
                })
                
                if len(batch) >= 500:
                    self._import_event_batch(batch)
                    count += len(batch)
                    print(f"  Imported {count} events...")
                    batch = []
            
            if batch:
                self._import_event_batch(batch)
                count += len(batch)
        
        print(f"  ✓ Total events imported: {count}")
        return count
    
    def _import_event_batch(self, batch):
        """Import a batch of events"""
        with self.driver.session() as session:
            query = """
            UNWIND $batch AS row
            CREATE (e:Event {
                event_id: row.event_id,
                article_id: row.article_id,
                type: row.type,
                trigger_word: row.trigger_word,
                confidence: row.confidence
            })
            """
            session.run(query, batch=batch)
    
    def import_entities(self, file_path):
        """Import entity nodes"""
        print(f"\nImporting entities from {file_path}...")
        count = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            batch = []
            
            for row in reader:
                batch.append({
                    'entity_id': row['entity_id'],
                    'text': row['text'],
                    'label': row['label']
                })
                
                if len(batch) >= 500:
                    self._import_entity_batch(batch)
                    count += len(batch)
                    print(f"  Imported {count} entities...")
                    batch = []
            
            if batch:
                self._import_entity_batch(batch)
                count += len(batch)
        
        print(f"  ✓ Total entities imported: {count}")
        return count
    
    def _import_entity_batch(self, batch):
        """Import a batch of entities"""
        with self.driver.session() as session:
            query = """
            UNWIND $batch AS row
            CREATE (ent:Entity {
                entity_id: row.entity_id,
                text: row.text,
                label: row.label
            })
            """
            session.run(query, batch=batch)
    
    def import_has_event_edges(self, file_path):
        """Import HAS_EVENT relationships"""
        print(f"\nImporting HAS_EVENT relationships from {file_path}...")
        count = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            batch = []
            
            for row in reader:
                batch.append({
                    'src': row['src'],
                    'dst': row['dst']
                })
                
                if len(batch) >= 1000:
                    self._import_has_event_batch(batch)
                    count += len(batch)
                    print(f"  Imported {count} relationships...")
                    batch = []
            
            if batch:
                self._import_has_event_batch(batch)
                count += len(batch)
        
        print(f"  ✓ Total HAS_EVENT relationships: {count}")
        return count
    
    def _import_has_event_batch(self, batch):
        """Import a batch of HAS_EVENT relationships"""
        with self.driver.session() as session:
            query = """
            UNWIND $batch AS row
            MATCH (a:Article {article_id: row.src})
            MATCH (e:Event {event_id: row.dst})
            CREATE (a)-[:HAS_EVENT]->(e)
            """
            session.run(query, batch=batch)
    
    def import_involves_edges(self, file_path):
        """Import INVOLVES relationships"""
        print(f"\nImporting INVOLVES relationships from {file_path}...")
        count = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            batch = []
            
            for row in reader:
                batch.append({
                    'src': row['src'],
                    'dst': row['dst']
                })
                
                if len(batch) >= 1000:
                    self._import_involves_batch(batch)
                    count += len(batch)
                    print(f"  Imported {count} relationships...")
                    batch = []
            
            if batch:
                self._import_involves_batch(batch)
                count += len(batch)
        
        print(f"  ✓ Total INVOLVES relationships: {count}")
        return count
    
    def _import_involves_batch(self, batch):
        """Import a batch of INVOLVES relationships"""
        with self.driver.session() as session:
            query = """
            UNWIND $batch AS row
            MATCH (e:Event {event_id: row.src})
            MATCH (ent:Entity {entity_id: row.dst})
            CREATE (e)-[:INVOLVES]->(ent)
            """
            session.run(query, batch=batch)
    
    def import_mentions_edges(self, file_path):
        """Import MENTIONS relationships"""
        print(f"\nImporting MENTIONS relationships from {file_path}...")
        count = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            batch = []
            
            for row in reader:
                batch.append({
                    'src': row['src'],
                    'dst': row['dst']
                })
                
                if len(batch) >= 1000:
                    self._import_mentions_batch(batch)
                    count += len(batch)
                    print(f"  Imported {count} relationships...")
                    batch = []
            
            if batch:
                self._import_mentions_batch(batch)
                count += len(batch)
        
        print(f"  ✓ Total MENTIONS relationships: {count}")
        return count
    
    def _import_mentions_batch(self, batch):
        """Import a batch of MENTIONS relationships"""
        with self.driver.session() as session:
            query = """
            UNWIND $batch AS row
            MATCH (a:Article {article_id: row.src})
            MATCH (ent:Entity {entity_id: row.dst})
            CREATE (a)-[:MENTIONS]->(ent)
            """
            session.run(query, batch=batch)
    
    def verify_import(self):
        """Verify the import by counting nodes and relationships"""
        print("\n" + "="*60)
        print("IMPORT VERIFICATION")
        print("="*60)
        
        with self.driver.session() as session:
            # Count nodes
            result = session.run("MATCH (a:Article) RETURN count(a) as count")
            articles = result.single()["count"]
            
            result = session.run("MATCH (e:Event) RETURN count(e) as count")
            events = result.single()["count"]
            
            result = session.run("MATCH (ent:Entity) RETURN count(ent) as count")
            entities = result.single()["count"]
            
            # Count relationships
            result = session.run("MATCH ()-[r:HAS_EVENT]->() RETURN count(r) as count")
            has_event = result.single()["count"]
            
            result = session.run("MATCH ()-[r:INVOLVES]->() RETURN count(r) as count")
            involves = result.single()["count"]
            
            result = session.run("MATCH ()-[r:MENTIONS]->() RETURN count(r) as count")
            mentions = result.single()["count"]
            
            print(f"\nNodes:")
            print(f"  Articles:  {articles:,}")
            print(f"  Events:    {events:,}")
            print(f"  Entities:  {entities:,}")
            print(f"  TOTAL:     {articles + events + entities:,}")
            
            print(f"\nRelationships:")
            print(f"  HAS_EVENT: {has_event:,}")
            print(f"  INVOLVES:  {involves:,}")
            print(f"  MENTIONS:  {mentions:,}")
            print(f"  TOTAL:     {has_event + involves + mentions:,}")
            
            # Sample query
            print(f"\nSample data:")
            result = session.run("""
                MATCH (a:Article)-[:HAS_EVENT]->(e:Event)-[:INVOLVES]->(ent:Entity)
                RETURN a.title as title, e.type as event_type, ent.text as entity
                LIMIT 3
            """)
            for record in result:
                print(f"  • {record['title'][:60]}")
                print(f"    Event: {record['event_type']}, Entity: {record['entity']}")


def main():
    print("="*60)
    print("NEO4J DATA IMPORT SCRIPT")
    print("="*60)
    print(f"\nConnecting to Neo4j...")
    print(f"URI: {NEO4J_URI}")
    print(f"User: {NEO4J_USER}")
    
    importer = Neo4jDataImporter(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    try:
        # Ask if user wants to clear database
        response = input("\n⚠️  Clear existing data? (yes/no): ").lower()
        if response == 'yes':
            importer.clear_database()
        
        # Create constraints
        importer.create_constraints()
        
        # Import nodes
        print("\n" + "="*60)
        print("IMPORTING NODES")
        print("="*60)
        
        articles_count = importer.import_articles(os.path.join(DATA_DIR, NODE_FILES["articles"]))
        events_count = importer.import_events(os.path.join(DATA_DIR, NODE_FILES["events"]))
        entities_count = importer.import_entities(os.path.join(DATA_DIR, NODE_FILES["entities"]))
        
        # Import relationships
        print("\n" + "="*60)
        print("IMPORTING RELATIONSHIPS")
        print("="*60)
        
        has_event_count = importer.import_has_event_edges(os.path.join(DATA_DIR, EDGE_FILES["has_event"]))
        involves_count = importer.import_involves_edges(os.path.join(DATA_DIR, EDGE_FILES["involves"]))
        mentions_count = importer.import_mentions_edges(os.path.join(DATA_DIR, EDGE_FILES["mentions"]))
        
        # Verify import
        importer.verify_import()
        
        print("\n" + "="*60)
        print("✓ IMPORT COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nYou can now:")
        print("  • Open the frontend: http://localhost:3000")
        print("  • Access Neo4j Browser: http://localhost:7474")
        print("  • Try the API: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ Error during import: {e}")
        import traceback
        traceback.print_exc()
    finally:
        importer.close()


if __name__ == "__main__":
    main()

