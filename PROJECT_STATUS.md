# Projektstatus — VAVOO.TO Kodi 18 Python 2 Port

**Branch:** `kodi18-py2`  
**Lokales Arbeitsverzeichnis:** `/root/VAVOO-PY2`  
**Zielplattform:** Amlogic S812 / M8S, AlexELEC 3.3.3, Kodi 18.3 Leia, Python 2.7  
**Letzte Änderung:** 2026-11-22

---

## Erledigt (Code-Änderungen)

| Bereich | Änderung | Datei |
|---------|----------|-------|
| addon.xml | `<import addon="inputstream.adaptive"/>` korrekt (keine ungültige `inputstream.ffmpeg`-Abhängigkeit) | `plugin.video.vavooto/addon.xml` |
| vjlive.py | Live-TV: `inputstream.ffmpeg` entfernt (keine gültige Add-on-ID in Kodi 18). HLS → `inputstream.adaptive` mit `manifest_type=hls`. MPEG-TS → kein inputstreamaddon (Kodi-nativ). | `resources/vavoo/vjlive.py` |
| vjackson.py | VOD: `inputstream` (Kodi 19+) entfernt, nur `inputstreamadinputstreamaddon` gesetzt. `inputstream.adaptive.manifest_type` (`hls`/`mpd`) hinzugefügt (Kodi 18 mandatory). `inputstream.adaptive.config` mit `ssl_verify_peer` entfernt (nicht in 2.3.22-Leia). `setMimeType()` und `setContentLookup(False)` hinzugefügt. DASH-Unterstützung (`.mpd`) hinzugefügt. | `resources/vavoo/vjackson.py` |

---

## Erledigt (Tests)

| Test | Typ | Datei | Status |
|------|-----|-------|--------|
| Live-HLS (.m3u8) → inputstream.adaptive, manifest_type=hls | Mock-Test | `tests/test_live_playback.py` | ✅ |
| Live-MPEG-TS (.ts) → kein inputstreamaddon (Kodi-nativ) | Mock-Test | `tests/test_live_playback.py` | ✅ |
| Live-HLS mit Query-Parametern → inputstream.adaptive | Mock-Test | `tests/test_live_playback.py` | ✅ |
| Kein inputstream.ffmpeg als inputstreamaddon | Mock-Test | `tests/test_live_playback.py` | ✅ |
| VOD-HLS (.m3u8) → inputstream.adaptive, manifest_type=hls | Mock-Test | `tests/test_vod_playback.py` | ✅ |
| VOD-DASH (.mpd) → inputstream.adaptive, manifest_type=mpd | Mock-Test | `tests/test_vod_playback.py` | ✅ |
| Keine inputstream.adaptive.config (nicht in 2.3.22-Leia) | Mock-Test | `tests/test_vod_playback.py` | ✅ |
| Keine `inputstream`-Property (Kodi 19+) für VOD | Mock-Test | `tests/test_vod_playback.py` | ✅ |
| Kodi 18.3 Inputstream-Auswahllogik (Simulation) | Simulation | `tests/test_inputstream_selection.py` | ✅ |
| inputstream.ffmpeg → ungültig (keine Add-on-ID) | Simulation | `tests/test_inputstream_selection.py` | ✅ |

---

## Offen (Hardware-Test, nicht automatisierbar)

| Testfall | Beschreibung | Datei | Status |
|----------|-------------|-------|--------|
| Live-HLS | Echter Stream auf M8S/AlexELEC | `HARDWARE_TEST.md` | ⬜ |
| Live-MPEG-TS | Echter Stream auf M8S/AlexELEC | `HARDWARE_TEST.md` | ⬜ |
| VOD-HLS | Echter Stream auf M8S/AlexELEC | `HARDWARE_TEST.md` | ⬜ |
| VOD-DASH | Echter Stream auf M8S/AlexELEC | `HARDWARE_TEST.md` | ⬜ |
| Kanalwechsel, Seek/Pause, Verbindungsabbruch | Auf echter Hardware | `HARDWARE_TEST.md` | ⬜ |

---

## ZIP-Paket

- **Nicht erstellt** — muss nach dem Commit gebaut werden (siehe CI/Workflow).
- Zielname: `plugin.video.vavooto-kodi18-py2.zip`

---

## Bekannte Widersprüche (bereinigt)

| Vorher | Nachher | Begründung |
|--------|---------|------------|
| `vjlive.py` setzte `inputstream.ffmpeg` als `inputstreamaddon` | `inputstream.ffmpeg` entfernt, HLS → `inputstream.adaptive`, MPEG-TS → kein Add-on | `inputstream.ffmpeg` ist keine gültige Add-on-ID in Kodi 18 |
| `vjackson.py` setzte `inputstream` (Kodi 19+) und `inputstream.adaptive.config` | Nur `inputstreamaddon`, `manifest_type`, `setMimeType()`, `setContentLookup(False)` | `inputstream.adaptive.config` existiert nicht in 2.3.22-Leia; `inputstream` ist Kodi 19+ |
| `addon.xml` hatte früher ungültige Abhängigkeit | Nur `inputstream.adaptive` (korrekt für Kodi 18) | `inputstream.ffmpeg` ist keine echte Add-on-ID |

---

## Nächste Schritte

1. ZIP-Paket erstellen (CI-Workflow oder lokal)
2. ZIP auf echter Hardware installieren und testen (siehe `HARDWARE_TEST.md`)
3. GitHub Actions Lauf prüfen und ggf. Fehler beheben
4. `PROJECT_STATUS.md` nach jedem abgeschlossenen Schritt aktualisieren
