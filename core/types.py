"""Type definitions for Suno MCP server."""

from typing import Literal

# Suno model versions
SunoModel = Literal[
    "chirp-v3-0",
    "chirp-v3-5",
    "chirp-v4",
    "chirp-v4-5",
    "chirp-v4-5-plus",
    "chirp-v5",
    "chirp-v5-5",
]

# Lyrics model versions (different from audio models)
LyricsModel = Literal["default", "remi-v1"]

# Vocal gender options (v4.5+ only)
VocalGender = Literal["", "f", "m"]

# Default model
DEFAULT_MODEL: SunoModel = "chirp-v4-5"

# Default lyrics model
DEFAULT_LYRICS_MODEL: LyricsModel = "default"
