import json

from apify_client import ApifyClient


def get_serp_results(client: ApifyClient,
                     query_string: str,
                     results_per_page: int = 40,
                     max_num_page: int = 5,
                     retry=True
                     ):
    # Prepare the Actor input
    run = run_apify_serp(client, max_num_page, query_string, results_per_page)
    return_items = []
    # Fetch and print Actor results from the run's dataset (if there are any)
    if run['status'] != 'SUCCEEDED':
        print(f"{ run = }. \n\n\n RETRYING .. ")

        if retry:
            run = run_apify_serp(client, max_num_page, query_string, results_per_page)

        if run['status'] != 'SUCCEEDED':
            return run['statusMessage'], run

    # Fetch and print Actor results from the run's dataset (if there are any)
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        return_items.append(item)

    return {"results":return_items}


def run_apify_serp(client, max_num_page, query_string, results_per_page):
    run_input = {
        "queries": query_string,
        "maxPagesPerQuery": max_num_page,
        "resultsPerPage": results_per_page,
        "mobileResults": False,
        "languageCode": "",
        "maxConcurrency": 2,
        "saveHtml": False,
        "saveHtmlToKeyValueStore": False,
        "includeUnfilteredResults": False,
        "customDataFunction": """async ({ input, $, request, response, html }) => {
      return {
        pageTitle: $('title').text(),
      };
      };""",
    }
    print(f"{ client = }")
    # Run the Actor and wait for it to finish
    run = client.actor("apify~google-search-scraper").call(run_input=run_input)
    return run


if __name__ == "__main__":
    apf_tok = "apify_api_b9YOZqAU6MCgRRDrsaSJ6Cy9NhjuTN2Mf0eJ"
    # Initialize the ApifyClient with your API token
    client = ApifyClient(apf_tok)
    actor = client.actor("apify~google-search-scraper").get()
    actor_params = client.actor("apify~google-search-scraper").params
    for k, v in actor.items():
        print(f" {k} : {v} ")
    print(f"{ actor_params = }")
    res = get_serp_results(client, "revenue for Mollie from zoominfo")
    out = json.dumps(res)
    print(f"Final {out}")
