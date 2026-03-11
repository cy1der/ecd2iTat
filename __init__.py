from picard import config, log
from picard.ui.options import OptionsPage, register_options_page
from picard.metadata import register_track_metadata_processor
from PyQt5 import QtWidgets

from .constants import *

def process_track(_, metadata, track, __):    
    disambiguation = track["recording"]["disambiguation"] if "disambiguation" in track["recording"] else ""
    album_disambiguation = metadata["~releasecomment"] if "~releasecomment" in metadata else ""

    explicit_keywords = config.setting["ecd2itat_explicit_keywords"] or DEFAULT_EXPLICIT_KEYWORDS
    if isinstance(explicit_keywords, str):
        explicit_keywords = [kw.strip() for kw in explicit_keywords.split(",")]

    clean_keywords = config.setting["ecd2itat_clean_keywords"] or DEFAULT_CLEAN_KEYWORDS
    if isinstance(clean_keywords, str):
        clean_keywords = [kw.strip() for kw in clean_keywords.split(",")]

    explicit_match = next((kw for kw in explicit_keywords if kw.lower() in disambiguation.strip().lower()), None)
    clean_match = next((kw for kw in clean_keywords if kw.lower() in disambiguation.strip().lower()), None)

    if explicit_match:
        metadata["itunesadvisory"] = iTunesAdvisory.EXPLICIT.value

        if config.setting["ecd2itat_save_rtng"]:
            metadata["rtng"] = rtng.EXPLICIT.value

        if config.setting["ecd2itat_strip_keyword_from_disambiguation"]:
            metadata["subtitle"] = strip_keyword_from_disambiguation(disambiguation, explicit_match)
            metadata["musicbrainz_albumcomment"] = strip_keyword_from_disambiguation(album_disambiguation, explicit_match)
    elif clean_match:
        metadata["itunesadvisory"] = iTunesAdvisory.CLEAN.value

        if (config.setting["ecd2itat_save_rtng"]):
            metadata["rtng"] = rtng.CLEAN.value

        if config.setting["ecd2itat_strip_keyword_from_disambiguation"]:
            metadata["subtitle"] = strip_keyword_from_disambiguation(disambiguation, clean_match)
            metadata["musicbrainz_albumcomment"] = strip_keyword_from_disambiguation(album_disambiguation, clean_match)

def strip_keyword_from_disambiguation(disambiguation, keyword):
    # If the keyword is the entire disambiguation, return an empty string (e,g. "explicit" becomes "")
    if disambiguation.strip().lower() == keyword.lower():
        return ""

    # keyword is at the start of the disambiguation (e.g. "explicit, original mix" becomes "original mix")
    if disambiguation.strip().lower().startswith(keyword.lower() + ","):
        return disambiguation[len(keyword)+1:].strip()

    # keyword is at the end of the disambiguation (e.g. "original mix,explicit" becomes "original mix")
    if disambiguation.strip().lower().endswith("," + keyword.lower()):
        return disambiguation[:-len(keyword)-1].strip()
    
    # keyword is at the end with a preceding comma and space (e.g. "original mix, explicit" becomes "original mix")
    if disambiguation.strip().lower().endswith(", " + keyword.lower()):
        return disambiguation[:-len(keyword)-2].strip()

    # keyword is in the middle of the disambiguation (e.g. "album version, explicit, remix" becomes "album version, remix")
    if "," + keyword.lower() + "," in disambiguation.strip().lower():
        return disambiguation.replace("," + keyword + ",", ",").strip()

    # Return the disambiguation unchanged if the keyword is not found or cannot be stripped
    log.debug(f"Keyword '{keyword}' not found in disambiguation '{disambiguation}' for stripping")
    return disambiguation

class ECD2ITatOptionsPage(OptionsPage):
    NAME = "ecd2itat"
    TITLE = "ecd2iTat"
    PARENT = "plugins"

    options = CONFIG_OPTIONS

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        options_group = QtWidgets.QGroupBox("Options", self)
        options_group.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        options_layout = QtWidgets.QVBoxLayout(options_group)

        self.save_rtng_checkbox = QtWidgets.QCheckBox("Save rtng", self)
        self.save_rtng_checkbox.setToolTip("Save the rtng tag")

        self.ecd2itat_strip_keyword_from_disambiguation_checkbox = QtWidgets.QCheckBox("Strip keywords from disambiguation", self)
        self.ecd2itat_strip_keyword_from_disambiguation_checkbox.setToolTip("Try to remove the keyword from the disambiguation after processing, enable this if you don't want the keywords to be visible in the disambiguation and save it under \"subtitle\" (applies to albums too under \"musicbrainz_albumcomment\")")

        options_layout.addWidget(self.save_rtng_checkbox)
        options_layout.addWidget(self.ecd2itat_strip_keyword_from_disambiguation_checkbox)

        layout.addWidget(options_group)

        keywords_group = QtWidgets.QGroupBox("Keywords", self)
        keywords_group.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        keywords_layout = QtWidgets.QVBoxLayout(keywords_group)

        explicit_keywords_layout = QtWidgets.QHBoxLayout()
        explicit_keywords_label = QtWidgets.QLabel("Explicit:", self)
        self.explicit_keywords_input = QtWidgets.QLineEdit(self)
        self.explicit_keywords_input.setPlaceholderText("Comma-separated list of keywords to consider as explicit")
        self.explicit_keywords_input.setToolTip("Comma-separated list of keywords to consider as explicit")

        explicit_keywords_layout.addWidget(explicit_keywords_label)
        explicit_keywords_layout.addWidget(self.explicit_keywords_input)

        clean_keywords_layout = QtWidgets.QHBoxLayout()
        clean_keywords_label = QtWidgets.QLabel("Clean:", self)
        self.clean_keywords_input = QtWidgets.QLineEdit(self)
        self.clean_keywords_input.setPlaceholderText("Comma-separated list of keywords to consider as clean")
        self.clean_keywords_input.setToolTip("Comma-separated list of keywords to consider as clean")

        clean_keywords_layout.addWidget(clean_keywords_label)
        clean_keywords_layout.addWidget(self.clean_keywords_input)

        keywords_layout.addLayout(explicit_keywords_layout)
        keywords_layout.addLayout(clean_keywords_layout)

        layout.addWidget(keywords_group)

        layout.addStretch()

    def load(self):
        self.save_rtng_checkbox.setChecked(config.setting["ecd2itat_save_rtng"] or False)
        self.ecd2itat_strip_keyword_from_disambiguation_checkbox.setChecked(config.setting["ecd2itat_strip_keyword_from_disambiguation"] or False)
        self.explicit_keywords_input.setText(config.setting["ecd2itat_explicit_keywords"] or ", ".join(DEFAULT_EXPLICIT_KEYWORDS))
        self.clean_keywords_input.setText(config.setting["ecd2itat_clean_keywords"] or ", ".join(DEFAULT_CLEAN_KEYWORDS))

    def save(self):
        config.setting["ecd2itat_save_rtng"] = self.save_rtng_checkbox.isChecked()
        config.setting["ecd2itat_strip_keyword_from_disambiguation"] = self.ecd2itat_strip_keyword_from_disambiguation_checkbox.isChecked()
        config.setting["ecd2itat_explicit_keywords"] = self.explicit_keywords_input.text()
        config.setting["ecd2itat_clean_keywords"] = self.clean_keywords_input.text()

register_options_page(ECD2ITatOptionsPage)
register_track_metadata_processor(process_track)