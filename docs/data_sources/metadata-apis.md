# Aircraft, Airline & Airport Metadata APIs
## African Air Traffic DataHouse & Analytics Platform

This document registers metadata APIs used to enrich ADS-B flight position data
with aircraft, airline, and airport context.

---

## 1. ADSBDB (adsbdb.com)

**Provider Type:** Aviation Metadata API  
**Access Method:** REST API  
**Authentication:** API key (if required)

### Data Provided
- Aircraft registration details
- Aircraft type and model
- Airline/operator information
- Airport reference data

### Usage in This Platform
- Enrich ADS-B flight records
- Populate dimension tables (aircraft, airline, airport)
- Enable airline and airport analytics

### Strengths
- Simple REST endpoints
- Clear mapping from ICAO24 to aircraft details

### Limitations
- Rate limits
- Metadata freshness depends on provider updates

---

## 2. Airport Reference Datasets (Open Data)

**Examples:**
- OurAirports
- OpenFlights

### Data Provided
- Airport codes (ICAO/IATA)
- Airport names and locations
- Country and region

### Usage in This Platform
- Airport dimension tables
- Geospatial mapping
- Regional aggregation

---

**Status:** Registered  
**Phase:** Phase 1 – Data Sources  
**Layer:** Ingestion
