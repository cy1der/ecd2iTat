# ecd2iTat

Convert disambiguations containing "explicit"/"clean" (and others) keywords to proper tags so clients can display the 🅴/🅲 symbol

## What the hell is that name?

(E)xplicit/(c)lean (d)isambiguation [to] (iT)unes (a)dvisory (t)ag\*

<small>\* `itunesadvisory` (and `rtng` because why not)</small>

## Getting Started

Requires MusicBrainz Picard 3 (plugin API v3).

1. Install the plugin, either:
   - In Picard, go to Options → Plugins and install from `https://github.com/cy1der/ecd2iTat`, or
   - Run `picard-cli plugins install https://github.com/cy1der/ecd2iTat`
2. Enable the plugin
3. Configure it to your liking (optional)

Settings from the Picard 2 version of the plugin are migrated automatically the first time it is enabled.

### Picard 2

The Picard 2 (plugin API v2) version lives on the [`apiv2`](https://github.com/cy1der/ecd2iTat/tree/apiv2) branch. Clone that branch to your Picard plugins folder to use it.
