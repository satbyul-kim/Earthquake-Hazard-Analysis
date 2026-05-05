"""
Plot earthquake distribution in California with fault line information

"""
import numpy as np
import os, sys
import pygmt
import pandas as pd
import geopandas as gpd
from pathlib import Path

# Configuration parameters
STATE = "California"
START_TIME = "2005-01-01"
END_TIME = "2026-01-01"
MIN_MAGNITUDE = 3.5
minmag_str = str(MIN_MAGNITUDE).replace(".", "p")

AGE_FILTER = None 
INCLUDE_OFFSHORE = True

OUTPUT_DIR = Path("outputs")
RAW_DATA_DIR = Path("data/raw")

# Data path
QFAULT_GDB = RAW_DATA_DIR / "Qfaults_GIS/GDB/Qfaults_2020_WGS84.gdb"
COUNTY_COORD_FILE = OUTPUT_DIR / "California_county_coordinates.csv"
DF_EQ_FILE =  OUTPUT_DIR / f"{STATE}_earthquakes_filtered_{START_TIME}_{END_TIME}_{minmag_str}.csv"

age_str = AGE_FILTER.lower().replace(" ", "_") if AGE_FILTER else "all_ages"
offshore_str = "with_offshore" if INCLUDE_OFFSHORE else "onshore_only"
OUTPUT_FILE = OUTPUT_DIR / f"{STATE}_fault_lines_{age_str}.png"
COORDS_FILE = OUTPUT_DIR / f"{STATE}_fault_coordinates_{age_str}_{offshore_str}.csv"

def line_geometries_to_xy(geometries):
    """
    Convert line geometries to flat x/y arrays with NaN separators.

    The NaN separators prevent PyGMT from drawing false connections between
    separate fault segments.
    """
    x_all = []
    y_all = []

    for geom in geometries:
        if geom is None or geom.is_empty:
            continue

        if geom.geom_type == "LineString":
            x, y = geom.xy
            x_all.extend(x)
            y_all.extend(y)
            x_all.append(np.nan)
            y_all.append(np.nan)

        elif geom.geom_type == "MultiLineString":
            for part in geom.geoms:
                x, y = part.xy
                x_all.extend(x)
                y_all.extend(y)
                x_all.append(np.nan)
                y_all.append(np.nan)

    return x_all, y_all


def extract_fault_coordinates(gdf, source_name):
    """
    Extract longitude/latitude coordinates for each fault feature.

    Each row in the returned table is one vertex point from one fault line part.
    """
    records = []

    for feature_index, (_, row) in enumerate(gdf.iterrows()):
        geom = row.geometry

        if geom is None or geom.is_empty:
            continue

        if source_name == "onshore":
            fault_id = row.get("fault_id")
            fault_name = row.get("fault_name")
            age = row.get("age")
        else:
            fault_id = row.get("FAULT_ID")
            fault_name = row.get("FAULT_NAME")
            age = row.get("FLT_AGE")

        if geom.geom_type == "LineString":
            parts = [geom]
        elif geom.geom_type == "MultiLineString":
            parts = list(geom.geoms)
        else:
            continue

        for part_id, part in enumerate(parts):
            for point_order, (x_coord, y_coord) in enumerate(part.coords):
                records.append(
                    {
                        "source": source_name,
                        "feature_index": feature_index,
                        "part_id": part_id,
                        "point_order": point_order,
                        "fault_id": fault_id,
                        "fault_name": fault_name,
                        "age": age,
                        "longitude": x_coord,
                        "latitude": y_coord,
                    }
                )

    return pd.DataFrame(records)


def coordinates_df_to_xy(coords_df):
    """
    Convert cached fault coordinate rows into PyGMT-ready x/y arrays.
    """
    x_all = []
    y_all = []

    group_cols = ["feature_index", "part_id"]
    grouped = coords_df.sort_values(group_cols + ["point_order"]).groupby(group_cols)

    for _, part_df in grouped:
        x_all.extend(part_df["longitude"].tolist())
        y_all.extend(part_df["latitude"].tolist())
        x_all.append(np.nan)
        y_all.append(np.nan)

    return x_all, y_all


