# Financial News Intelligent Monitoring System

Automated collection of financial news sources (e.g. cls.cn), extraction of sectors and companies via DeepSeek LLM, financial heat scoring (0-10), and front-end display of hotspots by sector for the past 5 days.

## What It Does

- **Scrapy + Playwright Crawler**: Auto-fetches cls.cn telegraph news, renders JS pages, scheduled incremental collection
- **LangChain + DeepSeek Agent**: Two intelligent pipelines — sector/company extraction + financial heat analysis
- **Spring Boot Backend**: REST API (`/health` `/login` `/data`), JPA persistence, daily-rotating HMAC token auth
- **Vue 3 Frontend**: Sector dropdown lists + company heat display, login auth, 5-day news filter
- **FastAPI Scheduling Service**: Startup → 30min → 1h crawling schedule, auto-triggers Agent analysis after each crawl
- **Prometheus + Grafana Monitoring**: Full coverage of backend JVM, host CPU/Memory/Disk, MySQL status
- **Docker Compose One-Click Deploy**: 11 services orchestrated, Kubernetes configs provided

## Architecture

```
Frontend (Vue 3 :3001)
  │  /api → nginx proxy
  ▼
Backend (Spring Boot :5070)
  │  JPA → MySQL
  ▼
MySQL (:3306) ←── Agent writes
  ▲
Crawler (FastAPI :5080)
  │  Scrapy + Playwright → News data
  │  LangChain + DeepSeek → Sector / Company / Heat score
  └─→ DB writes (t_field / t_company / t_news)

Monitoring (Prometheus :9090 + Grafana :3000)
  ├─ Spring Boot Micrometer :5071
  ├─ node_exporter ×3
  └─ mysqld_exporter
```

## Quick Start

### 1. Required Config After Cloning

| File | Field | Notes |
|------|-------|-------|
| `main/crawler/conf/agent.json` | `api_key` | Your DeepSeek API key (see `agent.example.json`) |

### 2. Docker Compose One-Click Deploy

```bash
cd run
docker compose up -d --build
```

Ensure data directory permissions on first run:
```bash
sudo chown -R 65534:65534 data/prometheus
sudo chown -R 472:472 data/grafana
mkdir -p data/mysql main/crawler/output main/crawler/logs
```

Exposed ports:

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3001 | Vue web UI |
| Grafana  | 3000 | Monitoring dashboard (admin/admin) |

## Future Improvements

- [ ] Support more news sources (interfaces ready, crawling logic not yet tuned)
- [ ] More effective and richer Agent strategies. Currently agents independently score heat and extract news info, mainly for learning purposes. Prompts are rudimentary and heat analysis lacks solid data support. Future work should build an evaluation system incorporating historical news.
- [ ] More robust project architecture. Due to limited development time and experience, many aspects — code decoupling, layer separation, config isolation — remain incomplete.
