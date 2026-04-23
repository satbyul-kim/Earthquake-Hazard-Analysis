"""
Aggregate earthquake event data to the county level.

"""

import pandas as pd
import geopandas as gpd
from pathlib import Path

# Index
STATE = "California"
START_TIME = "2005-01-01"
END_TIME = "2026-01-01"
MIN_MAGNITUDE = 3.5

OUTPUT_DIR = Path("outputs")
RAW_DATA_DIR = Path("data/raw")
minmag_str = str(MIN_MAGNITUDE).replace(".", "p")

# Data path
data_file = OUTPUT_DIR / f"{STATE}_earthquakes_with_county_{START_TIME}_{END_TIME}_{minmag_str}.csv"
out_file = OUTPUT_DIR / f"{STATE}_county_hazard_metrics_{START_TIME}_{END_TIME}_{minmag_str}.csv" 



# Read eq earthquaek data
df_eq = pd.read_csv(data_file)

# Make sure time is datetime
df_eq["time"] = pd.to_datetime(df_eq["time"])
df_eq["year"] = df_eq["time"].dt.year

# Full list of years 
years = pd.DataFrame({"year": range(pd.to_datetime(START_TIME).year, pd.to_datetime(END_TIME).year + 1)})

# Full list of counties
counties = pd.DataFrame({"NAME": sorted(df_eq["NAME"].dropna().unique())})

# Event counts by county
df_county_year = (
    df_eq.groupby(["NAME", "year"])
    .size()
    .reset_index(name="event_count")
)

# Build the full county-year grid:
county_year_grid = counties.merge(years, how="cross")

# Merge observed counts onto that grid:
df_county_year_full = county_year_grid.merge(
    df_county_year, 
    on=["NAME", "year"],
    how="left",
)

# Fill missing counts with zero
df_county_year_full["event_count"] = df_county_year_full["event_count"].fillna(0)

# Annualized frequency by county
df_county_year_full = (
    df_county_year_full.groupby("NAME")["event_count"]
    .mean()
    .reset_index(name="annualized_frequency")
)

# Annual events for each county
df_county_annual = (
    df_county_year.groupby("NAME")["event_count"]
    .mean()
    .reset_index(name="annualized_frequency")
)

# Total county event counts
df_county_total = (
    df_eq.groupby("NAME")
    .size()
    .reset_index(name="total_event_count")
)

# Count events each year
df_county_year_wide = df_county_year.pivot(
    index="NAME",
    columns="year",
    values="event_count",
)

df_county_year_wide.columns = [
    f"event_count_in_{year}" for year in df_county_year_wide.columns
]

df_county_year_wide = df_county_year_wide.reset_index()


# Build county summary
df_county_summary = df_county_total.merge(
    df_county_annual, 
    on="NAME", 
    how="left",
) 

df_county_summary = df_county_summary.merge(
    df_county_year_wide,
    on="NAME",
    how="left",
)

# Add metadata columns
df_county_summary["state"] = STATE
df_county_summary["start_time"] = START_TIME
df_county_summary["end_time"] = END_TIME
df_county_summary["min_magnitude"] = MIN_MAGNITUDE


df_county_summary.to_csv(out_file, index=False)

print(f"Saved: {out_file}")
print(df_county_summary.head())
