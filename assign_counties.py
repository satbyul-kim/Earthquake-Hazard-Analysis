"""
Take each earthquake point and determine which California county it belongs to.

"""

import os, sys
import pandas as pd
import geopandas as gpd
from pathlib import Path
from src.data.location_params import get_state_boundary

# Index
STATE = "California"
START_TIME = "2005-01-01"
END_TIME = "2026-01-01"
MIN_MAGNITUDE = 3.5

OUTPUT_DIR = Path("outputs")
RAW_DATA_DIR = Path("data/raw")
minmag_str = str(MIN_MAGNITUDE).replace(".", "p")

# Data path
earthquake_file = OUTPUT_DIR / f"{STATE}_earthquakes_filtered_{START_TIME}_{END_TIME}_{minmag_str}.csv"
county_file = RAW_DATA_DIR / f"county_boundaries/CA_Counties.shp"
output_file = OUTPUT_DIR / f"{STATE}_earthquakes_with_county_{START_TIME}_{END_TIME}_{minmag_str}.csv"


# Read eq earthquaek data
df_eq = pd.read_csv(earthquake_file)
gdf_eq = gpd.GeoDataFrame(
    df_eq, 
    geometry=gpd.points_from_xy(df_eq.longitude, df_eq.latitude), 
    crs="EPSG:4326",
)

# Read earthquaek data
gdf_county = gpd.read_file(county_file).to_crs("EPSG:4326")


# Assign earthquakes in counties
gdf_joined = gpd.sjoin(
    gdf_eq,
    gdf_county,
    how="left",
    predicate="within",
)

# Set the header
df_output = gdf_joined[["id", "time", "longitude", "latitude", "magnitude", "depth", "place", "COUNTYFP", "GEOID", "NAMELSAD", "NAME"]]

# Save output
df_output.to_csv(output_file, index=False)

print(f"Saved: {output_file}")
print(df_output.head())
