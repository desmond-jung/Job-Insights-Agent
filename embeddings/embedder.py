from sentence_transformers import SentenceTransformer
import openai
import numpy as np
import sqlite3
import faiss
import json
from typing import List, Dict, Any, Tuple
from qdrant_client import QdrantClient

class JobEmbedder:
    def __init__(self):
        # Load embedding model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.client = QdrantClient("localhost", port=6333)

    def create_embeddings(self, text: str) -> np.ndarray:
        return self.model.encode([text])[0]
    
    def prepare_job_text(self, job: Dict[str, Any]) -> str:
        """ Combine job details into single text"""
        title = job.get('title', '')
        description = job.get('description', '')
        company = job.get('company_name', '')

        return f"(Title: {title}\nCompany: {company}\nDescription: {description})"
    
    def add_job(self, job: Dict[str, Any]) -> int:
        # Prepare text and create embedding
        job_text = self.prepare_job_text(job)
        embedding = self.create_embeddings(job_text)
        
        # Add to Qdrant
        self.client.upsert(
            collection_name="jobs",
            points=[{
                "id": job["job_id"],
                "vector": embedding.tolist(),
                "payload": {
                    "title": job["title"],
                    "company": job["company_name"]
                }
            }]
        )

def embed_jobs(job_descriptions, method="sbert"):
    """Generate embeddings for job descriptions.
    
    Args:
        job_descriptions (list): List of job description strings
        method (str): Embedding method ("sbert" or "openai")
    
    Returns:
        list: List of embeddings
    """
    if method == "sbert":
        # Use SentenceTransformers
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings = model.encode(job_descriptions)
        return embeddings.tolist()
    elif method == "openai":
        # Use OpenAI embeddings
        client = openai.OpenAI()
        embeddings = []
        for description in job_descriptions:
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=description
            )
            embeddings.append(response.data[0].embedding)
        return embeddings
    else:
        raise ValueError(f"Unknown embedding method: {method}")
