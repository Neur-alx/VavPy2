# -*- coding: utf-8 -*-
"""Test für VOD-Wiedergabepfade unter Kodi 18.3 / AlexELEC 3.3.3 (Python 2.7).

Mockt xbmc/xbmcgui/xbmcaddon/xbmcplugin/xbmcvfs und führt den echten
vjackson.get-Code aus. Erfasst alle gesetzten ListItem-Properties und
prüft den tatsächlichen Inputstream-Pfad für HLS- und DASH-VOD.

HINWEIS: Dies ist ein Mock-Test ohne echtes Kodi. Er prüft, ob der
Python-Code die korrekten Properties setzt. Eine echte Wiedergabe auf
Hardware muss separat getestet werden (siehe HARDWARE_TEST.md).
"""

import sys
import os
import types

base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "plugin.video.vavooto", "resources"))
sys.path.insert(0, base)

# --- Kodi-Module mocken ------------------------------------------------------

def _strict(name):
    m = types.ModuleType(name)
    return m

for m in ("xbmc", "xbmcvfs", "xbmcaddon", "xbmcgui", "xbmcplugin"):
    sys.modules[m] = _strict(m)

import xbmcplugin
xbmcplugin.setResolvedUrl = lambda *a, **k: None
xbmcplugin.endOfDirectory = lambda *a, **k: None

import xbmc
xbmc.translatePath = lambda p: p
xbmc.Monitor = lambda *a, **k: _strict("monitor")
xbmc.Player = type("Player", (object,), {})
xbmc.getInfoLabel = lambda *a, **k: ""
xbmc.executebuiltin = lambda *a, **k: None
xbmc.getCondVisibility = lambda *a, **k: False
xbmc.LOGDEBUG = 0
xbmc.LOGINFO = 1
xbmc.log = lambda *a, **k: None

import xbmcaddon
class Addon(object):
    def getAddonInfo(self, k): return "/tmp/addon"
    def getSetting(self, k): return ""
    def setSetting(self, k, v): return None
    def openSettings(self): return None
xbmcaddon.Addon = lambda *a, **k: Addon()

import xbmcgui
captured = {}
class _Item(object):
    def __init__(self, *a, **k):
        self.props = {}
        self.path = None
        self.mime = None
        self.content_lookup = None
    def setProperty(self, k, v): self.props[k] = v
    def getProperty(self, k): return self.props.get(k, "")
    def setPath(self, p): self.path = p
    def setMimeType(self, m): self.mime = m
    def setContentLookup(self, lookup): self.content_lookup = lookup
    def setInfo(self, *a, **k): pass
    def setIsPlayable(self, *a, **k): pass
xbmcgui.ListItem = lambda *a, **k: _Item()
class _Win(object):
    def getProperty(self,k): return ""
    def setProperty(self,k,v): return None
xbmcgui.Window = lambda *a, **k: _Win()
xbmcgui.Dialog = lambda *a, **k: _strict("dlg")
xbmcgui.DialogProgress = lambda *a, **k: _strict("dp")
xbmcgui.NOTIFICATION_ERROR = 0

for m in ("resolveurl", "httpx", "requests", "urllib3", "infotagger"):
    if m not in sys.modules:
        sys.modules[m] = _strict(m)
import requests
requests.Session = lambda: _strict("session")

import vavoo.utils as utils
utils.get_cache = lambda k: (False, None)
utils.addon.getSetting = lambda k: ""
utils.set_cache = lambda *a, **k: None
utils.getSetting = lambda k: ""

import vavoo.vjackson as vj

# --- Test-Helfer -------------------------------------------------------------

_Item.instances = []
_orig_li = xbmcgui.ListItem
def _li(*a, **k):
    it = _Item()
    _Item.instances.append(it)
    return it
xbmcgui.ListItem = _li
vj.ListItem = _li


def _get_last_item():
    if _Item.instances:
        return _Item.instances[-1]
    return None


def _reset_mocks():
    _Item.instances = []


# --- Test: VOD-HLS (.m3u8) ---------------------------------------------------

def test_vod_hls_uses_inputstream_adaptive():
    """VOD-HLS (.m3u8) muss inputstream.adaptive mit manifest_type=hls setzen."""
    _reset_mocks()

    # Mock: get_mimirror liefert eine HLS-URL
    vj.get_mirrors = lambda params: [
        {"name": "1. TestHoster", "weight": 1000, "hoster": "test", "url": "http://example.com/vod.m3u8"}
    ]
    vj.resolve = lambda mirror: mirror["url"]
    vj.checkstream = lambda url: url
    vj.dialog = _strict("dialog")
    vj.dialog.select = lambda title, items: 0
    vj.getInfoLabel = lambda *a: "Test-Film"
    vj.showFailedNotification = lambda *a: None

    import xbmcplugin
    xbmcplugin.setResolvedUrl = lambda handle, succeeded, listitem: None

    vj.get({"id": "movie.123", "n": "Test-Film"})

    it = _get_last_item()
    assert it is not None, "ListItem wurde nicht erstellt"
    assert it.props.get("inputstreamaddon") == "inputstream.adaptive", \
        "inputstreamaddon muss inputstream.adaptive sein (war: %r)" % it.props.get("inputstreamaddon")
    assert it.props.get("inputstream.adaptive.manifest_type") == "hls", \
        "manifest_type muss hls sein (war: %r)" % it.props.get("inputstream.adaptive.manifest_type")
    assert it.mime == "application/vnd.apple.mpegurl", \
        "MIME muss application/vnd.apple.mpegurl sein (war: %r)" % it.mime
    assert it.content_lookup is False, \
        "ContentLookup muss False sein (war: %r)" % it.content_lookup
    print("  PASS: VOD-HLS nutzt inputstream.adaptive mit manifest_type=hls")


