# ResellzOS Vinted Feed – Koyeb Setup

Der Fork ist für einen einzelnen öffentlichen Web-Port vorbereitet.

## Öffentliche Endpunkte

Nach dem Deploy gilt bei deiner Koyeb-Domain:

- `/` – originales Vinted-Notifications Dashboard
- `/health` – Healthcheck
- `/feed.json` – strukturierter Feed für den ResellzOS Discord-Bot
- `/rss` – RSS-Feed als Fallback

Für den Discord-Bot ist `/feed.json` empfohlen.

## Koyeb

1. Create Web Service
2. GitHub als Quelle wählen
3. Repository: `batu030i/-ResellzOS-Vinted-Feed`
4. Branch: `main`
5. Builder: Dockerfile
6. Instance: Free
7. Region: Frankfurt, wenn verfügbar
8. Exposed port: `8000`, Protocol `HTTP`
9. Route: `/`
10. Health check: HTTP `/health`
11. Environment Variable: `PORT=8000`
12. Deploy

Danach sollte `https://DEINE-DOMAIN/health` JSON mit `status: ok` liefern.

## ResellzOS Discord-Bot

Beim Discord-Bot beim Hoster setzen:

```env
SNIPER_FEED_URL=https://DEINE-DOMAIN/feed.json
SNIPER_FEED_FORMAT=json
```

`SNIPER_FEED_TOKEN` wird für diesen öffentlichen Feed nicht benötigt.

Danach den Discord-Bot neu starten und `/sniper status` prüfen.

## Suchanfragen

Die Suchanfragen werden weiterhin über das normale Dashboard (`/`) verwaltet. Der ResellzOS-Gateway verändert den Vinted-Abrufcode nicht; er stellt nur die bereits gefundenen Daten für Discord als JSON/RSS bereit.

Wichtig: Gib einer Suchanfrage im Dashboard einen eindeutigen Namen wie `Lacoste`, `Nike`, `Ralph Lauren`, `Adidas`, `Tommy Hilfiger` oder `The North Face`. Dieser Name wird im JSON-Feed als `brand` verwendet und damit vom Discord-Bot in den passenden Premium-Kanal geroutet.
