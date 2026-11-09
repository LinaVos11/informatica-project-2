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
- Dataset inladen
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

# Screenshots van onze uiteindelijke website:
<img width="2251" height="1041" alt="Schermafbeelding 2026-11-09 203401" src="https://github.com/user-attachments/assets/901bb3a7-19dd-477a-8d6d-d890a94c26a7" />

<img width="2373" height="1082" alt="Schermafbeelding 2026-11-09 203216" src="https://github.com/user-attachments/assets/d65f233d-4c13-4a55-a82b-47f410aa8f07" />

<img width="2361" height="1051" alt="Schermafbeelding 2026-11-09 203340" src="https://github.com/user-attachments/assets/cd2d5c77-4f7f-4757-9c95-62eb1eed477c" />

<img width="2353" height="973" alt="Schermafbeelding 2026-11-09 203046" src="https://github.com/user-attachments/assets/bd6b9119-4573-4214-940a-f19a236cd42b" />

<img width="2376" height="911" alt="image" src="https://github.com/user-attachments/assets/a3d60df3-72ca-422c-b753-4fe9accb1e85" />

