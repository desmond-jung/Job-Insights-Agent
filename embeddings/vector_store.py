import faiss
import numpy as np

def build_faiss_index(embeddings, index_path = "jobs.index"):
    # store embeddings in numpy array
    embeddings = np.array(embeddings).astype('float32')

    embedding_dim = embeddings.shape[1]
    # creates FAISS index using euclidean distance - computes distance on the fly to give indicies of nearest neighbors
    index = faiss.IndexFlatL2(embedding_dim)
    index.add(embeddings)
    faiss.write_index(index, index_path)
    return index

def load_faiss_index(index_path = "jobs.index"):
    # load previos saved index from disk
    return faiss.read_index(index_path)

def search_faiss_index(index, query_embedding, k=5):
    D, I = index.search(query_embedding, k)
    return D, I