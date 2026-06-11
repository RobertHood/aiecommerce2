import pandas as pd
from neo4j import GraphDatabase
import os

# Neo4j connection details from env or default for local docker
URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
AUTH = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "password"))

def clear_db(tx):
    tx.run("MATCH (n) DETACH DELETE n")

def create_indexes(tx):
    tx.run("CREATE INDEX user_id_idx IF NOT EXISTS FOR (u:User) ON (u.id)")
    tx.run("CREATE INDEX product_id_idx IF NOT EXISTS FOR (p:Product) ON (p.id)")

def ingest_data(tx, df):
    # Using UNWIND for bulk import and MATCH/MERGE
    query = """
    UNWIND $rows AS row
    MERGE (u:User {id: row.user_id})
    MERGE (p:Product {id: row.product_id})
    WITH u, p, row
    CALL apoc.create.relationship(u, toUpper(row.action), {timestamp: row.timestamp}, p) YIELD rel
    RETURN count(rel)
    """
    
    # Alternatively without APOC if not installed
    query_no_apoc = """
    UNWIND $rows AS row
    MERGE (u:User {id: row.user_id})
    MERGE (p:Product {id: row.product_id})
    WITH u, p, row
    
    // Create relationship based on action
    FOREACH(ignoreMe IN CASE WHEN row.action = 'view' THEN [1] ELSE [] END |
        CREATE (u)-[:VIEWED {timestamp: row.timestamp}]->(p))
    FOREACH(ignoreMe IN CASE WHEN row.action = 'click' THEN [1] ELSE [] END |
        CREATE (u)-[:CLICKED {timestamp: row.timestamp}]->(p))
    FOREACH(ignoreMe IN CASE WHEN row.action = 'add_to_cart' THEN [1] ELSE [] END |
        CREATE (u)-[:ADDED_TO_CART {timestamp: row.timestamp}]->(p))
    """
    
    # Convert dataframe to list of dicts
    records = df.to_dict('records')
    tx.run(query_no_apoc, rows=records)

if __name__ == "__main__":
    print("Connecting to Neo4j...")
    try:
        driver = GraphDatabase.driver(URI, auth=AUTH)
        driver.verify_connectivity()
        
        print("Loading data...")
        df = pd.read_csv('data_user500.csv')
        
        with driver.session() as session:
            print("Clearing database...")
            session.execute_write(clear_db)
            print("Creating indexes...")
            session.execute_write(create_indexes)
            print("Ingesting data to Neo4j...")
            session.execute_write(ingest_data, df)
            
        print("Knowledge Base Graph successfully created.")
        driver.close()
    except Exception as e:
        print(f"Error connecting to Neo4j or establishing the graph: {e}")
        print("\nMake sure Neo4j is running. You can start it via Docker with:")
        print("docker-compose up -d neo4j")
