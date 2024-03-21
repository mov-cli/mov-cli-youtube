from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional, Dict, Generator, Any

    from mov_cli import Config
    from mov_cli.http_client import HTTPClient

import os
import sys
from pytube import YouTube, Search

from mov_cli import utils
from mov_cli.scraper import Scraper
from mov_cli import Series, Movie, Metadata, MetadataType

__all__ = ("YouTubeScraper",)

class YouTubeScraper(Scraper):
    def __init__(self, config: Config, http_client: HTTPClient) -> None:
        super().__init__(config, http_client)

    def search(self, query: str, limit: int = None) -> Generator[Metadata, Any, None]:
        search_query = Search(query)
        search_results: List[YouTube] = search_query.results

        max_videos = 20 if limit is None else limit

        # suppress pytube's stupid errors from getting to the console and ruining fzf output.
        sys.stderr = open(os.devnull, "w")

        for index, video in enumerate(search_results):
            if (index + 1) == len(search_results) and not (index + 1) >= max_videos:
                search_query.get_next_results()

            yield Metadata(
                id = video.watch_url, 
                title = f"{video.title} ~ {video.author}", 
                type = MetadataType.MOVIE, 
                year = str(video.publish_date.year)
            )

        # restore the console.
        sys.stderr = sys.__stderr__

    def scrape(self, metadata: Metadata, episode: Optional[utils.EpisodeSelector] = None, **kwargs) -> Series | Movie:
        if episode is None:
            episode = utils.EpisodeSelector()

        watch_url = metadata.id
        url = YouTube(watch_url).streams.get_highest_resolution().url

        return Movie(
            url = url, 
            title = metadata.title, 
            referrer = "", 
            year = metadata.year, 
            subtitles = None
        )

    def scrape_episodes(self, metadata: Metadata, **kwargs) -> Dict[None, int]:
        # Returning None as search does not return any metadata of type series.
        return {None: 1}