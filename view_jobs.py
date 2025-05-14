from functions.database import list_all_jobs

if __name__ == "__main__":
    jobs = list_all_jobs()
    print(f"Total jobs in database: {len(jobs)}\n")
    for i, job in enumerate(jobs, 1):
        print(f"Job #{i}")
        for k, v in job.items():
            print(f"  {k}: {v}")
        print("-" * 40)
        if i >= 10:
            print("... (showing first 10 jobs only)")
            break 