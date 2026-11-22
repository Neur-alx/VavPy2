# -*- coding: utf-8 -*-
"""Simulation der Kodi 18.3 Inputstream-Auswahllogik.

Dieser Test simuliert die Entscheidungslogik, die Kodi 18.3 (Leia)
bei der Auswahl des Inputstreams verwendet, basierend auf dem
Kodi-Quellstand 2e454a77bdd1289a7c2dc81a92783638c4779ab2.

WICHTIG: Dies ist eine SIMULATION, kein echter Kodi-Wiedergabetest.
Die Logik wurde aus dem Kodi 18.3-Quellcode abgeleitet und dient dazu,
den Python-Code von vjlive.py und vjackson.py gegen eine reproduzierbare
Auswahl-Logik zu validieren.

Quellen:
- DVDFactoryInputStream.cpp
- InputStreamAddon.cpp
- xbmc/inputstream.adaptive/wiki/Integration

Erkenntnisse aus Kodi 18.3:
1. Bei Binary-Inputstream-Add-ons wird "inputstreamaddon" gegen die
   tatsächliche ID eines installierten Add-ons geprueft.
2. "inputstream.ffmpeg" ist KEINE gueltige Add-on-ID.
3. Kodi 18.3 wählt den internen FFmpeg-Inputstream unter anderem bei:
   - bestimmten Protokollen
   - ".m3u8"-URLs
   - MIME-Type "application/vnd.apple.mpegurl"
4. Eine gewöhnliche HTTP-URL mit ".ts" und MIME-Type "video/mp2t"
   wird NICHT automatisch ueber denselben HLS-FFmpeg-Pfad abgewickelt.
5. inputstream.adaptive 2.3.22-Leia benoetigt:
   - inputstreamaddon = inputstream.adaptive (mandatory für Kodi 18)
   - inputstream.adaptive.manifest_type = hls|mpd (mandatory bis Kodi 20)
"""

import sys
import os

# --- Simulation der Kodi 18.3 Inputstream-Auswahl ----------------------------

INSTALLED_ADDONS = {
    "inputstream.adaptive": "2.3.22-Leia",
    # inputstream.ffmpeg existiert NICHT als Add-on in Kodi 18
}

# Liste bekannter ungültiger Add-on-IDs, die nicht installiert sind
INVALID_ADDON_IDS = {
    "inputstream.ffmpeg",
}


def kodi18_select_inputstream(url, mime_type, inputstreamaddon_prop, manifest_type_prop=None):
    """
    Simuliert die Kodi 18.3 Inputstream-Auswahl.

    Returns:
        (chosen_inputstream, reason, is_valid)
        - chosen_inputstream: Name des gewählten Inputstreams oder None
        - reason: Begründung der Entscheidung
        - is_valid: Ob die Konfiguration für Kodi 18.3 gültig ist
    """
    url_lower = url.lower()

    # 1. Prüfe ob inputstreamaddon auf eine gültige Add-on-ID verweist
    if inputstreamaddon_prop:
        if inputstreamaddon_prop in INVALID_ADDON_IDS:
            return None, "Ungültige inputstreamaddon-ID: %r (kein installiertes Add-on in Kodi 18)" % inputstreamaddon_prop, False
        if inputstreamaddon_prop not in INSTALLED_ADDONS:
            return None, "Unbekannte inputstreamaddon-ID: %r (nicht installiert)" % inputstreamaddon_prop, False
        addon_version = INSTALLED_ADDONS[inputstreamaddon_prop]

    # 2. HLS-Erkennung: .m3u8 in URL oder MIME application/vnd.apple.mpegurl
    is_hls_url = ".m3u8" in url_lower or "/hls/" in url_lower
    is_hls_mime = mime_type == "application/vnd.apple.mpegurl"

    # 3. DASH-Erkennung: .mpd in URL oder MIME application/dash+xml
    is_dash_url = ".mpd" in url_lower
    is_dash_mime = mime_type == "application/dash+xml"

    # 4. MPEG-TS-Erkennung: .ts in URL oder MIME video/mp2t
    is_mpeg_ts_url = url_lower.endswith(".ts") or url_lower.endswith(".mpegts")
    is_mpeg_ts_mime = mime_type == "video/mp2t"

    # --- Entscheidungslogik ---

    # Fall 1: HLS (.m3u8 oder application/vnd.apple.mpegurl)
    if is_hls_url or is_hls_mime:
        if inputstreamaddon_prop == "inputstream.adaptive":
            if manifest_type_prop == "hls":
                return "inputstream.adaptive (HLS)", "Kodi 18.3 wählt inputstream.adaptive für HLS mit manifest_type=hls", True
            else:
                return "inputstream.adaptive (HLS, fehlendes manifest_type)", "Kodi 18.3 benötigt manifest_type=hls für HLS", False
        else:
            return "inputstream.adaptive (HLS, falsches Add-on)", "Kodi 18.3 nutzt inputstream.adaptive für HLS, nicht %r" % inputstreamaddon_prop, False

    # Fall 2: DASH (.mpd oder application/dash+xml)
    if is_dash_url or is_dash_mime:
        if inputstreamaddon_prop == "inputstream.adaptive":
            if manifest_type_prop == "mpd":
                return "inputstream.adaptive (DASH)", "Kodi 18.3 wählt inputstream.adaptive für DASH mit manifest_type=mpd", True
            else:
                return "inputstream.adaptive (DASH, fehlendes manifest_type)", "Kodi 18.3 benötigt manifest_type=mpd für DASH", False
        else:
            return "inputstream.adaptive (DASH, falsches Add-on)", "Kodi 18.3 nutzt inputstream.adaptive für DASH, nicht %r" % inputstreamaddon_prop, False

    # Fall 3: MPEG-TS (.ts oder video/mp2t) ohne Manifest
    if is_mpeg_ts_url or is_mpeg_ts_mime:
        if not inputstreamaddon_prop:
            return "Kodi-interner ffmpegdemuxer", "Kodi 18.3 spielt MPEG-TS nativ ab (kein Inputstream-Add-on)", True
        elif inputstreamaddon_prop == "inputstream.adaptive":
            return "inputstream.adaptive (MPEG-TS, falsch)", "MPEG-TS sollte nicht über inputstream.adaptive laufen", False
        else:
            return "Unbekanntes Add-on %r für MPEG-TS" % inputstreamaddon_prop, "Ungültige Konfiguration", False

    # Fall 4: Unbekannt
    return None, "Keine Eingabe-Stream-Erkennung möglich", False


