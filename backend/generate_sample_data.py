"""
Sample Data Generator for Analytical Subsystem
Generates sample news data for testing the system.
"""

from datetime import datetime, timedelta
import random
from typing import List, Dict
import uuid


class SampleDataGenerator:
    """Generate sample news data for testing."""
    
    EVENT_TYPES = [
        "Conflict.Attack",
        "Conflict.AirStrike",
        "Diplomacy.Sanction",
        "Diplomacy.Meeting",
        "Diplomacy.Treaty",
        "Political.Election",
        "Political.Protest",
        "Economic.Trade",
    ]
    
    ENTITIES = [
        ("Russia", "GPE"),
        ("United States", "GPE"),
        ("China", "GPE"),
        ("Ukraine", "GPE"),
        ("European Union", "ORG"),
        ("NATO", "ORG"),
        ("United Nations", "ORG"),
        ("Vladimir Putin", "PERSON"),
        ("Joe Biden", "PERSON"),
        ("Xi Jinping", "PERSON"),
    ]
    
    SOURCES = [
        "Reuters",
        "BBC",
        "CNN",
        "Associated Press",
        "The Guardian",
        "New York Times",
    ]
    
    TRIGGER_WORDS = {
        "Conflict.Attack": ["attacked", "struck", "bombed", "assault"],
        "Conflict.AirStrike": ["airstrike", "bombed", "aerial attack"],
        "Diplomacy.Sanction": ["sanctioned", "penalties", "restrictions"],
        "Diplomacy.Meeting": ["met", "meeting", "talks", "summit"],
        "Diplomacy.Treaty": ["treaty", "agreement", "accord"],
        "Political.Election": ["election", "voted", "ballot"],
        "Political.Protest": ["protest", "demonstration", "rally"],
        "Economic.Trade": ["trade", "tariff", "export", "import"],
    }
    
    @staticmethod
    def generate_sample_data(num_articles: int = 100) -> List[str]:
        """Generate Cypher queries to create sample data."""
        queries = []
        
        # Create entities
        for entity_text, entity_label in SampleDataGenerator.ENTITIES:
            entity_id = f"ent_{entity_text.replace(' ', '_').lower()}"
            query = f"""
            CREATE (ent:Entity {{
                entity_id: '{entity_id}',
                text: '{entity_text}',
                label: '{entity_label}'
            }})
            """
            queries.append(query)
        
        # Generate articles, events, and relationships
        start_date = datetime.now() - timedelta(days=90)
        
        for i in range(num_articles):
            article_id = f"art_{str(uuid.uuid4())[:8]}"
            event_id = f"evt_{str(uuid.uuid4())[:8]}"
            
            # Random date within last 90 days
            days_offset = random.randint(0, 90)
            pub_date = start_date + timedelta(days=days_offset)
            
            # Random event type
            event_type = random.choice(SampleDataGenerator.EVENT_TYPES)
            trigger_word = random.choice(SampleDataGenerator.TRIGGER_WORDS[event_type])
            
            # Random entities (2-3)
            involved_entities = random.sample(SampleDataGenerator.ENTITIES, k=random.randint(2, 3))
            entity_texts = [e[0] for e in involved_entities]
            
            # Random source
            source = random.choice(SampleDataGenerator.SOURCES)
            
            # Generate title
            title = f"{entity_texts[0]} {trigger_word} {entity_texts[1]}"
            
            # Confidence score
            confidence = round(random.uniform(0.6, 0.95), 2)
            
            # Create article
            query = f"""
            CREATE (a:Article {{
                article_id: '{article_id}',
                title: '{title}',
                published_date: datetime('{pub_date.isoformat()}'),
                source: '{source}',
                link: 'https://example.com/{article_id}'
            }})
            """
            queries.append(query)
            
            # Create event
            query = f"""
            CREATE (e:Event {{
                event_id: '{event_id}',
                type: '{event_type}',
                trigger_word: '{trigger_word}',
                confidence: {confidence},
                article_id: '{article_id}'
            }})
            """
            queries.append(query)
            
            # Create relationships
            query = f"""
            MATCH (a:Article {{article_id: '{article_id}'}})
            MATCH (e:Event {{event_id: '{event_id}'}})
            CREATE (a)-[:HAS_EVENT]->(e)
            """
            queries.append(query)
            
            # Link entities
            for entity_text, entity_label in involved_entities:
                entity_id = f"ent_{entity_text.replace(' ', '_').lower()}"
                
                query = f"""
                MATCH (a:Article {{article_id: '{article_id}'}})
                MATCH (e:Event {{event_id: '{event_id}'}})
                MATCH (ent:Entity {{entity_id: '{entity_id}'}})
                CREATE (a)-[:MENTIONS]->(ent)
                CREATE (e)-[:INVOLVES]->(ent)
                """
                queries.append(query)
        
        return queries
    
    @staticmethod
    def export_to_file(queries: List[str], filename: str = "sample_data.cypher"):
        """Export queries to a Cypher file."""
        with open(filename, 'w') as f:
            f.write("// Sample Data for Analytical Subsystem\n")
            f.write("// Generated automatically for testing\n\n")
            for query in queries:
                f.write(query.strip() + ";\n\n")
        print(f"Sample data exported to {filename}")
        print(f"Total queries: {len(queries)}")
        print(f"\nTo import into Neo4j:")
        print(f"1. Open Neo4j Browser (http://localhost:7474)")
        print(f"2. Copy and paste the contents of {filename}")
        print(f"3. Execute the queries")


if __name__ == "__main__":
    print("Generating sample data...")
    queries = SampleDataGenerator.generate_sample_data(num_articles=100)
    SampleDataGenerator.export_to_file(queries)
    print("\nDone! Sample data ready for import.")

