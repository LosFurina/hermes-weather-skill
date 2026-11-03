#!/usr/bin/env python3
"""Weather forecast from Open-Meteo (https://open-meteo.com): free, no API key, stdlib only.

  python3 forecast.py "Los Angeles"                 # today, °F, JSON
  python3 forecast.py "Berlin" --days 3 --metric    # 3 days, °C / km/h / mm
  python3 forecast.py "Tokyo" --text                # human-readable lines instead of JSON

Location may be a city name ("Paris", "Paris, France") or "lat,lon" ("34.05,-118.24").
Exit code 2 = unknown location, 3 = network/API error (message on stderr).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

UA = {"User-Agent": "hermes-skill-open-meteo-weather/1.0"}
WMO = {0: "clear", 1: "mostly clear", 2: "partly cloudy", 3: "overcast", 45: "fog", 48: "rime fog",
       51: "light drizzle", 53: "drizzle", 55: "heavy drizzle", 56: "freezing drizzle",
       57: "freezing drizzle", 61: "light rain", 63: "rain", 65: "heavy rain", 66: "freezing rain",
       67: "freezing rain", 71: "light snow", 73: "snow", 75: "heavy snow", 77: "snow grains",
       80: "rain showers", 81: "rain showers", 82: "violent rain showers", 85: "snow showers",
       86: "snow showers", 95: "thunderstorm", 96: "thunderstorm with hail", 99: "thunderstorm with hail"}
_LATLON = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*$")


def _get(url: str, params: dict) -> dict:
    req = urllib.request.Request(url + "?" + urllib.parse.urlencode(params), headers=UA)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())


def geocode(query: str) -> dict:
    m = _LATLON.match(query)
    if m:
        return {"name": query.strip(), "lat": float(m[1]), "lon": float(m[2]), "timezone": "auto"}
    name, _, country = query.partition(",")
    res = _get("https://geocoding-api.open-meteo.com/v1/search",
               {"name": name.strip(), "count": 10, "language": "en", "format": "json"}).get("results") or []
    if country.strip():   # "Paris, France" / "Portland, OR": prefer a matching country or region
        want = country.strip().lower()
        res = [r for r in res if want in (r.get("country", "") + " " + r.get("country_code", "") + " "
                                          + r.get("admin1", "")).lower()] or res
    if not res:
        raise LookupError(f"unknown location: {query}")
    r = res[0]
    label = ", ".join(x for x in (r.get("name"), r.get("admin1"), r.get("country_code")) if x)
    return {"name": label, "lat": r["latitude"], "lon": r["longitude"], "timezone": r.get("timezone", "auto")}


def forecast(query: str, days: int = 1, metric: bool = False) -> dict:
    place = geocode(query)
    units = ({} if metric else {"temperature_unit": "fahrenheit", "wind_speed_unit": "mph",
                                "precipitation_unit": "inch"})
    d = _get("https://api.open-meteo.com/v1/forecast", {
        "latitude": place["lat"], "longitude": place["lon"], "timezone": place["timezone"],
        "forecast_days": max(1, min(days, 7)), **units,
        "current": "temperature_2m,apparent_temperature,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,"
                 "uv_index_max,sunrise,sunset"})
    cur, dl = d.get("current", {}), d.get("daily", {})
    t = "C" if metric else "F"
    return {
        "location": place["name"], "timezone": d.get("timezone"), "units": {"temp": f"°{t}",
                                                                              "wind": "km/h" if metric else "mph"},
        "now": {"temp": cur.get("temperature_2m"), "feels_like": cur.get("apparent_temperature"),
                "summary": WMO.get(cur.get("weather_code"), "unknown"), "wind": cur.get("wind_speed_10m")},
        "days": [{"date": day, "summary": WMO.get(dl["weather_code"][i], "unknown"),
                  "high": dl["temperature_2m_max"][i], "low": dl["temperature_2m_min"][i],
                  "rain_chance_pct": dl["precipitation_probability_max"][i], "uv_max": dl["uv_index_max"][i],
                  "sunrise": dl["sunrise"][i][-5:], "sunset": dl["sunset"][i][-5:]}
                 for i, day in enumerate(dl.get("time", []))],
        "source": "open-meteo.com (CC BY 4.0)"}


def as_text(f: dict) -> str:
    u = f["units"]["temp"]
    lines = [f"{f['location']}: now {f['now']['temp']}{u} (feels {f['now']['feels_like']}{u}), "
             f"{f['now']['summary']}, wind {f['now']['wind']} {f['units']['wind']}"]
    lines += [f"{d['date']}: {d['summary']}, {d['low']}–{d['high']}{u}, rain {d['rain_chance_pct']}%, "
              f"UV {d['uv_max']}, sun {d['sunrise']}–{d['sunset']}" for d in f["days"]]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("location")
    ap.add_argument("--days", type=int, default=1, help="1-7 (default 1)")
    ap.add_argument("--metric", action="store_true", help="°C, km/h, mm instead of °F, mph, inch")
    ap.add_argument("--text", action="store_true", help="plain text instead of JSON")
    a = ap.parse_args(argv)
    try:
        f = forecast(a.location, a.days, a.metric)
    except LookupError as exc:
        print(exc, file=sys.stderr)
        return 2
    except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as exc:
        print(f"open-meteo error: {exc}", file=sys.stderr)
        return 3
    print(as_text(f) if a.text else json.dumps(f, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
