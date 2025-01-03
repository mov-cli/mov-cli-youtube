from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, Generator, Any, List, Tuple, TypedDict

    from mov_cli import Config
    from mov_cli.http_client import HTTPClient
    from mov_cli.scraper import ScraperOptionsT

    ThumbnailData = TypedDict(
        "ThumbnailData",
        {
            "url": str, 
            "width": int, 
            "height": int
        }
    )

import yt_dlp

from mov_cli import ExtraMetadata, Metadata, MetadataType, Quality, Single
from mov_cli.scraper import Scraper
from mov_cli.utils import EpisodeSelector

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
                    type = MetadataType.SINGLE,
                    image_url = self.__get_best_thumbnail(key["thumbnails"]),
                    extra_func = lambda: self.__scrape_extra(key)
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

        subtitles = []
        audio_url = None

        with yt_dlp.YoutubeDL(yt_options) as ydl:
            info = ydl.extract_info(watch_url, download = False)

            if self.options.get("audio", False):
                url = self.__get_best_stream(info, audio = True)
            else:
                url = self.__get_best_stream(info, video = True)

                audio_url = self.__get_best_stream(
                    info,
                    audio = True,
                    ensure_correct_audio_localisation = self.options.get("disable_audio_l10n", True)
                )

            for lang_code, caption_data in info.get("subtitles", {}).items():
                if lang_code.startswith(self.config.language.iso639_1):
                    for caption in caption_data:
                        if caption.get("ext") == "vtt":
                            subtitles.append(caption.get("url"))

            for lang_code, caption_data in info.get("automatic_captions", {}).items():
                if lang_code == self.config.language.iso639_1:
                    for caption in caption_data:
                        if caption.get("ext") == "vtt":
                            subtitles.append(caption.get("url"))

        return Single(
            url = url, 
            audio_url = audio_url, 
            title = metadata.title, 
            year = metadata.year,
            subtitles = subtitles
        )

    def __get_best_stream(self, ytdlp_info: dict, video: bool = False, audio: bool = False, ensure_correct_audio_localisation: bool = True) -> str:
        """Returns the best stream respecting the parameters given."""
        stream_formats_to_sort: List[Tuple[int, str]] = []

        if video is False and audio is False:
            raise ValueError("Either video or audio arg must be True in '__get_best_stream'!")

        for stream_format in ytdlp_info["formats"]:

            if video is True and stream_format["video_ext"] == "none":
                continue

            if audio is True:

                if stream_format["audio_ext"] == "none":
                    continue

                if ensure_correct_audio_localisation and not stream_format["language"] == self.config.language.iso639_1:
                    continue

            if (
                # Only filter when not "auto"
                self.config.resolution != Quality.AUTO
                and stream_format.get("height")
                and stream_format["height"] > self.config.resolution.value
            ):
                continue

            url: str = stream_format["url"]
            quality: int = stream_format["quality"]

            stream_formats_to_sort.append((quality, url))

        # To absolutely ensure this shit doesn't blow up.
        if len(stream_formats_to_sort) == 0 and audio is True:
            self.logger.warning(
                "Couldn't find the right audio for your currently selected language so audio " \
                    "localisation will be disabled and the first audio from the YouTube video will be selected."
            )
            return self.__get_best_stream(
                ytdlp_info, audio = True, ensure_correct_audio_localisation = False
            )

        stream_formats_to_sort.sort(key = lambda x: x[0], reverse = True)
        return stream_formats_to_sort[0][1]

    def __get_best_thumbnail(self, thumbnails_data: List[ThumbnailData]) -> Optional[str]:
        """Returns the URL of the best thumbnail."""
        if len(thumbnails_data) == 0:
            return None

        thumbnails_data.sort(key = lambda x: x["height"], reverse = True)
        return thumbnails_data[0]["url"]

    def __yt_dlp_filter(self, shorts: bool = False, **kwargs):

        def filter(info, *, incomplete):
            url = info.get("url")

            if shorts is False and "/shorts" in url:
                return "Video is a YouTube short. Pass '--shorts' to the scraper to scrape for them."

        return filter

    def __scrape_extra(self, key: dict) -> ExtraMetadata:
        with yt_dlp.YoutubeDL() as ydl:
            info = ydl.extract_info(key["url"], download = False)

        return ExtraMetadata(
            description = info["description"],
            genres = info["categories"]
        )