# PROGRESS — VavPy2

> **Gemeinsame Fortschritts-Zentrale für agy (Antigravity) und OpenCode.**
> Beide Tools arbeiten am selben Projekt und müssen hier immer den aktuellen Stand hinterlassen.

## Regeln (verbindlich für den Agent in beiden Tools)

1. **Session-Start:** Diese Datei zuerst vollständig lesen.
2. **Während der Arbeit:** Nach jeder wesentlichen Erkenntnis/Änderung sofort hier eintragen.
3. **Einträge kennzeichnen:** `[agy]` oder `[oc]` + Datum (JJJJ-MM-TT). Einträge des anderen
   Tools niemals löschen oder umschreiben.
4. **Session-Ende:** "Offene Punkte" aktualisieren.

## Aktueller Stand

Kodi 18.9 / Python 2.7 Port für Amlogic S812 / M8S (AlexELEC 3.3.3) des VAVOO.TO Add-ons.
GitHub Repo: `Neur-alx/VavPy2`.
CodeRabbit GitHub App ist auf dem Repo autorisiert.

## Zuletzt erledigt

- `[agy] 2026-11-26` Repo lokal nach `/home/alx/VavPy2` geklont und in PROGRESS-REGISTRY registriert.
- `[agy] 2026-11-26` Bugfix in `vjlive.py`: doppelte URL/Header-Zuweisung entfernt.
- `[agy] 2026-11-26` Testfix in `test_playback_properties.py`: veraltete `inputstream.ffmpeg`-Assertions korrigiert.
- `[agy] 2026-11-26` `.coderabbit.yaml` mit Python 2.7 / Kodi 18.9 Instruktionen und deutscher Review-Sprache angelegt.
- `[agy] 2026-11-26` CI-Workflow `.github/workflows/vavoo-py2.yml` um `pull_request`-Trigger erweitert.

## Offene Punkte / Nächste Schritte

- [ ] Branch `refactor-kodi18-cleanup` pushen und Pull Request auf GitHub erstellen
- [ ] CodeRabbit Cloud-Review auf GitHub abwarten und überprüfen

## Wichtige Erkenntnisse (dauerhaft)

- Kodi 18.9 Leia auf AlexELEC 3.3.3 (Amlogic S812 / Kernel 3.10) verlangt zwingend Python 2.7. Kein automatisches Upgrade auf Python 3 durchführen!
- `inputstream.ffmpeg` ist keine gültige Add-on-ID in Kodi 18; HLS läuft über `inputstream.adaptive`, MPEG-TS nativ.

## Referenzen

- Repo: https://github.com/Neur-alx/VavPy2
- agy-Conversation: efb6339a-fbc6-4f74-a7b9-c04de4e06e0e
