import datetime
import os
from urllib.parse import parse_qs, urlparse

import requests
from feedgen.feed import FeedGenerator
from flask import Flask, Response, jsonify, request

import db

app = Flask(__name__)
INTERNAL_UI = "http://127.0.0.1:8001"


def _query_label(query_url, query_name):
    if query_name:
        return str(query_name).strip()

    try:
        parsed = urlparse(query_url)
        params = parse_qs(parsed.query)
        search_text = params.get("search_text", [None])[0]
        if search_text:
            return str(search_text).strip()
    except Exception:
        pass

    return "Vinted"


def _item_url(item_id, query_url):
    try:
        parsed = urlparse(query_url)
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}/items/{item_id}"
    except Exception:
        pass
    return None


def _iso_timestamp(value):
    try:
        return datetime.datetime.fromtimestamp(
            float(value), tz=datetime.timezone.utc
        ).isoformat()
    except Exception:
        return None


def serialize_item(row):
    item_id, title, price, currency, timestamp, query_url, photo_url, query_name = row
    url = _item_url(item_id, query_url)
    if not url:
        return None

    try:
        numeric_price = float(price)
    except (TypeError, ValueError):
        return None

    return {
        "id": str(item_id),
        "title": str(title or "Vinted Deal"),
        "brand": _query_label(query_url, query_name),
        "price": numeric_price,
        "currency": str(currency or "EUR"),
        "size": None,
        "condition": None,
        "estimatedResale": None,
        "score": None,
        "url": url,
        "imageUrl": photo_url or None,
        "createdAt": _iso_timestamp(timestamp),
        "source": "resellzos-vinted-feed",
    }


def get_feed_items(limit=100):
    items = []
    for row in db.get_items(limit=limit):
        item = serialize_item(row)
        if item:
            items.append(item)
    return items


def build_rss(items, public_base):
    feed = FeedGenerator()
    feed.title("ResellzOS Vinted Feed")
    feed.description("Latest listings collected by the ResellzOS Vinted feed service")
    feed.link(href=f"{public_base.rstrip('/')}/rss")
    feed.language("de")

    for item in reversed(items):
        entry = feed.add_entry()
        entry.id(item["url"])
        entry.title(item["title"])
        entry.link(href=item["url"])

        description = (
            f"🆕 Title : {item['title']}\n"
            f"💶 Price : {item['price']} {item['currency']}\n"
            f"🛍️ Brand : {item['brand']}"
        )
        if item.get("imageUrl"):
            description += f"\n<a href=\"{item['imageUrl']}\">&#8205;</a>"
        entry.description(description)

        if item.get("createdAt"):
            try:
                published = datetime.datetime.fromisoformat(item["createdAt"])
                entry.published(published)
            except ValueError:
                pass

    return feed.rss_str(pretty=True)


@app.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "service": "ResellzOS Vinted Feed",
            "items": db.get_total_items_count(),
            "queries": db.get_total_queries_count(),
        }
    )


@app.get("/feed.json")
def json_feed():
    try:
        limit = max(1, min(int(request.args.get("limit", "100")), 500))
    except ValueError:
        limit = 100

    return jsonify({"items": get_feed_items(limit=limit)})


@app.get("/rss")
def rss_feed():
    try:
        limit = max(1, min(int(request.args.get("limit", "100")), 500))
    except ValueError:
        limit = 100

    public_base = request.url_root.rstrip("/")
    return Response(
        build_rss(get_feed_items(limit=limit), public_base),
        mimetype="application/rss+xml",
    )


@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def proxy_dashboard(path):
    target = f"{INTERNAL_UI}/{path}"

    headers = {
        key: value
        for key, value in request.headers
        if key.lower() not in {"host", "content-length", "connection"}
    }

    try:
        upstream = requests.request(
            method=request.method,
            url=target,
            params=request.args,
            data=request.get_data(),
            headers=headers,
            cookies=request.cookies,
            allow_redirects=False,
            timeout=20,
        )
    except requests.RequestException as error:
        return jsonify(
            {
                "status": "starting",
                "message": "Dashboard is not ready yet.",
                "error": str(error),
            }
        ), 503

    excluded = {"content-encoding", "content-length", "transfer-encoding", "connection"}
    response_headers = [
        (key, value)
        for key, value in upstream.headers.items()
        if key.lower() not in excluded
    ]

    location = upstream.headers.get("Location")
    if location and location.startswith(INTERNAL_UI):
        public_base = request.url_root.rstrip("/")
        response_headers = [
            (key, value)
            for key, value in response_headers
            if key.lower() != "location"
        ]
        response_headers.append(("Location", location.replace(INTERNAL_UI, public_base, 1)))

    return Response(
        upstream.content,
        status=upstream.status_code,
        headers=response_headers,
    )


def gateway_process():
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    gateway_process()
