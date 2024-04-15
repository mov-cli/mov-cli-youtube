from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mov_cli.plugins import PluginHookData

from .youtube import *

plugin: PluginHookData = {
    "version": 1, 
    "package_name": "mov-cli-youtube", 
    "scrapers": {
        "DEFAULT": YouTubeScraper, 
    }
}

__version__ = "1.2.0alpha1"