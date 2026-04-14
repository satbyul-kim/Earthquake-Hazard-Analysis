import requests
import pandas as pd
import geopandas as gpd
import numpy as np
from src.data.location_params import (
    get_usgs_location_params, 
    filter_earthquakes_by_state,
)

STATE = "California"
START_TIME = "2020-01-01"
END_TIME = "2023-01-01"
MIN_MAGNITUDE = 2.5 
LIMIT = 20000
SHAPEFILE = "data/raw/state_boundaries/cb_2023_us_state_500k.shp"

# USGS API input 
url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
params = {
    "format": "geojson",
    "starttime": START_TIME,
    "endtime": END_TIME,
    "minmagnitude": MIN_MAGNITUDE,
    "limit": LIMIT 
}
params.update(get_usgs_location_params(SHAPEFILE, STATE))

# Add location parameters
print(f"Fetching earthquakes for {STATE}...")
response = requests.get(url, params=params)
data = response.json()


# Extract features
records = []
for feature in data["features"]:
    props = feature["properties"]
    geom = feature["geometry"]

    records.append({
        "id": feature["id"],
        "time": pd.to_datetime(props["time"], unit="ms"),
        "longitude": geom["coordinates"][0],
        "latitude": geom["coordinates"][1],
        "depth": geom["coordinates"][2],
        "magnitude": props["mag"],
        "place": props["place"]
    })

df = pd.DataFrame(records)
# Save CSV
df.to_csv(STATE+"_earthquakes_raw"+"_"+START_TIME+"_"+END_TIME+"_500k.csv", index=False)

# Filter data out of area 
df_filtered = filter_earthquakes_by_state(SHAPEFILE, df, STATE)

# Save CSV
df_filtered.to_csv(STATE+"_earthquakes_filtered"+"_"+START_TIME+"_"+END_TIME+"_500k.csv", index=False)

print(df.head())
print(f"\nTotal raw records: {len(df)}")
print(f"\nTotal filtered records: {len(df_filtered)}")


# Extract state boundary coordinates
boundary_data = gpd.read_file(SHAPEFILE)
boundary_state = boundary_data[boundary_data['NAME'] == STATE].geometry.iloc[0]

state_coords = []
for poly in boundary_state.geoms:
    # Add exterior coordinates
    state_coords.append(list(poly.exterior.coords))

flat_coords = []
for poly_array in state_coords:
    flat_coords.append(poly_array)
    flat_coords.append(np.array([[np.nan, np.nan]]))
final_state_coords = np.vstack(flat_coords)

state_coords_file = STATE + "_boundary_coordinates_500k.csv"
pd.DataFrame(final_state_coords).to_csv(state_coords_file, index=False, header=['longitude', 'latitude'], float_format='%.6f')
