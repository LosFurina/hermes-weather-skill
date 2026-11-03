# Hermes skill tap — open-meteo-weather

A [Hermes Agent](https://github.com/NousResearch/hermes-agent) skill tap with one skill:

| Skill | What it does |
|---|---|
| [`open-meteo-weather`](skills/open-meteo-weather/SKILL.md) | Current weather + 1–7 day forecast for any city or `lat,lon` via [Open-Meteo](https://open-meteo.com). Standard-library Python, no API key, °F or metric. |

Built for USC CSCI 599 Assignment 3 (personal assistant with hybrid LLM routing) by Weijun Li.

## Install on Hermes

```bash
hermes skills tap add LosFurina/hermes-weather-skill
hermes skills search open-meteo --source github
hermes skills install LosFurina/hermes-weather-skill/open-meteo-weather
```

Then ask the agent e.g. *"Do I need an umbrella in Seattle tomorrow?"*.

## Run the helper directly

```bash
python3 skills/open-meteo-weather/scripts/forecast.py "Los Angeles" --text
python3 skills/open-meteo-weather/scripts/forecast.py "Berlin, Germany" --days 3 --metric
```

Weather data © Open-Meteo, CC BY 4.0. Code: MIT.
