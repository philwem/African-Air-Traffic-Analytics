# African Air Traffic Analysis - Data Ingestion & Bronze Layer

## Overview

This module implements the **Bronze Layer** of the data platform, handling dual ingestion strategies:

- **Streaming Ingestion**: Real-time ADS-B flight position data from ADSBExchange
- **Batch Ingestion**: Hourly snapshots and daily aircraft metadata from ADSBDB API

All data is geospatially filtered to **West Africa** (4°N-20°N, 17°W-15°E) before storage.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Data Sources                             │
├──────────────────────┬──────────────────────────────────────┤
│  ADSBExchange API    │         ADSBDB API                   │
│  (Live Positions)    │      (Aircraft Metadata)             │
└──────────┬───────────┴───────────────┬──────────────────────┘
           │                           │
           ▼                           ▼
    ┌─────────────┐            ┌──────────────┐
    │  Streaming  │            │    Batch     │
    │  Ingester   │            │  Ingester    │
    └──────┬──────┘            └──────┬───────┘
           │                          │
           ▼                          ▼
    ┌──────────────────────────────────────┐
    │     Geospatial Filter (West Africa)   │
    └──────┬──────────────────┬────────────┘
           │                  │
           ▼                  ▼
    ┌─────────┐        ┌──────────┐
    │  Kafka  │        │  Parquet │
    │ Topics  │        │  Files   │
    └─────────┘        └──────────┘
          │                   │
          └─────────┬─────────┘
                    ▼
            ┌──────────────┐
            │ Bronze Layer │
            │  (Raw Data)  │
            └──────────────┘
```

## Components

### 1. Configuration (`config.py`)
- Centralized configuration management
- Environment variable handling
- West Africa bounding box definition
- API credentials and endpoints
- Kafka topics and storage paths

### 2. Geospatial Filter (`geospatial_filter.py`)
- Real-time position filtering
- Bounding box validation
- Airport proximity detection
- Position enrichment
- Filtering statistics

### 3. Streaming Ingestion (`streaming_ingestion.py`)
- Continuous polling of ADSBExchange API
- Real-time geospatial filtering
- Kafka message production
- Error handling and retry logic
- Performance monitoring

### 4. Batch Ingestion (`batch_ingestion.py`)
- Hourly position snapshots
- Daily aircraft metadata extraction
- ADSBDB API integration
- Rate limiting and backoff
- Parquet file storage

## Setup Instructions

### Prerequisites

1. **Python 3.11+**
2. **Docker & Docker Compose**
3. **ADSBExchange API Key** - [Register here](https://www.adsbexchange.com/data/)

### Installation

1. **Clone the repository**
```bash
cd african-air-traffic-analysis
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.template .env
# Edit .env and add your ADSBEXCHANGE_API_KEY
```

5. **Create data directories**
```bash
mkdir -p data/bronze/positions data/bronze/metadata data/bronze/logs
```

### Running with Docker Compose

**Start all services:**
```bash
docker-compose up -d
```

This launches:
- Zookeeper (port 2181)
- Kafka (port 9092)
- Kafka UI (port 8080)
- Stream Ingester
- Batch Ingester
- Snapshot Ingester

**View logs:**
```bash
docker-compose logs -f stream-ingester
docker-compose logs -f batch-ingester
```

**Stop services:**
```bash
docker-compose down
```

**Monitor Kafka:**
- Open browser to http://localhost:8080
- View topics, messages, and consumer groups

### Running Locally (without Docker)

**Terminal 1 - Start Kafka:**
```bash
# Requires local Kafka installation
$KAFKA_HOME/bin/zookeeper-server-start.sh config/zookeeper.properties
```

**Terminal 2 - Start Kafka Broker:**
```bash
$KAFKA_HOME/bin/kafka-server-start.sh config/server.properties
```

**Terminal 3 - Stream Ingestion:**
```bash
cd ingestion
python streaming_ingestion.py
```

**Terminal 4 - Hourly Snapshots:**
```bash
cd ingestion
python batch_ingestion.py snapshot
```

**Terminal 5 - Daily Metadata:**
```bash
cd ingestion
python batch_ingestion.py
```

## Kafka Topics

| Topic | Description | Retention |
|-------|-------------|-----------|
| `adsb.raw.positions` | Raw unfiltered positions | 24 hours |
| `adsb.bronze.positions` | Filtered West Africa positions | 7 days |
| `adsb.bronze.metadata` | Aircraft metadata | 30 days |

## Data Schema

### Position Message
```json
{
  "hex": "39C541",
  "flight": "ETH501",
  "lat": 9.0255,
  "lon": 38.7469,
  "alt_baro": 35000,
  "alt_geom": 35500,
  "gs": 445.2,
  "track": 185.4,
  "baro_rate": 0,
  "squawk": "2514",
  "category": "A3",
  "nav_qnh": 1013.6,
  "nav_altitude_mcp": 35008,
  "seen": 0.1,
  "rssi": -24.5,
  "ingestion_timestamp": "2025-01-01T12:30:45.123Z",
  "filtered_at": "2025-01-01T12:30:45.456Z",
  "source": "adsbexchange",
  "region": "west_africa",
  "nearest_airport": "ACC",
  "airport_name": "Accra Kotoka",
  "country": "Ghana"
}
```

### Aircraft Metadata
```json
{
  "icao": "39C541",
  "registration": "ET-APZ",
  "manufacturername": "Boeing",
  "model": "777-360ER",
  "operator": "Ethiopian Airlines",
  "operatoricao": "ETH",
  "registered_owner_country_name": "Ethiopia",
  "built": "2015",
  "engines": "2",
  "engine_type": "Jet",
  "metadata_fetched_at": "2025-01-01T00:15:30.789Z",
  "source": "adsbdb"
}
```

## Storage Structure

```
data/bronze/
├── positions/
│   ├── 2025/
│   │   ├── 01/
│   │   │   ├── 01/
│   │   │   │   ├── 00/
│   │   │   │   │   └── snapshot_20250101_000000.parquet
│   │   │   │   ├── 01/
│   │   │   │   │   └── snapshot_20250101_010000.parquet
├── metadata/
│   ├── 2025/
│   │   ├── 01/
│   │   │   ├── 01/
│   │   │   │   └── metadata_20250101_001530.parquet
└── logs/
    └── ingestion_20250101.log
