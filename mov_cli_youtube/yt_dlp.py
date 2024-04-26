from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, Dict, Generator, Any, List, Tuple

    from mov_cli import Config
    from mov_cli.http_client import HTTPClient
    from mov_cli.scraper import ScraperOptionsT

import yt_dlp

from mov_cli.scraper import Scraper
from mov_cli.utils import EpisodeSelector
from mov_cli import Single, Metadata, MetadataType

__all__ = ("YTDlpScraper",)

class YTDlpScraper(Scraper):
    def __init__(self, config: Config, http_client: HTTPClient, options: Optional[ScraperOptionsT] = None) -> None:
        super().__init__(config, http_client, options)

    def search(self, query: str, limit: Optional[int] = None) -> Generator[Metadata, Any, None]:
        max_videos = 70 if limit is None else limit

        yt_options = {
            "noplaylist": "True", 
            "default_search": "ytsearch", 
            "nocheckcertificate": True, 
            "geo_bypass": True, 
            "extract_flat": "in_playlist", 
            "skip_download": True, 
            "quiet": False if self.config.debug else True, 
            "ignoreerrors": True, 
            "match_filter": self.__yt_dlp_filter(**self.options)
        }

        with yt_dlp.YoutubeDL(yt_options) as ydl:
            info = ydl.extract_info(f"ytsearch{max_videos}:{query}", download = False)

            for key in info["entries"]:

                yield Metadata(
                    id = key["url"], 
                    title = f"{key['title']} ~ {key['uploader']}", 
                    type = MetadataType.SINGLE
                )

    def scrape(
        self, 
        metadata: Metadata, 
        _: EpisodeSelector
    ) -> Single:

        watch_url = metadata.id

        yt_options = {
            "format": "best", 
            "nocheckcertificate": True, 
            "geo_bypass": True, 
            "quiet": False if self.config.debug else True
        }

        audio_url = None

        with yt_dlp.YoutubeDL(yt_options) as ydl:
            info = ydl.extract_info(watch_url, download = False)

            if self.options.get("audio", False):
                url = self.__get_best_stream(info, audio = True)
            else:
                url = self.__get_best_stream(info, video = True)
                audio_url = self.__get_best_stream(info, audio = True)

        return Single(
            url = url, 
            audio_url = audio_url, 
            title = metadata.title, 
            year = metadata.year
        )

    def scrape_episodes(self, _: Metadata) -> Dict[None, int]:
        # Returning None as search does not return any metadata of type series.
        return {None: 1}

    def __get_best_stream(self, ytdlp_info: dict, video: bool = False, audio: bool = False) -> str:
        """Returns the best stream respecting the parameters given."""
        stream_formats_to_sort: List[Tuple[int, str]] = []

        for stream_format in ytdlp_info["formats"]:

            if video is True and stream_format["video_ext"] == "none":
                continue

            if audio is True and stream_format["audio_ext"] == "none":
                continue

            url: str = stream_format["url"]
            quality: int = stream_format["quality"]

            stream_formats_to_sort.append((quality, url))

        stream_formats_to_sort.sort(key = lambda x: x[0], reverse = True)
        return stream_formats_to_sort[0][1]

    def __yt_dlp_filter(self, shorts: bool = False, **kwargs):

        def filter(info, *, incomplete):
            url = info.get("url")

            if shorts is False and "/shorts" in url:
                return "Video is a YouTube short. Pass '--shorts' to the scraper to scrape for them."

        return filter