# --- Tests -------------------------------------------------------------------

def test_simulation_live_hls():
    """Live-HLS (.m3u8) -> inputstream.adaptive mit manifest_type=hls"""
    stream, reason, valid = kodi18_select_inputstream(
        url="http://example.com/stream.m3u8",
        mime_type="application/vnd.apple.mpegurl",
        inputstreamaddon_prop="inputstream.adaptive",
        manifest_type_prop="hls",
    )
    assert stream == "inputstream.adaptive (HLS)", stream
    assert valid is True
    assert "manifest_type=hls" in reason
    print("  PASS: Simulation Live-HLS -> inputstream.adaptive (HLS)")


def test_simulation_live_mpeg_ts():
    """Live-MPEG-TS (.ts) -> Kodi-interner ffmpegdemuxer (kein Add-on)"""
    stream, reason, valid = kodi18_select_inputstream(
        url="http://example.com/stream.ts",
        mime_type="video/mp2t",
        inputstreamaddon_prop=None,
        manifest_type_prop=None,
    )
    assert stream == "Kodi-interner ffmpegdemuxer", stream
    assert valid is True
    print("  PASS: Simulation Live-MPEG-TS -> Kodi-interner ffmpegdemuxer")


def test_simulation_live_hls_with_query():
    """Live-HLS mit Query-Parametern -> inputstream.adaptive mit manifest_type=hls"""
    stream, reason, valid = kodi18_select_inputstream(
        url="http://example.com/stream.m3u8?token=abc123",
        mime_type="application/vnd.apple.mpegurl",
        inputstreamaddon_prop="inputstream.adaptive",
        manifest_type_prop="hls",
    )
    assert stream == "inputstream.adaptive (HLS)", stream
    assert valid is True
    print("  PASS: Simulation Live-HLS mit Query -> inputstream.adaptive (HLS)")


def test_simulation_vod_hls():
    """VOD-HLS (.m3u8) -> inputstream.adaptive mit manifest_type=hls"""
    stream, reason, valid = kodi18_select_inputstream(
        url="http://example.com/vod.m3u8",
        mime_type="application/vnd.apple.mpegurl",
        inputstreamaddon_prop="inputstream.adaptive",
        manifest_type_prop="hls",
    )
    assert stream == "inputstream.adaptive (HLS)", stream
    assert valid is True
    print("  PASS: Simulation VOD-HLS -> inputstream.adaptive (HLS)")


def test_simulation_vod_dash():
    """VOD-DASH (.mpd) -> inputstream.adaptive mit manifest_type=mpd"""
    stream, reason, valid = kodi18_select_inputstream(
        url="http://example.com/vod.mpd",
        mime_type="application/dash+xml",
        inputstreamaddon_prop="inputstream.adaptive",
        manifest_type_prop="mpd",
    )
    assert stream == "inputstream.adaptive (DASH)", stream
    assert valid is True
    print("  PASS: Simulation VOD-DASH -> inputstream.adaptive (DASH)")


def test_simulation_inputstream_ffmpeg_invalid():
    """inputstream.ffmpeg ist keine gueltige Add-on-ID -> ungültig"""
    stream, reason, valid = kodi18_select_inputstream(
        url="http://example.com/stream.m3u8",
        mime_type="application/vnd.apple.mpegurl",
        inputstreamaddon_prop="inputstream.ffmpeg",
        manifest_type_prop="hls",
    )
    assert stream is None, stream
    assert valid is False
    assert "inputstream.ffmpeg" in reason
    print("  PASS: Simulation inputstream.ffmpeg -> ungültig (keine Add-on-ID)")


def test_simulation_vod_hls_missing_manifest_type():
    """VOD-HLS ohne manifest_type -> ungültig für Kodi 18"""
    stream, reason, valid = kodi18_select_inputstream(
        url="http://example.com/vod.m3u8",
        mime_type="application/vnd.apple.mpegurl",
        inputstreamaddon_prop="inputstream.adaptive",
        manifest_type_prop=None,
    )
    assert valid is False
    assert "manifest_type" in reason
    print("  PASS: Simulation VOD-HLS ohne manifest_type -> ungültig")


if __name__ == "__main__":
    test_simulation_live_hls()
    test_simulation_live_mpeg_ts()
    test_simulation_live_hls_with_query()
    test_simulation_vod_hls()
    test_simulation_vod_dash()
    test_simulation_inputstream_ffmpeg_invalid()
    test_simulation_vod_hls_missing_manifest_type()
    print("\nAlle Simulation-Tests bestanden.")
