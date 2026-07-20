import os
from qdrant_client import QdrantClient

def get_company_questions(company_name: str, job_title: str = "") -> list[str]:
    """Retrieve commonly asked questions for a specific company from the Qdrant Vector DB."""
    if not company_name:
        return []
    
    normalized_name = company_name.lower().strip()
    
    try:
        # Connect to the local Qdrant database
        db_path = os.path.join(os.path.dirname(__file__), "..", "qdrant_db")
        client = QdrantClient(path=db_path)
        
        # We query using the company name and job title to find semantically relevant questions
        query_text = f"{normalized_name} {job_title} interview questions"
        
        # Search the database, filtering by the company metadata
        # Qdrant's query() method automatically embeds the text using 'fastembed'
        results = client.query(
            collection_name="company_questions",
            query_text=query_text,
            query_filter={
                "must": [
                    {
                        "key": "company",
                        "match": {
                            "value": normalized_name
                        }
                    }
                ]
            },
            limit=5
        )
        
        # Extract the text of the questions from the search results
        return [hit.document for hit in results]
        
    except Exception as e:
        print(f"Failed to query Qdrant Vector DB: {e}")
        return []
