from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional, Generator, Any

    from mov_cli import Config
    from mov_cli.http_client import HTTPClient
    from mov_cli.scraper import ScraperOptionsT

import os
import sys
from pytubefix import YouTube, Search

from mov_cli.scraper import Scraper
from mov_cli.utils import EpisodeSelector, get_temp_directory, what_platform
from mov_cli import Single, Metadata, MetadataType, ExtraMetadata

from mov_cli.media import Quality

__all__ = ("PyTubeScraper",)

class PyTubeScraper(Scraper):
    def __init__(self, config: Config, http_client: HTTPClient, options: Optional[ScraperOptionsT] = None) -> None:
        super().__init__(config, http_client, options)

    def search(self, query: str, limit: Optional[int] = None) -> Generator[Metadata, Any, None]:
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
                type = MetadataType.SINGLE, 
                year = str(video.publish_date.year), 
                image_url = video.thumbnail_url, 
                extra_func = lambda: self.__scrape_extra(video)
            )

        # restore the console.
        sys.stderr = sys.__stderr__

    def scrape(self, metadata: Metadata, _: EpisodeSelector) -> Single:
        audio_only: bool = self.options.get("audio", False)
        subtitles = []

        watch_url = metadata.id
        video = YouTube(watch_url)

        if audio_only:
            url = video.streams.get_audio_only().url

        elif not self.config.resolution == Quality.AUTO:
            url = video.streams.get_by_resolution(self.config.resolution.apply_p()).url

            if url is None:
                url = video.streams.get_highest_resolution().url

        else:
            url = video.streams.get_highest_resolution().url
    
        for caption in video.captions:
            if caption.code.startswith(self.config.language.iso639_1):
                platform = what_platform()

                temp = get_temp_directory(platform).joinpath(video.video_id)

                with temp.open("w", encoding = "utf-8") as f:
                    f.write(
                        caption.generate_srt_captions()
                    )
                
                subtitles.append(temp)

        return Single(
            url = url, 
            title = metadata.title, 
            year = metadata.year,
            subtitles = subtitles
        )

    def __scrape_extra(self, key: YouTube) -> ExtraMetadata:
        return ExtraMetadata(
            description = key.description
        )
