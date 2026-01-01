# Quick Start Guide - African Air Traffic Ingestion

## 5-Minute Setup

### 1. Prerequisites Check
```bash
# Check Python version (need 3.11+)
python --version

# Check Docker installation
docker --version
docker-compose --version
```

### 2. Clone and Setup
```bash
# Navigate to project
cd african-air-traffic-analysis

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Copy environment template
cp .env.template .env

# Edit .env and add your API key
# Get free API key from: https://www.adsbexchange.com/data/
nano .env  # or use your preferred editor
```

Add your API key:
```bash
ADSBEXCHANGE_API_KEY=your_actual_api_key_here
```

### 4. Start Infrastructure
```bash
# Start Kafka and services
docker-compose up -d

# Check services are running
docker-compose ps

# Expected output: zookeeper, kafka, kafka-ui all running
```

### 5. Validate Setup
```bash
# Run validation tests
cd ingestion
python validate_ingestion.py all

# This will test:
# - Configuration
# - Storage paths
# - Geospatial filtering
# - Kafka connectivity
# - API connection
```

### 6. Test Live Data
```bash
# Fetch sample data to verify everything works
python validate_ingestion.py sample

# This will:
# - Connect to ADSBExchange
# - Fetch current flight positions
# - Filter to West Africa
# - Display sample flights
```

## Verify Everything is Working

### Check Kafka UI
Open browser to: http://localhost:8080

You should see:
- Cluster connected
- Topics created: `adsb.bronze.positions`, `adsb.bronze.metadata`

### Check Ingestion Logs
```bash
# View streaming ingestion logs
docker-compose logs -f stream-ingester

# Should see messages like:
# "Fetched 1234 aircraft positions"
# "Filtered 1234 positions -> 45 within West Africa"
```

### Check Data Files
```bash
# List stored data
ls -lh data/bronze/positions/

# Should see parquet files organized by date/time
tree data/bronze/
```

## Common Commands

### Start/Stop Services
```bash
# Start all
docker-compose up -d

# Stop all
docker-compose down

# Restart specific service
docker-compose restart stream-ingester

# View logs
docker-compose logs -f stream-ingester
docker-compose logs -f batch-ingester
```

### Manual Testing
```bash
cd ingestion

# Test geospatial filter
python validate_ingestion.py filter

# Test API connection
python validate_ingestion.py api

# Test Kafka
python validate_ingestion.py kafka

# Fetch live sample
python validate_ingestion.py sample
```

### Run Individual Services Locally
```bash
# Terminal 1: Streaming ingestion
python streaming_ingestion.py

# Terminal 2: Hourly snapshots
python batch_ingestion.py snapshot

# Terminal 3: Daily metadata
python batch_ingestion.py
```

## Expected Data Flow

### First Hour
```
1. Stream ingester starts polling ADSBExchange every 5 seconds
2. Each poll fetches ~5000-15000 global aircraft positions
3. Geospatial filter reduces to ~20-100 West Africa positions
4. Positions published to Kafka topic: adsb.bronze.positions
5. Snapshot captured at top of hour
6. Parquet file saved: data/bronze/positions/2025/01/01/12/snapshot_*.parquet
```

### First Day
```
1. Stream runs continuously, accumulating position data
2. Hourly snapshots capture point-in-time views (24 files)
3. End of day: Metadata batch extracts unique aircraft from previous day
4. Fetches aircraft details from ADSBDB for each unique ICAO code
5. Saves metadata: data/bronze/metadata/2025/01/01/metadata_*.parquet
6. Publishes to Kafka: adsb.bronze.metadata
```

## Monitoring

### Key Metrics to Watch

**Streaming Ingestion:**
- Requests per minute: ~12 (every 5 seconds)
- Filtering pass rate: ~1-3% for West Africa
- Kafka publish rate: ~20-100 messages per poll
- Error rate: <1%

**Batch Metadata:**
- Unique aircraft per day: ~500-2000 for West Africa
- ADSBDB API success rate: ~70-90%
- Rate limit compliance: 2 requests/second max

### Health Checks
```bash
# Check all services
docker-compose ps

# Check Kafka topics
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9093

# Check data size
du -sh data/bronze/*

# Check ingestion statistics
docker-compose logs stream-ingester | grep "Stats"
```

## Troubleshooting Quick Fixes

### Issue: No data in Kafka
```bash
# Restart ingestion service
docker-compose restart stream-ingester

# Check API key is set
docker-compose exec stream-ingester env | grep ADSBEXCHANGE
```

### Issue: Kafka connection refused
```bash
# Restart Kafka stack
docker-compose restart zookeeper kafka
sleep 30  # Wait for startup

# Re-run validation
python validate_ingestion.py kafka
```

### Issue: Permission errors on data folder
```bash
# Fix permissions
sudo chown -R $USER:$USER data/
chmod -R 755 data/
```

### Issue: High memory usage
```bash
# Check container stats
docker stats

# Reduce Kafka retention if needed
# Edit docker-compose.yml:
# KAFKA_LOG_RETENTION_HOURS: 24  # Instead of 168
```

## Next Steps

Once ingestion is running smoothly:

1. **Verify Data Quality** (Week 1)
   - Monitor data completeness
   - Check for gaps or anomalies
   - Validate position accuracy

2. **Build Silver Layer** (Week 2)
   - Data cleaning and deduplication
   - Schema enforcement
   - Quality metrics

3. **Create Gold Layer** (Week 3)
   - Aggregated analytics tables
   - Flight paths and trajectories
   - Airport activity summaries

4. **Add Orchestration** (Week 4)
   - Apache Airflow DAGs
   - Automated testing
   - Data quality checks

5. **Build Dashboards** (Week 5)
   - Real-time flight tracking
   - Historical trends
   - Airport analytics

## Getting Help

### Check Logs
```bash
# Application logs
docker-compose logs stream-ingester
docker-compose logs batch-ingester

# Kafka logs
docker-compose logs kafka

# All logs
docker-compose logs
```

### Debug Mode
```bash
# Run with debug logging
LOG_LEVEL=DEBUG docker-compose up stream-ingester
```

### Manual Debug Session
```bash
# Enter container
docker-compose exec stream-ingester bash

# Run Python interactively
python
>>> from config import config
>>> print(config.geo_bbox)
>>> exit()
```

## Resources

- **ADSBExchange API Docs**: https://www.adsbexchange.com/data/
- **ADSBDB API Docs**: https://api.adsbdb.com/
- **Kafka Documentation**: https://kafka.apache.org/documentation/
- **Project README**: See INGESTION_README.md for detailed documentation

## Success Indicators

You'll know everything is working when:

✅ Validation script shows all tests passing  
✅ Docker containers stay running (not restarting)  
✅ Kafka UI shows messages flowing through topics  
✅ New parquet files appear every hour in data/bronze/positions/  
✅ Logs show successful API fetches and filtering  
✅ No error messages in container logs  

**Happy ingesting!** 🚀✈️