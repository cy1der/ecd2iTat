from picard.plugin3.api import OptionsPage, PluginApi
from PyQt6 import QtWidgets
import re

from .constants import *

def process_track(api, _, metadata, track_node, __=None):
    disambiguation = track_node["recording"]["disambiguation"] if "recording" in track_node and "disambiguation" in track_node["recording"] else track_node["disambiguation"] if "disambiguation" in track_node else ""
    album_disambiguation = metadata["~releasecomment"] if "~releasecomment" in metadata else ""

    explicit_keywords = api.plugin_config["explicit_keywords"] or DEFAULT_EXPLICIT_KEYWORDS
    if isinstance(explicit_keywords, str):
        explicit_keywords = [kw.strip() for kw in explicit_keywords.split(",")]
    explicit_keywords = sorted((kw for kw in explicit_keywords if kw), key=len, reverse=True)

    clean_keywords = api.plugin_config["clean_keywords"] or DEFAULT_CLEAN_KEYWORDS
    if isinstance(clean_keywords, str):
        clean_keywords = [kw.strip() for kw in clean_keywords.split(",")]
    clean_keywords = sorted((kw for kw in clean_keywords if kw), key=len, reverse=True)

    disambiguation_lc = disambiguation.strip().lower()
    album_disambiguation_lc = album_disambiguation.strip().lower()

    explicit_match = next((kw for kw in explicit_keywords if kw.lower() in disambiguation_lc), None)
    clean_match = next((kw for kw in clean_keywords if kw.lower() in disambiguation_lc), None)
    album_explicit_match = next((kw for kw in explicit_keywords if kw.lower() in album_disambiguation_lc), None)
    album_clean_match = next((kw for kw in clean_keywords if kw.lower() in album_disambiguation_lc), None)

    stripped_disambiguation = disambiguation
    stripped_album_disambiguation = album_disambiguation

    if explicit_match:
        metadata["itunesadvisory"] = iTunesAdvisory.EXPLICIT.value
        if api.plugin_config["save_rtng"]:
            metadata["rtng"] = rtng.EXPLICIT.value
    elif clean_match:
        metadata["itunesadvisory"] = iTunesAdvisory.CLEAN.value
        if api.plugin_config["save_rtng"]:
            metadata["rtng"] = rtng.CLEAN.value
    elif album_explicit_match:
        metadata["itunesadvisory"] = iTunesAdvisory.EXPLICIT.value
        if api.plugin_config["save_rtng"]:
            metadata["rtng"] = rtng.EXPLICIT.value
    elif album_clean_match:
        metadata["itunesadvisory"] = iTunesAdvisory.CLEAN.value
        if api.plugin_config["save_rtng"]:
            metadata["rtng"] = rtng.CLEAN.value

    if api.plugin_config["strip_keyword_from_disambiguation"]:
        if explicit_match:
            stripped_disambiguation = strip_keyword_from_disambiguation(api, disambiguation, explicit_match)
        elif clean_match:
            stripped_disambiguation = strip_keyword_from_disambiguation(api, disambiguation, clean_match)

        if album_explicit_match:
            stripped_album_disambiguation = strip_keyword_from_disambiguation(api, album_disambiguation, album_explicit_match)
        elif album_clean_match:
            stripped_album_disambiguation = strip_keyword_from_disambiguation(api, album_disambiguation, album_clean_match)

    metadata["~recordingcomment"] = stripped_disambiguation
    metadata["~releasecomment"] = stripped_album_disambiguation

