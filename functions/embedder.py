from sentence_transformers import SentenceTransformer
import openai

def embed_jobs(job_descriptions, method="sbert"):
    embeddings = None
    if method == "sbert":
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings = model.encode(job_descriptions, convert_to_tensor=False)
    elif method == "openai":
        embeddings = []
        for desc in job_descriptions:
            response = openai.Embedding.create(
                input=desc,
                model="text-embedding-3-small"
            )
            embeddings.append(response['data'][0]['embedding'])
    else:
        raise ValueError("Unknown embedding method: choose 'sbert' or 'openai'.")
    return embeddings