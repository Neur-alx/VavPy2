# -*- coding: utf-8 -*-
"""Test für Live-TV Wiedergabepfade unter Kodi 18.3 / AlexELEC 3.3.3 (Python 2.7).

Mockt xbmc/xbmcgui/xbmcaddon/xbmcplugin/xbmcvfs und führt den echten
vjlive.livePlay-Code aus. Erfasst alle gesetzten ListItem-Properties und
prüft den tatsächlichen Inputstream-Pfad.

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
    def getSetting(self, k): return "true" if k == "vavoo" else ""
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
    def setProperty(self, k, v): self.props[k] = v
    def getProperty(self, k): return self.props.get(k, "")
    def setPath(self, p): self.path = p
    def setMimeType(self, m): self.mime = m
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
utils.addon.getSetting = lambda k: "true" if k == "vavoo" else ""
utils.set_cache = lambda *a, **k: None
utils.getSetting = lambda k: "true" if k in ("vavoo", "live_auto_retry") else ""

import vavoo.vjlive as vj
vj.getSetting = utils.addon.getSetting

# --- Test-Helfer -------------------------------------------------------------

def _reset_mocks():
    """Setzt die ListItem-Erfassung zurück."""
    _Item.instances = []

_Item.instances = []
_orig_li = xbmcgui.ListItem
def _li(*a, **k):
    it = _Item()
    _Item.instances.append(it)
    return it
xbmcgui.ListItem = _li
vj.ListItem = _li


def _get_last_item():
    """Liefert das zuletzt erstellte ListItem oder None."""
    if _Item.instances:
        return _Item.instances[-1]
    return None


# --- Test: Live-HLS (.m3u8) --------------------------------------------------

def test_live_hls_uses_inputstream_adaptive():
    """Live-HLS (.m3u8) muss inputstream.adaptive mit manifest_type=hls setzen."""
    vj.getchannels = lambda *a, **k: {
        "Test-HLS": [
            {"source": "vavoo", "url": "http://example.com/stream.m3u8"}
        ]
    }
    vj.resolve_link = lambda link: ("http://example.com/stream.m3u8", None)

    vj.livePlay("Test-HLS")

    it = _get_last_item()
    assert it is not None, "ListItem wurde nicht erstellt"
    assert it.props.get("inputstreamaddon") == "inputstream.adaptive", \
        "inputstreamaddon muss inputstream.adaptive sein (war: %r)" % it.props.get("inputstreamaddon")
    assert it.props.get("inputstream.adaptive.manifest_type") == "hls", \
        "manifest_type muss hls sein (war: %r)" % it.props.get("inputstream.adaptive.manifest_type")
    assert it.mime == "application/vnd.apple.mpegurl", \
        "MIME muss application/vnd.apple.mpegurl sein (war: %r)" % it.mime
    assert it.props.get("ContentLookup") is False or it.props.get("contentlookup") is False, \
        "ContentLookup sollte False sein"
    print("  PASS: Live-HLS nutzt inputstream.adaptive mit manifest_type=hls")


# --- Test: Live-MPEG-TS (.ts) ------------------------------------------------

def test_live_mpeg_ts_no_inputstream_addon():
    """Live-MPEG-TS (.ts) darf KEIN inputstreamaddon setzen (Kodi 18 native)."""
    vj.getchannels = lambda *a, **k: {
        "Test-TS": [
            {"source": "stalker", "url": "http://example.com/stream.ts"}
        ]
    }
    vj.resolve_link = lambda link: ("http://example.com/stream.ts", None)

    vj.livePlay("Test-TS")

    it = _get_last_item()
    assert it is not None, "ListItem wurde nicht erstellt"
    # MPEG-TS darf kein inputstreamaddon haben -> Kodi nutzt internen Demuxer
    assert it.props.get("inputstreamaddon") != "inputstream.ffmpeg", \
        "inputstream.ffmpeg ist KEINE gueltige Add-on-ID in Kodi 18"
    assert it.props.get("inputstreamaddon") is None or it.props.get("inputstreamaddon") == "", \
        "MPEG-TS darf kein inputstreamaddon setzen (war: %r)" % it.props.get("inputstreamaddon")
    assert it.mime == "video/mp2t", \
        "MIME muss video/mp2t sein (war: %r)" % it.mime
    print("  PASS: Live-MPEG-TS hat kein inputstreamaddon (Kodi 18 native)")


# --- Test: Live-HLS mit Query-Parametern -------------------------------------

def test_live_hls_query_params():
    """Live-HLS mit Query-Parametern muss trotzdem inputstream.adaptive nutzen."""
    vj.getchannels = lambda *a, **k: {
        "Test-HLS-Q": [
            {"source": "vavoo", "url": "http://example.com/stream.m3u8?token=abc123"}
        ]
    }
    vj.resolve_link = lambda link: ("http://example.com/stream.m3u8?token=abc123", None)

    vj.livePlay("Test-HLS-Q")

    it = _get_last_item()
    assert it is not None, "ListItem wurde nicht erstellt"
    assert it.props.get("inputstreamaddon") == "inputstream.adaptive", \
        "HLS mit Query-Params braucht inputstream.adaptive"
    assert it.props.get("inputstream.adaptive.manifest_type") == "hls", \
        "manifest_type muss hls sein"
    assert ".m3u8" in it.path, "URL muss .m3u8 enthalten"
    print("  PASS: Live-HLS mit Query-Parametern nutzt inputstream.adaptive")


# --- Test: Inputstream.ffmpeg ist verboten -----------------------------------

def test_no_inputstream_ffmpeg_property():
    """inputstream.ffmpeg darf niemals als inputstreamaddon gesetzt werden."""
    vj.getchannels = lambda *a, **k: {
        "Test-NoFFmpeg": [
            {"source": "vavoo", "url": "http://example.com/stream.m3u8"}
        ]
    }
    vj.resolve_link = lambda link: ("http://example.com/stream.m3u8", None)

    vj.livePlay("Test-NoFFmpeg")

    it = _get_last_item()
    assert it is not None
    assert it.props.get("inputstreamaddon") != "inputstream.ffmpeg", \
        "inputstream.ffmpeg ist KEINE gueltige Add-on-ID in Kodi 18"
    assert it.props.get("inputstream") != "inputstream.ffmpeg", \
        "inputstream=inputstream.ffmpeg ist auf Kodi 18 wirkungslos"
    print("  PASS: Kein inputstream.ffmpeg als inputstreamaddon")


if __name__ == "__main__":
    test_live_hls_uses_inputstream_adaptive()
    test_live_mpeg_ts_no_inputstream_addon()
    test_live_hls_query_params()
    test_no_inputstream_ffmpeg_property()
    print("\nAlle Live-TV-Tests bestanden.")
