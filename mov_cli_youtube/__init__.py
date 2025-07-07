from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mov_cli.plugins import PluginHookData

from .pytube import *
from .yt_dlp import *

plugin: PluginHookData = {
    "version": 1, 
    "package_name": "mov-cli-youtube", 
    "scrapers": {
        "DEFAULT": YTDlpScraper, 
        # Fall back to pytube on iOS and Android as their players can't take audio_url. 
        # This will sadly result in slower query and scraping.
        "ANDROID.DEFAULT": PyTubeScraper, 
        "IOS.DEFAULT": PyTubeScraper, 

        "yt-dlp": YTDlpScraper, 
        "pytube": PyTubeScraper, 
    }
}

__version__ = "1.3.9"