"""
PyGMT comparison: earthquake data before vs after state boundary filtering.
Plots California region with USGS API bounding box dimensions.
Uses pygmt_exam.py styling conventions.
"""

import pygmt
import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path
from src.data.location_params import (
     get_state_boundary,
     extract_boundary_coordinates,
)


STATE = "California"
START_TIME = "2005-01-01"
END_TIME = "2026-01-01"
MIN_MAGNITUDE = 3.5


OUTPUT_DIR = Path("outputs")
RAW_DATA_DIR = Path("data/raw")
minmag_str = str(MIN_MAGNITUDE).replace(".", "p")


# Data path
df_raw_file = Path("outputs") / f"{STATE}_earthquakes_raw_{START_TIME}_{END_TIME}_{minmag_str}.csv"
df_filtered_file = Path("outputs") / f"{STATE}_earthquakes_filtered_{START_TIME}_{END_TIME}_{minmag_str}.csv"

state_boundary_shapefile = Path("data/raw/state_boundaries") / "cb_2023_us_state_500k.shp"
county_boundary_shapefile = Path("data/raw/county_boundaries") / "CA_Counties.shp"

state_coords_file = Path("outputs") / f"{STATE}_boundary_coordinates.csv"
county_coords_file = OUTPUT_DIR/ f"{STATE}_county_coordinates.csv"

fig_file = OUTPUT_DIR/ f"{STATE}_eq_filter_comparison_{START_TIME}_{END_TIME}_{minmag_str}.jpg"

# Read data
df_raw = pd.read_csv(df_raw_file)
df_filtered = pd.read_csv(df_filtered_file)


# Extract county boundary coordinates
if state_coords_file.exists():
    state_coords = pd.read_csv(state_coords_file)
    state_boundary_xall = state_coords["longitude"].tolist()
    state_boundary_yall = state_coords["latitude"].tolist() 
    print(f"The state boundary file already exists")
else:
    state_gdf = get_state_boundary(state_boundary_shapefile, STATE)
    state_boundary_xall, state_boundary_yall = extract_boundary_coordinates(state_gdf)
    pd.DataFrame({
        "longitude": state_boundary_xall,
        "latitude": state_boundary_yall,
    }).to_csv(state_coords_file, index=False)
    print(f"The state boundary file is created")


# Extract county boundary coordinates
if county_coords_file.exists():
    county_coords = pd.read_csv(county_coords_file)
    county_boundary_xall = county_coords["longitude"].tolist()
    county_boundary_yall = county_coords["latitude"].tolist()
    print(f"The county boundary file already exists")
else:
    county_gdf = gpd.read_file(county_boundary_shapefile)
    county_gdf = county_gdf.to_crs("EPSG:4326")
    county_boundary_xall, county_boundary_yall = extract_boundary_coordinates(county_gdf)
    pd.DataFrame({
        "longitude": county_boundary_xall,
        "latitude": county_boundary_yall,
    }).to_csv(county_coords_file, index=False)
    print(f"The county boundary file is created")


region=[
    min(state_boundary_xall)-1, 
    max(state_boundary_xall)+1,
    min(state_boundary_yall)-1, 
    max(state_boundary_yall)+1,
]

bbox_x = [min(state_boundary_xall), 
          min(state_boundary_xall), 
          max(state_boundary_xall), 
          max(state_boundary_xall), 
          min(state_boundary_xall), 
]
bbox_y = [min(state_boundary_yall), 
          max(state_boundary_yall), 
          max(state_boundary_yall), 
          min(state_boundary_yall), 
          min(state_boundary_yall), 
]



time_label = f"Data: {START_TIME} to {END_TIME}"

bbox = np.array([bbox_x, bbox_y])
bbox_label = (
    f"USGS API Boundary: "
    f"{abs(min(bbox_x)):.1f}W-{abs(max(bbox_x)):.1f}W, "
    f"{min(bbox_y):.1f}N-{max(bbox_y):.1f}N"
)

PROJ = "M10.5c"

fig = pygmt.Figure()
pygmt.config(
    MAP_FRAME_TYPE="plain",
    MAP_TICK_LENGTH_PRIMARY="0.1",
    FONT_ANNOT_PRIMARY="Helvetica,9.5p",
    FONT_TITLE="Helvetica,15p",
    MAP_TITLE_OFFSET="3p",
    MAP_FRAME_PEN="1.p",
)


with fig.subplot(
    nrows=1, ncols=2, 
    subsize=("10.5c", "13c"), 
    margins="0.5c",
    region=region,
    projection=PROJ,
):    

    with fig.set_panel(0):
        fig.coast(
            region=region,
            projection=PROJ,
            frame=[f'WSne+tBefore Filter: Bounding Box (n={len(df_raw)})', "xa2f0.5", "ya2f0.5"],
            land="lightgray",
            water="lightcyan",
            borders="2/0.5p,gray40",
            shorelines="0.5p,gray40",
        )
        fig.plot(x=county_boundary_xall, y=county_boundary_yall, pen="0.5p,black")
        fig.plot(x=state_boundary_xall, y=state_boundary_yall, pen="1p,black")
        fig.plot(x=bbox_x, y=bbox_y, pen="1.2p,GRAY23,--")
        fig.plot(
            x=df_raw["longitude"], y=df_raw["latitude"],
            style="c0.15c", fill="GRAY40", transparency=30,
        )
        fig.text(
            x=region[0] + 0.3, y=region[3] - 0.4,
            text=bbox_label,
            font="7p,Helvetica,red", justify="BL",
        )
        fig.text(
            x=region[0] + 0.3, y=region[3] - 0.7,
            text=time_label,
            font="7p,Helvetica,black", justify="BL",
        )

    with fig.set_panel(1):
        fig.coast(
            region=region,
            projection=PROJ,
            frame=[f'WSne+t"After Filter: State Boundary (n={len(df_filtered)})"', "xa2f1", "ya2f1"],
            land="lightgray",
            water="lightcyan",
            borders="2/0.5p,gray40",
            shorelines="0.5p,gray40",
        )
        fig.plot(x=bbox_x, y=bbox_y, pen="1.2p,GRAY23,--")
        fig.plot(x=county_boundary_xall, y=county_boundary_yall, pen="0.5p,black")
        fig.plot(x=state_boundary_xall, y=state_boundary_yall, pen="1p,black")
        fig.plot(
            x=df_filtered["longitude"], y=df_filtered["latitude"],
            style="c0.15c", fill="red", transparency=30,
        )    
fig.savefig(fig_file, dpi=800)
print(f"\nSaved: {fig_file}")
    
