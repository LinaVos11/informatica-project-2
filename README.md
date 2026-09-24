<p align="center">
  <img alt="header" src="https://shieldcn.dev/header/surface.svg?title=SongSip&amp;subtitle=Discover+a+new+song+every+day%21&amp;mode=dark" />
</p>

## Welkom bij SongSip

SongSip is een website waar je elke dag een nieuw liedje kan ontdekken. In plaats van eindeloos door afspeellijsten te scrollen, krijgt de bezoeker bij elk bezoek of bij een klik op de knop **één willekeurig nummer** voorgeschoteld.

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




