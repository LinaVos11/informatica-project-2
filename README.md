<p align="center">
  <img alt="header" src="https://shieldcn.dev/header/surface.svg?title=SongSip&amp;subtitle=Discover+a+new+song+every+day%21&amp;mode=dark" />
</p>

## Welkom bij SongSip

SongSip is een website waar je elke dag een nieuw liedje kan ontdekken. In plaats van eindeloos door afspeellijsten te scrollen, krijgt de bezoeker bij elk bezoek of bij een klik op de knop **één willekeurig nummer** voorgeschoteld of een willekeurig nummer van een gekozen genre. Je krijgt dan naast de titel, ook het album, de artiest en de spotifylink te zien.

# Beoordeling 
Wij willen ons project laten beoordelen op de volgende domeinen:
1. Website
2. Interactie
3. Database

# Planning 
| Week:  |  Wat moet af? |
|---|---|
| standup 1-2  | Fase 1  |
| standup 3  | goed begin fase 2 |
| standup 4    | fase 2 af, start fase 3  |
| standup 5  | sprint review & verder fase 3  |
| standup 6  | fase 3 af, begin aan fase 5 en 6  |
| eindpresentatie | alles af |

* onder voorbehoud, kan verschoven worden

# Functionaliteiten: 
* gebruiker kan inloggen met Spotify
* gebruiker kan genre kiezen
* website geeft een nummer
* nummer moet uit de dataset komen
* nummer mag niet eerder aan deze gebruiker zijn voorgeschoteld
* informatie over nummer wordt weergegeven
* gebruiker kan Spotify-link openen
* genres van opgeslagen nummers en recente afspeelbeurten worden gebruikt om binnen de gekozen muziekgroep vaker een passend datasetgenre aan te bevelen
* gebruiker kan nummer liken/disliken
* website onthoudt voorkeur
* gebruiker kan later opnieuw inloggen

# MoSCoW-prioriteiten

### Must have
* genre kiezen
* nummer selecteren
* informatie tonen
* nieuw nummer per gebruiker
* like/dislike opslaan

### Should have
* Spotify koppelen
* mooie albumafbeelding
* geschiedenis bekijken
* eenvoudige personalisatie

### Could have
* statistieken
* "jouw muzieksmaak"
* aanbevelingen op basis van eerdere likes


# Architectuur website


                    Website
                       │
                 HTML + CSS
                       │
                       ▼
                     Flask
                       │
                     Python
                  ┌────┴────┐
                  │         │
                  ▼         ▼
               Dataset   Database
                  │         │
                  ▼         ├── Gebruikers
                Muziek      ├── Likes
                            └── Gezien
                  │
                  └──────────┐
                             ▼
                        Spotify API
                             │
                             ▼
                    Spotify-account

# Projectfasen

### Fase 1 — Voorbereiding

- Eisen en functionaliteiten bepalen
- User stories maken
- Dataset kiezen en onderzoeken
- Technische architectuur bepalen
- Database-ontwerp maken
- Taken verdelen

### Fase 2 — Basiswebsite