# Extract onshore fault lines
faults_onshore = gpd.read_file(QFAULT_GDB, layer="Qfaults_2020").to_crs("EPSG:4326")
faults_state = faults_onshore[faults_onshore["Location"] == "California"].copy()

if AGE_FILTER:
	fault_state = faults_state[faults_state["age"] == AGE_FILTER].copy()

# Extract offshore fault lines
faults_offshore = gpd.read_file(QFAULT_GDB, layer="California_Offshore").to_crs("EPSG:4326")


# Build or load cached fault coordinates
if COORDS_FILE.exists():
    fault_coords = pd.read_csv(COORDS_FILE)
    print(f"Fault coordinate file already exists: {COORDS_FILE}")
else:
    coords_frames = [extract_fault_coordinates(faults_state, "onshore")]
    if INCLUDE_OFFSHORE:
        coords_frames.append(extract_fault_coordinates(faults_offshore, "offshore"))
    
    fault_coords = pd.concat(coords_frames, ignore_index=True)
    fault_coords.to_csv(COORDS_FILE, index=False)
    print(f"Saved fault coordinates: {COORDS_FILE}")

#fault_xall, fault_yall = coordinates_df_to_xy(fault_coords)

#Convert cached coordinates to plotting arrays
onshore_coords = fault_coords[fault_coords["source"] == "onshore"].copy()
fault_onshore_x, fault_onshore_y = coordinates_df_to_xy(onshore_coords)

fault_offshore_x, fault_offshore_y = [], []
offshore_coords = pd.DataFrame()
if INCLUDE_OFFSHORE:
    offshore_coords = fault_coords[fault_coords["source"] == "offshore"].copy()
    fault_offshore_x, fault_offshore_y = coordinates_df_to_xy(offshore_coords)


# Read county boundary coordinate
county_coords = pd.read_csv(COUNTY_COORD_FILE)
county_boundary_xall = county_coords["longitude"].tolist()
county_boundary_yall = county_coords["latitude"].tolist()

# Read earthquake data
df_eq = pd.read_csv(DF_EQ_FILE)


region=[
    min(county_boundary_xall)-1,
    max(county_boundary_xall)+1,
    min(county_boundary_yall)-1,
    max(county_boundary_yall)+1,
]
df_eq["size"] = df_eq["magnitude"] * 0.025

fig = pygmt.Figure()
pygmt.config(
    MAP_FRAME_TYPE="plain",
    MAP_TICK_LENGTH_PRIMARY="0.1",
    FONT_ANNOT_PRIMARY="Helvetica,9.5p",
    FONT_TITLE="Helvetica,15p",
    MAP_TITLE_OFFSET="3p",
    MAP_FRAME_PEN="1.p",
)

title_parts = [STATE, "Fault Lines"]
if AGE_FILTER:
    title_parts.append(f"({AGE_FILTER})")

fig.coast(
    region=region,
    projection="M10.c",
    frame=[f'WSne+t"{ " ".join(title_parts) }"', "xa2f0.5", "ya2f0.5"],
    land="GRAY91",
    water="AZURE",
    borders="2/0.3p,gray70",
    shorelines="0.3p,gray70",
)
fig.plot(x=county_boundary_xall, y=county_boundary_yall, pen="0.3p,GRAY40")
#fig.plot(x=fault_xall, y=fault_yall, pen="0.1p,DARKRED")
fig.plot(x=fault_onshore_x, y=fault_onshore_y, pen="0.1p,DARKRED")
fig.plot(x=fault_offshore_x, y=fault_offshore_y, pen="0.1p,DARKRED")
#fig.plot(x=state_boundary_xall, y=state_boundary_yall, pen="1p,black")
fig.plot(
    x=df_eq["longitude"], y=df_eq["latitude"],
    style="cc", pen="0.1,GRAY20", size=df_eq["size"], fill="CYAN", transparency=30,
)

fig.savefig(OUTPUT_FILE, dpi=800)
print(f"\nSaved: {OUTPUT_FILE}")