def strip_keyword_from_disambiguation(api, disambiguation, keyword):
    disambiguation_stripped = disambiguation.strip()
    keyword_stripped = keyword.strip()

    if not disambiguation_stripped or not keyword_stripped:
        return disambiguation

    keyword_pattern = re.compile(rf"(?<!\w){re.escape(keyword_stripped)}(?!\w)", re.IGNORECASE)
    if not keyword_pattern.search(disambiguation_stripped):
        api.logger.debug(f"Keyword '{keyword}' not found in disambiguation '{disambiguation}' for stripping")
        return disambiguation

    parts = re.split(r"\s*(,|\||-)\s*", disambiguation_stripped)
    terms = parts[::2]
    separators = parts[1::2]

    cleaned_terms = []
    for term in terms:
        cleaned_term = keyword_pattern.sub("", term)
        cleaned_term = re.sub(r"\(\s*\)", "", cleaned_term)
        cleaned_term = re.sub(r"\s{2,}", " ", cleaned_term).strip()
        cleaned_terms.append(cleaned_term)

    non_empty_indexes = [i for i, term in enumerate(cleaned_terms) if term]
    if not non_empty_indexes:
        return ""

    result = cleaned_terms[non_empty_indexes[0]]
    for index in non_empty_indexes[1:]:
        separator = separators[index - 1] if index - 1 < len(separators) else ","
        if separator == ",":
            result += f", {cleaned_terms[index]}"
        else:
            result += f" {separator} {cleaned_terms[index]}"

    return result

class ECD2ITatOptionsPage(OptionsPage):
    NAME = "ecd2itat"
    TITLE = "ecd2iTat"
    PARENT = "plugins"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        options_group = QtWidgets.QGroupBox("Options", self)
        options_group.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Minimum)
        options_layout = QtWidgets.QVBoxLayout(options_group)

        self.save_rtng_checkbox = QtWidgets.QCheckBox("Save rtng", self)
        self.save_rtng_checkbox.setToolTip("Save the rtng tag")

        self.ecd2itat_strip_keyword_from_disambiguation_checkbox = QtWidgets.QCheckBox("Strip keywords from disambiguation", self)
        self.ecd2itat_strip_keyword_from_disambiguation_checkbox.setToolTip("Try to remove the keyword from the disambiguation after processing, enable this if you don't want the keywords to be visible in the disambiguation (applies to albums too)")

        options_layout.addWidget(self.save_rtng_checkbox)
        options_layout.addWidget(self.ecd2itat_strip_keyword_from_disambiguation_checkbox)

        layout.addWidget(options_group)

        keywords_group = QtWidgets.QGroupBox("Keywords", self)
        keywords_group.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Minimum)
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
        self.save_rtng_checkbox.setChecked(self.api.plugin_config["save_rtng"] or False)
        self.ecd2itat_strip_keyword_from_disambiguation_checkbox.setChecked(self.api.plugin_config["strip_keyword_from_disambiguation"] or False)
        self.explicit_keywords_input.setText(self.api.plugin_config["explicit_keywords"] or ", ".join(DEFAULT_EXPLICIT_KEYWORDS))
        self.clean_keywords_input.setText(self.api.plugin_config["clean_keywords"] or ", ".join(DEFAULT_CLEAN_KEYWORDS))

    def save(self):
        self.api.plugin_config["save_rtng"] = self.save_rtng_checkbox.isChecked()
        self.api.plugin_config["strip_keyword_from_disambiguation"] = self.ecd2itat_strip_keyword_from_disambiguation_checkbox.isChecked()
        self.api.plugin_config["explicit_keywords"] = self.explicit_keywords_input.text()
        self.api.plugin_config["clean_keywords"] = self.clean_keywords_input.text()

def migrate_legacy_options(api: PluginApi, options):
    legacy_settings = api.global_config.setting

    for name, option in options.items():
        legacy_name = LEGACY_OPTION_PREFIX + name
        if name in api.plugin_config or legacy_name not in legacy_settings:
            continue

        api.plugin_config[name] = option.convert(legacy_settings.raw_value(legacy_name, qtype=option.qtype))
        api.logger.info(f"Migrated option '{legacy_name}' from plugin API v2 to '{name}'")

def enable(api: PluginApi):
    options = {name: api.plugin_config.register_option(name, default) for name, default in CONFIG_OPTIONS.items()}
    migrate_legacy_options(api, options)

    api.register_options_page(ECD2ITatOptionsPage)
    api.register_track_metadata_processor(process_track)
