"""
PyGMT comparison: earthquake data before vs after state boundary filtering.
Plots California region with USGS API bounding box dimensions.
Uses pygmt_exam.py styling conventions.
"""

import pygmt
import pandas as pd
import numpy as np

STATE = "California"
START_TIME = "2020-01-01"
END_TIME = "2023-01-01"


df_raw_file = STATE+"_earthquakes_raw"+"_"+START_TIME+"_"+END_TIME+"_500k.csv"  
df_filtered_file = STATE+"_earthquakes_filtered"+"_"+START_TIME+"_"+END_TIME+"_500k.csv"
state_boundary_file = STATE+"_boundary_coordinates_500k.csv"


df_raw = pd.read_csv(df_raw_file)
df_filtered = pd.read_csv(df_filtered_file)
state_boundary = pd.read_csv(state_boundary_file)



region=[
    state_boundary["longitude"].min()-1, 
    state_boundary["longitude"].max()+1,
    state_boundary["latitude"].min()-1, 
    state_boundary["latitude"].max()+1,
]

bbox_x = [state_boundary["longitude"].min(), 
          state_boundary["longitude"].min(), 
          state_boundary["longitude"].max(), 
          state_boundary["longitude"].max(), 
          state_boundary["longitude"].min(), 
]
bbox_y = [state_boundary["latitude"].min(), 
          state_boundary["latitude"].max(), 
          state_boundary["latitude"].max(), 
          state_boundary["latitude"].min(), 
          state_boundary["latitude"].min(), 
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
        fig.plot(x=state_boundary['longitude'], y=state_boundary['latitude'], pen="1p,black")
        fig.plot(x=bbox_x, y=bbox_y, pen="1.5p,red,--")
        fig.plot(
            x=df_raw["longitude"], y=df_raw["latitude"],
            style="c0.15c", fill="red", transparency=30,
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
        fig.plot(x=state_boundary['longitude'], y=state_boundary['latitude'], pen="1.5p,black")
        fig.plot(x=bbox_x, y=bbox_y, pen="1.5p,darkgray,--")
        fig.plot(
            x=df_filtered["longitude"], y=df_filtered["latitude"],
            style="c0.15c", fill="blue", transparency=20,
        )
fig.savefig(STATE+"_eq_filter_comparison.jpg", dpi=800)
print(f"\nSaved: "+ STATE + "_eq_filter_comparison.jpg")
    
