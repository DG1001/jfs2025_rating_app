# Java Forum Stuttgart 2025 - Bewertungsapp

Eine Flask-basierte Anwendung zur Verwaltung und Bewertung von Vorträgen für das Java Forum Stuttgart 2025.

## Funktionen

- Modernes, responsives Design mit fixierter Navigation
- Übersicht aller Vorträge mit Filterfunktionen
- Detailansicht mit vollständigem Abstract und Speaker-Informationen
- Bewertungssystem mit 1-5 Sternen (Bewertung durch Klick auf die Sterne)
- Kommentarfunktion für Vorträge (max. 200 Zeichen)
- "Schütteln für Zufallsvortrag" Funktion auf Mobilgeräten
- Fortschrittsanzeige (X/Y Vorträge bewertet)
- Admin-Oberfläche zur Benutzerverwaltung und Bewertungsübersicht
- Access-Token-System für Benutzerauthentifizierung
- JSON-basierte Datenspeicherung ohne Datenbankabhängigkeit


## Installation

1. Repository klonen oder Dateien herunterladen
2. Abhängigkeiten installieren:

```bash
pip install -r requirements.txt
```

3. Umgebungsvariablen setzen (optional, Standardwerte werden verwendet, wenn nicht gesetzt):

```bash
export FLASK_APP=app.py
export FLASK_ENV=development  # oder production für Produktionsumgebung
export SECRET_KEY=your_secret_key_here
export ADMIN_USERNAME=admin_username
export ADMIN_PASSWORD=admin_password
```

4. Anwendung starten:

```bash
flask run --host=0.0.0.0 --port=5000
```

## Verwendung

### Admin-Zugang

- URL: `/admin-login`
- Benutzername und Passwort werden über Umgebungsvariablen festgelegt
- Standardwerte: `admin` / `admin` (nur für Entwicklung)

### Benutzer-Zugang

- URL: `/login`
- Benutzer benötigen ein Access-Token, das vom Administrator generiert wird
- Tokens werden über die Admin-Oberfläche unter "Benutzer verwalten" erstellt
- Direkter Zugang über Token in URL möglich: `/login?token=<token>`

### Mobile Funktionen

- Schütteln des Mobilgeräts führt zu einem zufälligen, noch nicht bewerteten Vortrag
- Auf iOS-Geräten muss die Bewegungserkennung zuerst aktiviert werden

## Datenstruktur

Die Anwendung verwendet JSON-Dateien zur Datenspeicherung:

- `data/talks.json`: Vorträge
- `data/speakers.json`: Speaker
- `data/users.json`: Benutzer und Access-Tokens
- `data/ratings.json`: Bewertungen
- `data/comments.json`: Kommentare

## Tests

Ausführen der Tests:

```bash
python tests.py
```

## Technische Details

- Python 3.10+ mit Flask 2.3.3
- Flask-Login für Authentifizierung
- Bootstrap 5 für responsives Design
- JSON-Dateien für Datenspeicherung
- Logging-System für Bewertungen

## Datenschutz

Diese Anwendung speichert folgende Daten:
- Name und E-Mail-Adresse der Benutzer (für die Authentifizierung)
- Bewertungen und Kommentare zu Vorträgen
- Zugriffstoken für die Anmeldung

Alle Daten werden lokal in JSON-Dateien gespeichert und nicht an externe Server übermittelt.

## Lizenz

MIT Lizenz

Copyright (c) 2025 Java Forum Stuttgart

Hiermit wird unentgeltlich jeder Person, die eine Kopie dieser Software und der zugehörigen Dokumentationen (die "Software") erhält, die Erlaubnis erteilt, sie uneingeschränkt zu nutzen, inklusive und ohne Ausnahme mit dem Recht, sie zu verwenden, zu kopieren, zu verändern, zusammenzuführen, zu veröffentlichen, zu verbreiten, zu unterlizenzieren und/oder zu verkaufen, und Personen, denen diese Software überlassen wird, diese Rechte zu verschaffen, unter den folgenden Bedingungen:

Der obige Urheberrechtsvermerk und dieser Erlaubnisvermerk sind in allen Kopien oder Teilkopien der Software beizulegen.

DIE SOFTWARE WIRD OHNE JEDE AUSDRÜCKLICHE ODER IMPLIZIERTE GARANTIE BEREITGESTELLT, EINSCHLIESSLICH DER GARANTIE ZUR BENUTZUNG FÜR DEN VORGESEHENEN ODER EINEM BESTIMMTEN ZWECK SOWIE JEGLICHER RECHTSVERLETZUNG, JEDOCH NICHT DARAUF BESCHRÄNKT. IN KEINEM FALL SIND DIE AUTOREN ODER COPYRIGHTINHABER FÜR JEGLICHEN SCHADEN ODER SONSTIGE ANSPRÜCHE HAFTBAR ZU MACHEN, OB INFOLGE DER ERFÜLLUNG EINES VERTRAGES, EINES DELIKTES ODER ANDERS IM ZUSAMMENHANG MIT DER SOFTWARE ODER SONSTIGER VERWENDUNG DER SOFTWARE ENTSTANDEN.