```

## Configuration

### West Africa Bounding Box

Default coordinates (can be modified in `config.py`):
- **Min Latitude**: 4.0°N
- **Max Latitude**: 20.0°N  
- **Min Longitude**: 17.0°W
- **Max Longitude**: 15.0°E

### Major Airports Covered

- Lagos Murtala Muhammed (LOS) - Nigeria
- Accra Kotoka (ACC) - Ghana
- Abidjan Felix Houphouet-Boigny (ABJ) - Ivory Coast
- Dakar Blaise Diagne (DKR) - Senegal
- Abuja Nnamdi Azikiwe (ABV) - Nigeria
- Niamey Diori Hamani (NIM) - Niger
- Ouagadougou (OUA) - Burkina Faso
- Freetown Lungi (FNA) - Sierra Leone
- Cotonou Cadjehoun (COO) - Benin
- Lome Gnassingbe Eyadema (LFW) - Togo

## Monitoring

### Streaming Statistics
- Requests per minute
- Filtering pass rate
- Kafka publish rate
- Error rate

### Batch Statistics
- Aircraft processed
- Metadata fetch success rate
- Storage write performance
- API rate limit adherence

## Troubleshooting

### Issue: No data being ingested

**Check:**
1. API key is valid: `echo $ADSBEXCHANGE_API_KEY`
2. Kafka is running: `docker-compose ps`
3. Network connectivity to APIs
4. View ingester logs: `docker-compose logs stream-ingester`

### Issue: High filtering rate (few positions passing)

**Possible causes:**
1. Limited air traffic in West Africa at current time
2. Bounding box misconfiguration
3. API returning global data correctly filtered

**Verify:**
```bash
# Check bounding box
python -c "from config import config; print(config.geo_bbox)"
```

### Issue: Kafka connection errors

**Solutions:**
```bash
# Restart Kafka services
docker-compose restart kafka zookeeper

# Check Kafka is healthy
docker-compose ps kafka
```

## Performance Tuning

### Streaming Ingestion
- Adjust `stream_poll_interval` in config (default: 5 seconds)
- Increase Kafka batch size for higher throughput
- Use multiple consumer partitions

### Batch Ingestion
- Adjust `rate_limit_delay` for ADSBDB API
- Increase `max_retries` for reliability
- Optimize parquet compression settings

## Next Steps

After bronze layer is operational:
1. **Silver Layer**: Data cleaning, deduplication, validation
2. **Gold Layer**: Aggregations, analytics-ready tables
3. **Orchestration**: Airflow DAGs for scheduling
4. **Monitoring**: Grafana dashboards for metrics
5. **Testing**: Unit tests and integration tests

## API Documentation

- **ADSBExchange**: https://www.adsbexchange.com/data/
- **ADSBDB**: https://api.adsbdb.com/

## License

[Your License]

## Contact

[Your Contact Information]