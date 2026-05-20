"""
Plot a California county choropleth map using hazard score.

Inputs:
- outputs/California_county_severity_2005-01-01_2026-01-01_3p5.csv
- data/raw/county_boundaries/CA_Counties.shp

Output:
- draft/California_hazard_score_choropleth_2005-01-01_2026-01-01_3p5.png
"""

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from shapely.geometry import LineString
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

STATE = "California"
START_TIME = "2005-01-01"
END_TIME = "2026-01-01"
MIN_MAGNITUDE = 3.5
TOP_N = 10

ROOT_DIR = Path(__file__).resolve().parents[0]
OUTPUT_DIR = ROOT_DIR / "outputs"
RAW_DATA_DIR = ROOT_DIR / "data/raw"

minmag_str = str(MIN_MAGNITUDE).replace(".", "p")

METRICS_FILE = OUTPUT_DIR / f"{STATE}_county_severity_{START_TIME}_{END_TIME}_{minmag_str}.csv"
COUNTY_SHP = RAW_DATA_DIR / "county_boundaries/CA_Counties.shp"
FAULT_COORDS_FILE = OUTPUT_DIR / f"{STATE}_fault_coordinates_all_ages_with_offshore.csv"
FIGURE_FILE = OUTPUT_DIR / f"{STATE}_hazard_score_choropleth_{START_TIME}_{END_TIME}_{minmag_str}.png"


df_metrics = pd.read_csv(METRICS_FILE)
gdf_counties = gpd.read_file(COUNTY_SHP)
gdf_plot = gdf_counties.merge(df_metrics, on="NAME", how="left")
metric_specs = [
    {
        "column": "annualized_frequency",
        "title": f"Annual Frequency",
        "xlabel": "Annualized frequency",
        "cmap": "YlOrRd",
        "fmt": "{:.2f}",
    },
    {
        "column": "hazard_score",
        "title": f"Hazard Score",
        "xlabel": "Hazard score",
        "cmap": "YlOrRd",
        "fmt": "{:.3f}",
    },
    {
        "column": "severity",
        "title": f"Severity Metric",
        "xlabel": "Severity",
        "cmap": "YlOrRd",
        "fmt": "{:.3f}",
    },
]

def top_n_counties(df, metric_name):
    """
    Return the top N counties for a given metric, ordered for barh plotting.
    """
    return df.nlargest(TOP_N, metric_name).sort_values(metric_name, ascending=True)  

 

fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(24, 11), constrained_layout=True)
fig.suptitle(
    f"{STATE} Top County Rankings",
    #f"{STATE} Top County Rankings, {START_TIME} to {END_TIME}, {MIN_MAGNITUDE}+",
    fontsize=25,
    fontweight="bold"
)
for ax, spec in zip(axes, metric_specs):
    #top_df = top_n_counties(df, spec["column"])
    cax = inset_axes(ax, 
          width="3%", height="40%", 
          loc='lower left', 
          bbox_to_anchor=(0.08, 0.05, 1, 1), 

          bbox_transform=ax.transAxes)

    print(spec["column"])
    gdf_plot.plot(
        column=spec["column"],
        cmap=spec["cmap"],
        linewidth=0.5,
        edgecolor="white",
        legend=True,
        missing_kwds={
            "color": "lightgray",
            "edgecolor": "white",
            "label": "No {xlabel}",
        },
        legend_kwds={
            "label": spec["xlabel"],
            "shrink": 0.72,
            "orientation": "vertical"
        },
        ax=ax,
        cax=cax,
    )
    ax.set_title(spec["title"], fontsize=16, pad=1)
    ax.set_axis_off()

    # Inset axes 
    top_df = top_n_counties(df_metrics, spec["column"])
    inset_ax = inset_axes(ax, 
                          width="40%", 
                          height=2, 
                          loc="upper right",
                          bbox_to_anchor=(-0.01, -0.05, 1, 1), 
                          bbox_transform=ax.transAxes)
    inset_ax.barh(
              top_df["NAME"],
              top_df[spec["column"]],
              color="gray",
              edgecolor="white",
              linewidth=0.6,
              alpha=0.9,
          )

    inset_ax.set_title("Top 10", fontsize=11, pad=5, loc='left')
    inset_ax.set_ylabel("")
    inset_ax.spines[['top', 'right']].set_color('white')
    xmax = float(top_df[spec["column"]].max())
    inset_ax.set_xlim(0, xmax * 1.18)
    for value, county in zip(top_df[spec["column"]], top_df["NAME"]):
        inset_ax.text(
            value + xmax * 0.02,
            county,
            spec["fmt"].format(value),
            va="center",
            ha="left",
            fontsize=8,
        )



plt.savefig(FIGURE_FILE, dpi=300, bbox_inches="tight")
print(f"Saved: {FIGURE_FILE}")
