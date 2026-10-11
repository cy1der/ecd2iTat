from typing import Any, Dict, List
from enum import Enum

class iTunesAdvisory(Enum):
    EXPLICIT = 1
    CLEAN = 2

class rtng(Enum):
    EXPLICIT = 4
    CLEAN = 2

DEFAULT_EXPLICIT_KEYWORDS: List[str] = [
    "explicit release version",
    "dirty release version",
    "explicit version",
    "dirty version",
    "explicit",
    "dirty"
]

DEFAULT_CLEAN_KEYWORDS: List[str] = [
    "censored release version",
    "clean release version",
    "censored version",
    "clean version",
    "censored",
    "clean"
]

CONFIG_OPTIONS: Dict[str, Any] = {
    "explicit_keywords": ", ".join(DEFAULT_EXPLICIT_KEYWORDS),
    "clean_keywords": ", ".join(DEFAULT_CLEAN_KEYWORDS),
    "save_rtng": False,
    "strip_keyword_from_disambiguation": False,
}

# Plugin API v2 stored options in the global "setting" section with an "ecd2itat_" prefix
LEGACY_OPTION_PREFIX = "ecd2itat_"