# --- Test: VOD-DASH (.mpd) ---------------------------------------------------

def test_vod_dash_uses_inputstream_adaptive():
    """VOD-DASH (.mpd) muss inputstream.adaptive mit manifest_type=mpd setzen."""
    _reset_mocks()

    vj.get_mirrors = lambda params: [
        {"name": "1. TestHoster", "weight": 1000, "hoster": "test", "url": "http://example.com/vod.mpd"}
    ]
    vj.resolve = lambda mirror: mirror["url"]
    vj.checkstream = lambda url: url
    vj.dialog = _strict("dialog")
    vj.dialog.select = lambda title, items: 0
    vj.getInfoLabel = lambda *a: "Test-Film"
    vj.showFailedNotification = lambda *a: None

    vj.get({"id": "movie.123", "n": "Test-Film"})

    it = _get_last_item()
    assert it is not None, "ListItem wurde nicht erstellt"
    assert it.props.get("inputstreamaddon") == "inputstream.adaptive", \
        "inputstreamaddon muss inputstream.adaptive sein (war: %r)" % it.props.get("inputstreamaddon")
    assert it.props.get("inputstream.adaptive.manifest_type") == "mpd", \
        "manifest_type muss mpd sein (war: %r)" % it.props.get("inputstream.adaptive.manifest_type")
    assert it.mime == "application/dash+xml", \
        "MIME muss application/dash+xml sein (war: %r)" % it.mime
    assert it.content_lookup is False, \
        "ContentLookup muss False sein (war: %r)" % it.content_lookup
    print("  PASS: VOD-DASH nutzt inputstream.adaptive mit manifest_type=mpd")


# --- Test: Keine inputstream.adaptive.config mit ssl_verify_peer ------------

def test_no_inputstream_adaptive_config():
    """inputstream.adaptive.config mit ssl_verify_peer ist in 2.3.22-Leia nicht verfuegbar."""
    _reset_mocks()

    vj.get_mirrors = lambda params: [
        {"name": "1. TestHoster", "weight": 1000, "hoster": "test", "url": "http://example.com/vod.m3u8"}
    ]
    vj.resolve = lambda mirror: mirror["url"]
    vj.checkstream = lambda url: url
    vj.dialog = _strict("dialog")
    vj.dialog.select = lambda title, items: 0
    vj.getInfoLabel = lambda *a: "Test-Film"
    vj.showFailedNotification = lambda *a: None

    vj.get({"id": "movie.123", "n": "Test-Film"})

    it = _get_last_item()
    assert it is not None
    assert it.props.get("inputstream.adaptive.config") is None or it.props.get("inputstream.adaptive.config") == "", \
        "inputstream.adaptive.config (ssl_verify_peer) ist in 2.3.22-Leia nicht verfuegbar (war: %r)" % it.props.get("inputstream.adaptive.config")
    print("  PASS: Keine inputstream.adaptive.config (nicht in 2.3.22-Leia)")


# --- Test: Kein inputstream für VOD ------------------------------------------

def test_no_inputstream_property_for_vod():
    """inputstream (Kodi 19+) darf nicht gesetzt werden, nur inputstreamaddon."""
    _reset_mocks()

    vj.get_mirrors = lambda params: [
        {"name": "1. TestHoster", "weight": 1000, "hoster": "test", "url": "http://example.com/vod.m3u8"}
    ]
    vj.resolve = lambda mirror: mirror["url"]
    vj.checkstream = lambda url: url
    vj.dialog = _strict("dialog")
    vj.dialog.select = lambda title, items: 0
    vj.getInfoLabel = lambda *a: "Test-Film"
    vj.showFailedNotification = lambda *a: None

    vj.get({"id": "movie.123", "n": "Test-Film"})

    it = _get_last_item()
    assert it is not None
    assert it.props.get("inputstream") is None or it.props.get("inputstream") == "", \
        "inputstream ist eine Kodi 19+-Property, nicht fuer Kodi 18 (war: %r)" % it.props.get("inputstream")
    assert it.props.get("inputstreamaddon") == "inputstream.adaptive", \
        "inputstreamaddon muss inputstream.adaptive sein"
    print("  PASS: Keine inputstream-Property (Kodi 19+), nur inputstreamaddon")


if __name__ == "__main__":
    test_vod_hls_uses_inputstream_adaptive()
    test_vod_dash_uses_inputstream_adaptive()
    test_no_inputstream_adaptive_config()
    test_no_inputstream_property_for_vod()
    print("\nAlle VOD-Tests bestanden.")
