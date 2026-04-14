# California Earthquake Hazard Analysis

This project is building toward earthquake hazard analytics. The current direction is to focus first on California, establish a strong hazard analysis foundation, then add one simple exposure layer and present the result as a relative risk-screening prototype rather than a full catastrophe model.

## Overview

The repository currently focuses on earthquake event retrieval, geographic filtering, and early mapping workflows for California. The longer-term goal is to extend this foundation into county-level hazard analysis and a simple exposure-adjusted screening workflow.

## Project Questions

- Where are earthquake events concentrated in California?
- Which counties show relatively higher hazard based on frequency and severity?
- How does that picture change when a simple exposure layer is added?

## Current Position

The repository currently contains the early ingestion and geographic filtering stage:

- `fetch_earthquake_data.py`
  Pulls California earthquake events from the USGS API, exports raw results, filters events to the actual state boundary, and saves boundary coordinates for mapping.
- `visualize_filter_comparison_pygmt.py`
  Produces a comparison map showing the difference between the USGS bounding-box query and state-boundary filtering.
- `src/data/location_params.py`
  Contains helper functions for state boundaries, USGS query bounds, and point-in-polygon filtering.

This is the base layer for the next project stages.

## Scope and Positioning

This project is not intended to estimate insured loss, expected loss, or full catastrophe-model output. It is designed as an interpretable screening workflow that demonstrates:

- data collection
- geospatial filtering
- county-level aggregation
- basic hazard scoring
- simple exposure integration
- clear insurance-oriented framing

## Data Sources

- USGS Earthquake Catalog API for earthquake event data
- U.S. Census data for county-level exposure metrics
- U.S. Census state and county boundary files for geographic filtering and mapping

