# Hardware-Testmatrix für AlexELEC 3.3.3 / M8S (Amlogic S812, Kodi 18.3 Leia, Python 2.7)

Dieser Testplan gilt für den VAVOO.TO Python-2.7-Port auf Kodi 18.3.
Er muss auf echter Hardware (M8S, S812, AlexELEC 3.3.3) ausgeführt werden.
Keine Änderungen an Bootloader, NAND, eMMC, Kernel oder Betriebssystem.

## Voraussetzungen

- AlexELEC 3.3.3 installiert auf M8S (S812)
- Kodi 18.3 Leia (Python 2.7)
- Add-on `plugin.video.vavooto` installiert (ZIP aus CI-Artefakt)
- Add-on `inputstream.adaptive 2.3.22-Leia` installiert und aktiviert
- VAVOO- oder Stalker-Portal-Zugangsdaten konfiguriert

## Testmatrix

| # | Testfall | URL-Typ | MIME-Type | Erwarteter Inputstream-Pfad | Status |
|---|----------|---------|-----------|----------------------------|--------|
| 1 | Live-HLS (.m3u8) | `http://.../stream.m3u8` | `application/vnd.apple.mpegurl` | inputstream.adaptive, manifest_type=hls | ⬜ |
| 2 | Live-HLS mit Query-Params | `http://.../stream.m3u8?token=...` | `application/vnd.apple.mpegurl` | inputstream.adaptive, manifest_type=hls | ⬜ |
| 3 | Live-HLS über Redirect | HTTP 301/302 auf .m3u8 | `application/vnd.apple.mpegurl` | inputstream.adaptive, manifest_type=hls | ⬜ |
| 4 | Live-MPEG-TS direkt (.ts) | `http://.../stream.ts` | `video/mp2t` | Kodi-interner ffmpegdemuxer (kein Add-on) | ⬜ |
| 5 | Live-MPEG-TS ohne Endung | `http://.../stream` | `video/mp2t` | Kodi-interner ffmpegdemuxer (kein Add-on) | ⬜ |
| 6 | Live über lokalen Proxy | `http://127.0.0.1:19888/...` | `application/vnd.apple.mpegurl` | inputstream.adaptive, manifest_type=hls | ⬜ |
| 7 | VOD-HLS | `http://.../vod.m3u8` | `application/vnd.apple.mpegurl` | inputstream.adaptive, manifest_type=hls | ⬜ |
| 8 | VOD-DASH | `http://.../vod.mpd` | `application/dash+xml` | inputstream.adaptive, manifest_type=mpd | ⬜ |

## Prüfpunkte pro Testfall

Für jeden Testfall müssen folgende Punkte geprüft und dokumentiert werden:

1. **Startzeit**: Zeit vom Klicken bis zum ersten Bild (Sekunden)
2. **Bild und Ton**: Bild erscheint, Ton ist synchron
3. **Kanalwechsel**: Wechsel zu einem anderen Kanal funktioniert innerhalb von 5 Sekunden
4. **Seek/Pause**: (sofern unterstützt) Pause und Seek funktionieren
5. **Verbindungsabbruch**: Stream unterbrechen und wiederherstellen
6. **Kodi-Log**: Prüfen, welcher Inputstream tatsächlich verwendet wurde

## Kodi-Log-Auswertung

Der tatsächlich verwendete Inputstream lässt sich im Kodi-Log (`~/.kodi/temp/kodi.log`) identifizieren:

```bash
# Inputstream-Add-on prüfen
grep -i "inputstream" ~/.kodi/temp/kodi.log | tail -20

# Demuxer-Info prüfen
grep -i "demuxer\|ffmpeg\|hls\|dash" ~/.kodi/temp/kodi.log | tail -20
```

Erwartete Log-Einträge pro Testfall:

| Testfall | Erwarteter Log-Eintrag |
|----------|----------------------|
| Live-HLS | `inputstream.adaptive`, `manifest_type=hls` |
| Live-MPEG-TS | `ffmpegdemuxer`, `video/mp2t`, kein inputstreamaddon |
| VOD-HLS | `inputstream.adaptive`, `manifest_type=hls` |
| VOD-DASH | `inputstream.adaptive`, `manifest_type=mpd` |

## Bekannte Einschränkungen

- `inputstream.ffmpeg` ist **keine** gültige Add-on-ID in Kodi 18.3 und darf nicht verwendet werden.
- `inputstream.adaptive.config` mit `ssl_verify_peer` ist in Version 2.3.22-Leia nicht verfügbar (erst ab v.21.4.11).
- `inputstream.adaptive.manifest_type` ist in Kodi 18 mandatory und muss explizit gesetzt werden.

## Abschließende Freigabe

Der Port gilt als funktionsfähig, wenn alle 8 Testfälle auf echter Hardware bestanden wurden und die Kodi-Logs den erwarteten Inputstream-Pfad bestätigen.

Datum: ____________________  Getestet von: ____________________  Ergebnis: ____________________
