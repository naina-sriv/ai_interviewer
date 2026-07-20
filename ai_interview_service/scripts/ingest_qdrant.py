import os
import csv
from qdrant_client import QdrantClient

def ingest_data():
    print("Initializing Qdrant Client...")
    # Use a local database stored in a folder so it persists, without needing a cloud key
    # (In production, replace this with url="your-cluster-url", api_key="your-key")
    db_path = os.path.join(os.path.dirname(__file__), "..", "qdrant_db")
    client = QdrantClient(path=db_path)
    
    collection_name = "company_questions"
    
    print("Reading CSV data...")
    csv_path = os.path.join(os.path.dirname(__file__), "mock_questions.csv")
    
    documents = []
    metadata = []
    ids = []
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for i, row in enumerate(reader):
            documents.append(row['question'])
            metadata.append({
                "company": row['company'].lower().strip(),
                "job_title": row['job_title']
            })
            ids.append(i + 1)
            
    print(f"Loaded {len(documents)} questions. Adding to Qdrant...")
    
    # Qdrant's .add() method automatically generates embeddings using 'fastembed'
    # This is much lighter than sentence-transformers and runs completely locally!
    client.add(
        collection_name=collection_name,
        documents=documents,
        metadata=metadata,
        ids=ids
    )
    
    print("✅ Successfully ingested all questions into the local Qdrant Vector DB!")

if __name__ == "__main__":
    ingest_data()
