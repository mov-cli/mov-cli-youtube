from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, Dict, Generator, Any

    from mov_cli import Config
    from mov_cli.http_client import HTTPClient

import yt_dlp
from pytube import YouTube

from mov_cli.scraper import Scraper
from mov_cli.utils import EpisodeSelector
from mov_cli import Series, Movie, Metadata, MetadataType

__all__ = ("YouTubeScraper",)

class YouTubeScraper(Scraper):
    def __init__(self, config: Config, http_client: HTTPClient) -> None:
        super().__init__(config, http_client)

    def search(self, query: str, limit: int = None, **kwargs) -> Generator[Metadata, Any, None]:
        max_videos = 100 if limit is None else limit

        yt_options = {
            "format": "best", 
            "noplaylist":"True", 
            "default_search": "ytsearch", 
            "nocheckcertificate": True, 
            "geo_bypass": True, 
            "extract_flat": "in_playlist", 
            "skip_download": True, 
            "quiet": False if self.config.debug else True, 
            "ignoreerrors": True, 
            "match_filter": self.__yt_dlp_filter(**kwargs)
        }

        with yt_dlp.YoutubeDL(yt_options) as ydl:
            info = ydl.extract_info(f"ytsearch{max_videos}:{query}", download = False)

            for key in info["entries"]:

                yield Metadata(
                    id = key["url"], 
                    title = f"{key['title']} ~ {key['uploader']}", 
                    type = MetadataType.MOVIE, 
                    year = key["release_timestamp"]
                )

    def scrape(
        self, 
        metadata: Metadata, 
        episode: Optional[EpisodeSelector] = None, 
        audio = False, 
        **kwargs: Dict[str, bool]
    ) -> Series | Movie:

        if episode is None:
            episode = EpisodeSelector()

        watch_url = metadata.id
        video = YouTube(watch_url)

        if audio:
            url = video.streams.get_audio_only().url
        else:
            url = video.streams.get_highest_resolution().url

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

    def __yt_dlp_filter(self, shorts: bool = False, **kwargs):

        def filter(info, *, incomplete):
            url = info.get("url")

            if shorts is False and "/shorts" in url:
                return "Video is a youtube short. Pass '--shorts' to the scraper to scrape for shorts."

        return filter