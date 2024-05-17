from mov_cli import Config, Scraper, Metadata, Single
from mov_cli.utils import EpisodeSelector
from mov_cli.http_client import HTTPClient
from mov_cli_youtube import YTDlpScraper, PyTubeScraper
from typing import Dict

query = "Flight 370"

def scrapers() -> Dict[str, Scraper]:
    config = Config()
    http = HTTPClient(config)

    return {
        "ytdlp": YTDlpScraper(config, http),
        "pytube": PyTubeScraper(config, http)
    }

def search(scrapers: Dict[str, Scraper]) -> Dict[str, Metadata]:
    results = {}

    for key, scraper in scrapers.items():
        results[key] = next(
            scraper.search(query)
        )

        print(f"{key}: Searching for {query}")

    return results

def scrape(scrapers: Dict[str, Scraper], search: Dict[str, Metadata]) -> Dict[str, Single]:
    results = {}

    episode = EpisodeSelector()

    for key, scraper in scrapers.items():
        if search.get(key):
            results[key] = scraper.scrape(
                search.get(key), episode
            )

            print(f"{key}: scraping {search.get(key).id}")
        else:
            raise Exception("No search result")
        
    return results

if __name__ == "__main__":
    plugin_scrapers = scrapers()
    search_results = search(plugin_scrapers)
    scrape_results = scrape(plugin_scrapers, search_results)
    for key, result in scrape_results.items():
        print(f"{key} result: {result.url}")