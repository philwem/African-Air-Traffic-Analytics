
# Naming Conventions

## African Air Traffic DataHouse & Analytics Platform

This document defines mandatory naming standards for all code, data, pipelines, and documentation within the African Air Traffic DataHouse & Analytics Platform.

These rules are **not optional**. Consistency is required to ensure scalability, maintainability, and auditability.

---

## 1. General Rules

* Use **lowercase only**
* Use **snake_case** for all names
* Names must be **descriptive and explicit**
* Avoid abbreviations unless they are aviation or data-industry standard
* UTC is the default time reference

---

## 2. Repository Naming

**Format:**

```
air-traffic-datahouse
```

Only one mono-repository is used for the platform.

---

## 3. Branch Naming

| Branch Type | Pattern               | Example                       |
| ----------- | --------------------- | ----------------------------- |
| Main        | main                  | main                          |
| Development | develop               | develop                       |
| Feature     | feature/<description> | feature/adsb_stream_ingestion |
| Bugfix      | bugfix/<description>  | bugfix/schema_validation      |
| Hotfix      | hotfix/<description>  | hotfix/pipeline_failure       |

---

## 4. Commit Message Convention

**Format:**

```
<type>: <short, clear description>
```

**Allowed Types:**

* feat – new functionality
* fix – bug fix
* docs – documentation only
* refactor – code restructuring without logic change
* test – adding or updating tests
* chore – tooling, configs, or cleanup

**Examples:**

```
feat: add adsb json schema
fix: handle null altitude values
```

---

## 5. Data Layer Naming

Each dataset must clearly declare its processing layer.

| Layer  | Prefix  | Description              |
| ------ | ------- | ------------------------ |
| Raw    | raw_    | Unmodified landing data  |
| Bronze | bronze_ | Validated but unfiltered |
| Silver | silver_ | Cleaned and enriched     |
| Gold   | gold_   | Analytics-ready          |

**Example:**

```
silver_flight_positions
```

---

## 6. Table Naming

**Format:**

```
<layer>_<entity>[_<granularity>]
```

**Examples:**

* bronze_adsb_messages
* silver_flights_hourly
* gold_airport_congestion_daily

---

## 7. Column Naming

* Use snake_case
* Include measurement units where applicable
* Avoid ambiguous names

**Examples:**

* aircraft_icao
* latitude_deg
* longitude_deg
* altitude_ft
* ground_speed_kt
* event_timestamp_utc

---

## 8. Pipeline & DAG Naming

**Format:**

```
<layer>_<source>_<frequency>
```

**Examples:**

* ingestion_adsb_streaming
* bronze_metadata_daily
* silver_transform_hourly

---

## 9. dbt Model Naming

| Model Type   | Prefix | Example            |
| ------------ | ------ | ------------------ |
| Staging      | stg_   | stg_adsb_positions |
| Intermediate | int_   | int_flight_tracks  |
| Mart / Gold  | mart_  | mart_airline_kpis  |

---

## 10. File Naming

* Configuration files: snake_case
* SQL files match model names

**Examples:**

* adsb_schema.json
* silver_flight_positions.sql

---

## 11. Environment Naming

| Environment | Name    |
| ----------- | ------- |
| Development | dev     |
| Staging     | staging |
| Production  | prod    |

---

## 12. Governance Rules

* Any new dataset must follow these conventions
* Breaking changes require documentation
* Non-compliant code or data will not be merged

---

## 13. Ownership

All contributors are responsible for enforcing naming standards.

Failure to comply introduces technical debt and will be corrected.

---

**Status:** Approved
