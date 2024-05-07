from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional, Dict, Generator, Any

    from mov_cli import Config
    from mov_cli.http_client import HTTPClient
    from mov_cli.scraper import ScraperOptionsT

import os
import sys
from pytubefix import YouTube, Search

from mov_cli.scraper import Scraper
from mov_cli.utils import EpisodeSelector
from mov_cli import Single, Metadata, MetadataType

__all__ = ("PyTubeScraper",)

class PyTubeScraper(Scraper):
    def __init__(self, config: Config, http_client: HTTPClient, options: Optional[ScraperOptionsT] = None) -> None:
        super().__init__(config, http_client, options)

    def search(self, query: str, limit: int = None) -> Generator[Metadata, Any, None]:
        search_query = Search(query)
        search_results: List[YouTube] = search_query.videos

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

    def scrape(self, metadata: Metadata, _: EpisodeSelector) -> Single:
        audio_only: bool = self.options.get("audio", False)

        watch_url = metadata.id
        video = YouTube(watch_url)

        if audio_only:
            url = video.streams.get_audio_only().url

        elif self.config.resolution is not None:
            url = video.streams.get_by_resolution(f"{self.config.resolution}p").url

            if url is None:
                url = video.streams.get_highest_resolution().url

        else:
            url = video.streams.get_highest_resolution().url

        return Single(
            url = url, 
            title = metadata.title, 
            year = metadata.year
        )

    def scrape_episodes(self, metadata: Metadata, **kwargs) -> Dict[None, int]:
        # Returning None as search does not return any metadata of type series.
        return {None: 1}