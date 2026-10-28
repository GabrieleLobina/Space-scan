"""Refresh Space Scan data. Network failures preserve the last verified snapshot."""
import datetime as dt
import json
import pathlib
import re
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data.json"
LAUNCH_API = "https://ll.thespacedevs.com/2.2.0/launch/upcoming/?limit=50&mode=detailed"
KEYWORDS = ("artemis", "spacex", "starship", "super heavy", "falcon 9", "falcon heavy", "orion", "sls")
UTC = dt.timezone.utc


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "SpaceScan/4.0 (github.com/GabrieleLobina/Space-scan)", "Accept": "application/json, application/xml, text/xml, */*"})
    with urllib.request.urlopen(req, timeout=25) as res:
        return res.read()


def parse_iso(value):
    if not value:
        return None
    try:
        result = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        return result.replace(tzinfo=UTC) if result.tzinfo is None else result.astimezone(UTC)
    except (ValueError, TypeError, AttributeError):
        return None


def normalize_launch(item):
    """Return a safe, sourced launch. Avoid a precise countdown for NET estimates."""
    name = str(item.get("name") or "").strip()
    provider = (item.get("launch_service_provider") or {}).get("name") or ""
    rocket = (item.get("rocket") or {}).get("configuration") or {}
    vehicle = rocket.get("full_name") or rocket.get("name") or "Veicolo da confermare"
    if not any(k in (name + " " + provider + " " + vehicle).lower() for k in ("spacex", "starship", "falcon", "artemis", "sls", "orion")):
        return None
    net = parse_iso(item.get("net"))
    if net is None:
        return None
    status = (item.get("status") or {}).get("name") or "TBD"
    status_text = status.lower()
    if any(k in status_text for k in ("launch successful", "failure", "in flight", "cancelled")):
        return None
    # Launch Library NET is a 'no earlier than' estimate, not necessarily a confirmed launch time.
    # Only show countdowns for statuses explicitly marked as Go for Launch.
    confirmed = "go for launch" in status_text
    pad = item.get("pad") or {}
    site = pad.get("name") or (pad.get("location") or {}).get("name") or ""
    url = item.get("url") or "https://ll.thespacedevs.com/"
    if not str(url).startswith("https://"):
        url = "https://ll.thespacedevs.com/"
    return {
        "name": name,
        "vehicle": str(vehicle),
        "date": net.isoformat().replace("+00:00", "Z") if confirmed else None,
        "window": "NET " + net.strftime("%d %b %Y, %H:%M UTC") if not confirmed else None,
        "precision": "datetime" if confirmed else "window",
        "status": "scheduled" if confirmed else "tentative",
        "site": str(site),
        "source": str(url),
        "provider": "Launch Library 2",
        "id": str(item.get("id") or name),
    }


def update_launches(data, payload, today):
    results = payload.get("results")
    if not isinstance(results, list):
        raise ValueError("Launch Library response missing results")
    launches = [x for item in results if (x := normalize_launch(item))]
    if not launches:
        raise ValueError("No matching upcoming launches; keeping existing snapshot")
    launches = launches[:12]
    previous = {x.get("id") or x.get("name"): x for x in data.get("launches", [])}
    changes = []
    for item in launches:
        old = previous.get(item["id"])
        if old and (old.get("date"), old.get("window"), old.get("status")) != (item["date"], item["window"], item["status"]):
            changes.append({"date": today, "text": f"Lancio aggiornato: {item['name']} — {item.get('window') or item.get('date')}"})
    data["launches"] = launches
    data.setdefault("changes", [])[:0] = changes[:10]


def news_items():
    items = []
    try:
        root = ET.fromstring(fetch("https://www.nasa.gov/feed/"))
        for entry in root.findall(".//item"):
            title = entry.findtext("title") or ""
            if any(k in title.lower() for k in ("artemis", "orion", "moon", "lunar", "space launch system", "sls")):
                items.append({"title": title, "url": entry.findtext("link") or "", "date": entry.findtext("pubDate") or "", "source": "NASA"})
    except Exception as exc:
        print("NASA RSS unavailable:", exc)
    try:
        response = json.loads(fetch("https://api.spaceflightnewsapi.net/v4/articles/?limit=100"))
        for entry in response.get("results", []):
            title = entry.get("title") or ""
            if any(k in (title + " " + (entry.get("summary") or "")).lower() for k in KEYWORDS):
                items.append({"title": title, "url": entry.get("url") or "", "date": entry.get("published_at") or "", "source": entry.get("news_site") or "Spaceflight News"})
    except Exception as exc:
        print("Spaceflight News unavailable:", exc)
    return items


def news_timestamp(item):
    value = item.get("date") or ""
    parsed = parse_iso(value)
    if parsed:
        return parsed.timestamp()
    try:
        return parsedate_to_datetime(value).timestamp()
    except (ValueError, TypeError, IndexError):
        return 0


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    today = dt.datetime.now(UTC).date().isoformat()
    try:
        update_launches(data, json.loads(fetch(LAUNCH_API)), today)
    except Exception as exc:
        print("Launch Library unavailable; preserving previous launches:", exc)
    fresh = news_items()
    if fresh:
        unique = {x["url"]: x for x in fresh if x.get("url", "").startswith("https://")}
        ordered = sorted(unique.values(), key=news_timestamp, reverse=True)
        old_urls = {x.get("url") for x in data.get("news", [])}
        count = sum(x["url"] not in old_urls for x in ordered)
        if count:
            data.setdefault("changes", []).insert(0, {"date": today, "text": f"{count} nuove notizie rilevate"})
        data["news"] = ordered[:15]
    data["changes"] = data.get("changes", [])[:30]
    data["updated"] = dt.datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
