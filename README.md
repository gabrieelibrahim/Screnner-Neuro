# ScannerNeuro IDX Breakout

Professional breakout screener for the Indonesian stock market (IDX) using yfinance.

## Architecture
- **FastAPI**: REST API serving data
- **PostgreSQL**: Stores historical signals, alerts, and market data
- **Redis**: Caching indicators and deduplicating alerts
- **APScheduler**: Running tasks every 5 minutes
- **yfinance**: Market data source (Batch download)

## Features
- Breakout Detection & Anti-Fakeout filter
- RVOL (Relative Volume) analysis
- Telegram alerts for top setups
- Momentum ranking engine

## Quickstart
1. Copy `.env.example` to `.env` and fill the keys.
2. Run `docker-compose up -d --build`.
