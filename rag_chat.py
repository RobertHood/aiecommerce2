import os
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_groq import ChatGroq

# Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# You must set GROQ_API_KEY environment variable.
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-api-key")

def setup_rag():
    try:
        # 1. Connect to Neo4j
        graph = Neo4jGraph(
            url=NEO4J_URI,
            username=NEO4J_USERNAME,
            password=NEO4J_PASSWORD
        )
        
        # 2. Setup LLM (Groq - free tier, fast)
        llm = ChatGroq(
            temperature=0,
            model_name="llama-3.3-70b-versatile",
            groq_api_key=GROQ_API_KEY
        )
        
        # 3. Create Cypher QA Chain
        chain = GraphCypherQAChain.from_llm(
            llm=llm,
            graph=graph,
            verbose=True,
            return_direct=False,
            allow_dangerous_requests=True,
        )
        
        return chain
        
    except Exception as e:
        print(f"Error setting up RAG (Neo4j might not be running or OpenAI key is missing): {e}")
        return None

def ask_question(chain, question):
    if not chain:
        return "RAG system is not initialized."
    try:
        response = chain.invoke({"query": question})
        return response.get('result')
    except Exception as e:
        return f"Error executing query: {e}"

if __name__ == "__main__":
    print("--- E-commerce AI Chat / RAG ---")
    chain = setup_rag()
    
    if chain:
        print("RAG System initialized. Type 'quit' to exit.")
        while True:
            user_input = input("You: ")
            if user_input.lower() in ['quit', 'exit']:
                break
            
            response = ask_question(chain, user_input)
            print(f"AI Agent: {response}\n")
