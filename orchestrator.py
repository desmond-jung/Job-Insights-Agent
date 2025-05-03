from functions.scraper import scrape_jobs
from functions.scraper import embed_jobs  #

def main():
    jobs = scrape_jobs("Data Scientist", "Los Angeles County", num_jobs=10)
    job_descriptions = [job['description'] for job in jobs]
    embeddings = embed_jobs(job_descriptions, method="sbert")
    # Optionally: build_faiss_index(embeddings)
    # Optionally: save jobs and embeddings

if __name__ == "__main__":
    main() 