- Flask-project opzetten
- HTML/CSS-structuur maken
- Dataset inladen (onze dataset: https://www.kaggle.com/datasets/saichaitanyareddyai/spotify-tracks-dataset-audio-features/data?utm_source=chatgpt.com)
- Genrekeuze maken
- Nummer selecteren en informatie weergeven

### Fase 3 — Database

- SQLite koppelen aan Flask
- Gebruikers en nummers opslaan
- Likes/dislikes opslaan
- Bijhouden welke nummers een gebruiker al heeft gezien
- Voorkomen dat hetzelfde nummer opnieuw wordt voorgesteld

### Fase 4 — Spotify-integratie

- Spotify Developer App instellen
- OAuth/inlogsysteem bouwen
- Spotify-gebruiker herkennen en koppelen aan onze database
- Spotify-links naar nummers toevoegen

### Fase 5 — Integratie

- Alle onderdelen samenvoegen
- Volledige gebruikersflow implementeren:
  **inloggen → genre kiezen → nummer krijgen → luisteren → like/dislike**
- Foutafhandeling toevoegen

### Fase 6 — Verbeteren & testen

- Website vormgeving verbeteren
- Functionaliteiten testen
- Bugs oplossen
- Gebruiksvriendelijkheid verbeteren
- Eventueel personalisatie/recommendatie-algoritme toevoegen

### Eindresultaat

Een website waarop gebruikers met hun Spotify-account kunnen inloggen, een genre kunnen kiezen en dagelijks een nieuw nummer uit onze dataset kunnen ontdekken. De website onthoudt welke nummers de gebruiker al heeft gezien en welke nummers de gebruiker leuk of niet leuk vond.

## SongSip lokaal starten op Windows

SongSip is een lokale Flask-applicatie en staat niet online. Iedereen die de app
draait, heeft eigen inloggegevens van een Spotify Developer-app nodig. Deel je
Spotify Client Secret niet en voeg die nooit toe aan de ZIP van het project.

### Benodigdheden

- Windows
- Python 3.10 of nieuwer
- Een Spotify-account
- Internetverbinding voor Spotify-login en Spotify API-verzoeken

### 1. Pak het project uit

Pak de project-ZIP uit in een map, bijvoorbeeld:

```text
C:\SongSip
```

Open PowerShell in die map. Je moet daar `requirements.txt` en de map `SongSip`
kunnen zien.

### 2. Maak een virtuele omgeving en installeer de benodigdheden

Voer deze opdrachten uit vanuit de hoofdmap van het project:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Als `py` niet wordt herkend, installeer Python en zorg dat de Python Launcher
beschikbaar is, of vervang `py` door `python`.

### 3. Maak een Spotify Developer-app aan

1. Log in op het Spotify Developer Dashboard en maak een app aan. (website: https://developer.spotify.com/dashboard)
2. Voeg bij de instellingen van die app deze exacte Redirect URI toe:

   ```text
   http://127.0.0.1:5000/callback
   ```

 En als website code voor Songsip: http://127.0.0.1:5000
3. Sla de instellingen op en kopieer de **Client ID** en **Client Secret** van
   de app.

De Client ID en Client Secret horen bij de Spotify Developer-app; het zijn niet
je Spotify-gebruikersnaam of wachtwoord. Houd de Client Secret privé. Iedereen
die een eigen kopie van SongSip gebruikt, maakt zelf een Spotify Developer-app
aan en gebruikt de eigen gegevens daarvan.

### 4. Zet de gegevens in een lokaal `.env`-bestand

Kopieer in de hoofdmap van het project `.env.example` naar een nieuw bestand
met de naam `.env`. Open `.env` en vul de waarden van je eigen Spotify
Developer-app in:

```text
SPOTIFY_CLIENT_ID=je_client_id
SPOTIFY_CLIENT_SECRET=je_client_secret
FLASK_SECRET_KEY=
```

Zet geen aanhalingstekens om de waarden. Je kunt `FLASK_SECRET_KEY` leeg laten
voor lokaal gebruik; SongSip maakt bij het starten zelf een tijdelijke sleutel
aan.

Het `.env`-bestand is alleen voor jouw computer. Commit of upload dit bestand
niet en voeg het niet toe aan een ZIP die je deelt. De app leest `.env` uit de
hoofdmap van het project. Er is geen formulier op de website om een Client ID
of Client Secret in te voeren.

### 5. Start de website

Start de Flask-server vanuit de hoofdmap van het project:

```powershell
.\.venv\Scripts\python.exe .\SongSip\app.py
```

Laat het PowerShell-venster open zolang je de website gebruikt. Open in je
browser:

```text
http://127.0.0.1:5000
```

Kies **LOG IN WITH SPOTIFY** en geef de app toestemming. Daarna kun je nummers
ontdekken en beoordelen. Stop de server door in PowerShell op `Ctrl+C` te
drukken.

Bij de eerste start wordt de lokale SQLite-database aangemaakt. De nummers
komen uit het datasetbestand `SongSip\spotify_tracks.csv.zip`; laat dit bestand
in de map `SongSip` staan.


## Problemen oplossen

- **Spotify meldt dat de Redirect URI ongeldig is:** controleer of in het
  Spotify Developer Dashboard exact `http://127.0.0.1:5000/callback` staat.
- **De app meldt dat Spotify niet is ingesteld:** controleer of `.env` in de
  hoofdmap staat, of de namen van de variabelen exact kloppen en of de waarden
  zijn ingevuld. Start de server opnieuw nadat je `.env` hebt aangepast.
- **De website is niet bereikbaar:** controleer of de server nog draait in
  PowerShell en open `http://127.0.0.1:5000` op dezelfde computer.
- **Nummers kunnen niet worden geladen:** controleer of
  `SongSip\spotify_tracks.csv.zip` aanwezig is en of er internetverbinding is.


# Screenshots van onze uiteindelijke website:
<img width="2251" height="1041" alt="Schermafbeelding 2026-11-09 203401" src="https://github.com/user-attachments/assets/901bb3a7-19dd-477a-8d6d-d890a94c26a7" />

<img width="2373" height="1082" alt="Schermafbeelding 2026-11-09 203216" src="https://github.com/user-attachments/assets/d65f233d-4c13-4a55-a82b-47f410aa8f07" />

<img width="2361" height="1051" alt="Schermafbeelding 2026-11-09 203340" src="https://github.com/user-attachments/assets/cd2d5c77-4f7f-4757-9c95-62eb1eed477c" />

<img width="2353" height="973" alt="Schermafbeelding 2026-11-09 203046" src="https://github.com/user-attachments/assets/bd6b9119-4573-4214-940a-f19a236cd42b" />

<img width="2376" height="911" alt="image" src="https://github.com/user-attachments/assets/a3d60df3-72ca-422c-b753-4fe9accb1e85" />