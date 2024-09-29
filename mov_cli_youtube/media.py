from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional

from dataclasses import dataclass, field

from mov_cli.media import Metadata, MetadataType

@dataclass
class VideoMetadata(Metadata):
    # NOTE: You can't set fields without defaults when inheriting from Metadata.
    type: MetadataType = field(init = False, default = MetadataType.SINGLE)

    duration: float = field(default = 0.0)
    view_count: int = field(default = 0)

    @property
    def display_release_date(self) -> str:
        if self.release_date is None:
            return ""

        release_date_string = self.release_date.strftime("%b %d, %Y")

        return f"({release_date_string})"

    @property
    def preview_details(self) -> Optional[str]:
        details = ""

        if self.description:
            details += self.description

        # TODO: Make duration and views human readable (e.g 32 minutes, 2.5k views)
        details += f"{self.duration} second(s) • {self.view_count} view(s)"

        return details