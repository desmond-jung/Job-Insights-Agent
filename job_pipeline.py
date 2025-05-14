from functions.company_generator import generate_company_list, enrich_company_data, validate_careers_url
from functions.careers_finder import discover_careers_url

def main():
    companies = generate_company_list()
    enriched = enrich_company_data(companies)
    for company in enriched:
        careers_url = company.get("careers_page_url")
        # Step 1: Try to validate the LLM-provided careers page URL
        if careers_url and validate_careers_url(careers_url):
            company["validated_careers_url"] = careers_url
        else:
            # Step 2: Fallback to discovering the careers page from the domain
            domain = company.get("domain")
            if domain:
                if not domain.startswith("http"):
                    domain = "https://" + domain
                discovered_url = discover_careers_url(domain)
                company["validated_careers_url"] = discovered_url
            else:
                company["validated_careers_url"] = None

    # Print or use the results
    for company in enriched:
        print(company)

if __name__ == "__main__":
    main()