from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional, Dict

    from mov_cli import Config
    from mov_cli.http_client import HTTPClient

from pytube import YouTube

from mov_cli import utils
from mov_cli.scraper import Scraper
from mov_cli import Series, Movie, Metadata, MetadataType

__all__ = ("TestScraper",)

class TestScraper(Scraper):
    def __init__(self, config: Config, http_client: HTTPClient) -> None:
        self.creative_common_films = [
            Metadata(id = "https://youtu.be/aqz-KE-bpKQ", title = "Big Buck Bunny", type = MetadataType.MOVIE, year = "2008"),
            Metadata(id = "https://www.youtube.com/watch?v=BBgghnQF6E4", title = "Steamboat Willie", type = MetadataType.MOVIE, year = "1928"),
            Metadata(id = "https://cdn.devgoldy.xyz/ricky.webm", title = "Ricky :)", type = MetadataType.MOVIE, year = "2009")
        ]

        super().__init__(config, http_client)

    def search(self, query: str, limit: int = None) -> List[Metadata]:
        # This is where you would want to implement searching for your scraper. 
        # This method is called whenever the user searches for something.

        return self.creative_common_films # NOTE: In my case I already know the media so let's just my hardcoded metadata.

    def scrape(self, metadata: Metadata, episode: Optional[utils.EpisodeSelector] = None) -> Series | Movie:
        if episode is None:
            episode = utils.EpisodeSelector()

        url = metadata.id

        if "https://youtu.be" in url:
            url = YouTube(url).streams.get_highest_resolution().url

        # NOTE: I could have just dropped series as all the media in my list are 
        # films and not series but I'll leave it in here as an example.
        if metadata.type == MetadataType.SERIES:
            return Series(
                url = url, 
                title = metadata.title, 
                referrer = url, 
                episode = episode.episode, 
                season = episode.season,
                subtitles = None
            )

        return Movie(
            url = url, 
            title = metadata.title, 
            referrer = url, 
            year = metadata.year,
            subtitles = None
        )

    def scrape_metadata_episodes(self, metadata: Metadata) -> Dict[int | None, int]:
        # NOTE: Let's just return None for now as we don't have any series in the list hence no episodes.
        return {None: 1}