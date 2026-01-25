# ADS-B Data Providers Registration
## African Air Traffic DataHouse & Analytics Platform

This document formally registers the ADS-B data providers used by the platform.
These providers supply real-time aircraft position data that forms the backbone
of all downstream analytics.

---

## 1. OpenSky Network

**Provider Name:** OpenSky Network  
**Provider Type:** ADS-B Flight Tracking Network  
**Access Method:** REST API  
**Primary Endpoint:** `/api/states/all`  
**Authentication:** Optional (rate-limited without login)

### Data Provided
- Live aircraft position data
- ICAO24 aircraft identifiers
- Latitude / Longitude
- Altitude, velocity, track (when available)
- On-ground status

### Update Frequency
- Near real-time (seconds)

### Strengths
- Free and open access
- Well-documented API
- Suitable for academic and portfolio projects
- Historical datasets available

### Limitations
- Strict rate limits
- Some fields frequently null
- Receiver density varies across Africa

### Usage in This Platform
- Baseline ADS-B provider
- Primary source for schema definition
- Used when ADSBExchange data is unavailable

---

## 2. ADSBExchange

**Provider Name:** ADSBExchange  
**Provider Type:** ADS-B Flight Tracking Network  
**Access Method:** REST API / Streaming  
**Authentication:** API key required

### Data Provided
- Live aircraft position data
- Global aircraft coverage
- Minimal aircraft filtering
- Higher data completeness in many regions

### Update Frequency
- Near real-time

### Strengths
- Stronger coverage in African airspace
- Fewer blocked or anonymized aircraft
- Better redundancy for ingestion pipelines

### Limitations
- Paid service (free tier may be limited)
- API key management required

### Usage in This Platform
- Coverage enhancement provider
- Redundancy source for ingestion reliability
- Preferred source where coverage is superior

---

## 3. Provider Selection Strategy

The platform supports multiple ADS-B providers to:
- Improve geographic coverage across Africa
- Reduce data loss due to outages or rate limits
- Enable source comparison and validation

During ingestion, records are tagged with their source to preserve lineage.

---

**Status:** Registered  
**Phase:** Phase 1 – Data Sources  
**Layer:** Ingestion
