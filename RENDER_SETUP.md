# ResellzOS Vinted Feed – Render Setup

Der Fork ist für einen kostenlosen Render Web Service vorbereitet.

## Render

1. Öffne Render und erstelle einen neuen **Web Service**.
2. Verbinde GitHub und wähle `batu030i/-ResellzOS-Vinted-Feed`.
3. Branch: `main`.
4. Render erkennt das Dockerfile bzw. kann `render.yaml` verwenden.
5. Instance Type: **Free**.
6. Health Check Path: `/health`.
7. `PORT=10000` ist bereits im Blueprint hinterlegt.
8. Deploy starten.

## Öffentliche Endpunkte

Nach erfolgreichem Deploy:

- `/` – Dashboard
- `/health` – Status
- `/feed.json` – empfohlener Feed für den ResellzOS Discord-Bot
- `/rss` – RSS-Fallback

## Discord-Bot

Beim Discord-Bot später setzen:

```env
SNIPER_FEED_URL=https://DEIN-SERVICE.onrender.com/feed.json
SNIPER_FEED_FORMAT=json
```

Danach Bot neu starten und `/sniper status` prüfen.

## Free-Plan Hinweis

Render-Free nutzt ein flüchtiges Dateisystem. Lokale SQLite-Daten können bei Neustarts, Redeploys oder Spin-down verloren gehen. Für Tests ist das ausreichend; für dauerhaften Betrieb sollte die Konfiguration später persistent ausgelagert werden.
