---
name: open-meteo-weather
description: "Current weather and up-to-7-day forecasts for any city or lat,lon via Open-Meteo — no API key."
version: 1.0.1
author: Weijun Li (CSCI 599 A3)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Weather, Forecast, Open-Meteo, Travel, Briefing]
    related_skills: []
---

# Open-Meteo Weather

## When to use

Use when the user asks about the weather, temperature, rain, UV, sunrise/sunset, what to wear,
or whether to take an umbrella — now or for the next 1–7 days — for a named place or coordinates.
Also use it for the weather section of a daily briefing.

## How

Run the helper with your **terminal** tool (there is no separate weather tool). It uses only the
Python standard library and the free Open-Meteo API — no key, no account, nothing to install.
The path below is filled in by Hermes when the skill is loaded:

```bash
python3 ${HERMES_SKILL_DIR}/scripts/forecast.py "Seattle, WA" --days 2 --text
python3 ${HERMES_SKILL_DIR}/scripts/forecast.py "Berlin, Germany" --days 3 --metric --text
python3 ${HERMES_SKILL_DIR}/scripts/forecast.py "34.05,-118.24"            # JSON output
```

- `--days N` (1–7) covers today plus the following days; "tomorrow" needs `--days 2`.
- Default units are °F / mph / inch; add `--metric` for °C / km/h / mm. Use metric when the user
  writes in metric or the place is outside the US, unless they asked otherwise.
- Disambiguate with a country or region after a comma: `"Portland, OR"`, `"Paris, France"`.
- Exit code 2 means the place was not found — ask the user to clarify instead of guessing.
  Exit code 3 is a network/API error — say the forecast is unavailable; never invent numbers.

## Answer format

Lead with what matters for the question (e.g. "Yes, take an umbrella: 70% rain after 3 pm"),
then one line per day: summary, low–high, rain chance. Mention UV only when ≥ 6 and wind only when
notable. Always name the resolved location so a wrong geocode is visible, and keep the units the
script reported. Data: Open-Meteo, CC BY 4.0.
