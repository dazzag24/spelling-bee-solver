# Spelling Bee Helper - Agent Instructions

## Project Overview

A Flask web application that fetches daily puzzle data from [spellbee.org](https://spellbee.org/) and helps users find valid words based on the current day's letters and center letter.

## Architecture

- **Language**: Python 3.14+
- **Framework**: Flask with Playwright for browser automation
- **Deployment**: Docker multi-stage build (slim image)
- **Entry point**: `entrypoint.py` → `app.py`
- **Port**: 8080 (exposed as 8060 via docker-compose)

## Key Files

| File | Purpose |
|------|---------|
| `app/app.py` | Main Flask application with routes and puzzle logic |
| `entrypoint.py` | Starts Xvfb (virtual display) and launches the app |
| `docker-compose.yaml` | Service configuration |
| `Dockerfile.slim` | Multi-stage Docker build (builder + runtime) |
| `pyproject.toml` | Python dependencies managed by uv |

## Routes

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Renders the main form |
| `/solve` | POST | Returns words matching a prefix, filtered by current letters |
| `/letters` | GET | Returns the current day's letters |
| `/search` | GET | Autocomplete-style word search |

## Constraints

- **Do not modify** `Dockerfile.slim` or `docker-compose.yaml` without explicit user approval — these are intentionally optimized for minimal image size
- **Do not upgrade** Playwright beyond 1.62.0 without testing — browser compatibility with spellbee.org is critical
- **Preserve** the existing data flow: Playwright scrapes spellbee.org → Flask serves filtered results
- **Maintain** the 7-letter + 1 center-letter puzzle model
- **Keep** word length minimum of 4 characters

## Patterns

- Global state (`word_set`, `letters`, `center_letter`) is populated on startup and refreshed daily at 1:00 AM via APScheduler
- Word validation: must contain center letter, use only allowed letters, be ≥4 characters, match prefix
- Responses are JSON with consistent structure: `{words, count, pangrams}`
- Xvfb is required for headless Playwright operation in Docker

## Development Notes

- The app uses `uv` for dependency management (see `pyproject.toml`)
- Playwright browsers are pre-installed in the Docker builder stage and copied to runtime
- The runtime image uses a non-root user (`appuser:1000`)
- `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1` prevents duplicate downloads

## Testing

Run with `docker-compose up --build` and navigate to `http://localhost:8060`.

## Common Tasks

- Adding a new route: add to `app/app.py`, ensure it returns JSON
- Modifying word filtering: edit the validation logic in the `/solve` endpoint
- Updating dependencies: modify `pyproject.toml`, rebuild Docker image
