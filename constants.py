from typing import List
from enum import Enum
from picard.config import BoolOption, TextOption, Option

PLUGIN_NAME = "ecd2iTat"
PLUGIN_AUTHOR = "cy1der"
PLUGIN_DESCRIPTION = "Convert disambiguations containing \"explicit\"/\"clean\" (and others) keywords to proper tags so clients can display the 🅴/🅲 symbol"
PLUGIN_VERSION = "1.0.1"
PLUGIN_API_VERSIONS = ["2.7", "2.8", "2.9", "2.10", "2.11", "2.12", "2.13"]
PLUGIN_LICENSE = "GPL-2.0-or-later"
PLUGIN_LICENSE_URL = "https://www.gnu.org/licenses/gpl-2.0.html"
PLUGIN_USER_GUIDE_URL = "https://github.com/cy1der/ecd2iTat"

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

CONFIG_OPTIONS: List[Option] = [
    TextOption("setting", "ecd2itat_explicit_keywords", ", ".join(DEFAULT_EXPLICIT_KEYWORDS)),
    TextOption("setting", "ecd2itat_clean_keywords", ", ".join(DEFAULT_CLEAN_KEYWORDS)),
    BoolOption("setting", "ecd2itat_save_rtng", False),
    BoolOption("setting", "ecd2itat_strip_keyword_from_disambiguation", False),
]