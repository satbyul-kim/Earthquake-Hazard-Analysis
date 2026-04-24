"""
Turn earthquake-level data into county-level hazard measures.

"""
import math
import numpy as np
import pandas as pd
from pathlib import Path


# Configuration paramters
STATE = "California"
START_TIME = "2005-01-01"
END_TIME = "2026-01-01"
MIN_MAGNITUDE = 3.5
minmag_str = str(MIN_MAGNITUDE).replace(".", "p")
threshold = 4.0 
comp_factor = 0.5

# Data path
OUTPUT_DIR = Path("outputs")
input_file = OUTPUT_DIR / f"{STATE}_earthquakes_with_county_{START_TIME}_{END_TIME}_{minmag_str}.csv"
output_file = OUTPUT_DIR / f"{STATE}_county_severity_{START_TIME}_{END_TIME}_{minmag_str}.csv"
COUNTY_SUMMARY = OUTPUT_DIR / f"{STATE}_county_hazard_metrics_{START_TIME}_{END_TIME}_{minmag_str}.csv"

# Read data
df_eq = pd.read_csv(input_file)
df_county_summary = pd.read_csv(COUNTY_SUMMARY)


# Calculate energy-aware weight
weight_list = []
for magnitude in df_eq["magnitude"]: 
    weight = math.pow(10, 1.5*(magnitude-threshold)*comp_factor)
    weight_list.append(weight)


# weight_list to datafram
df_weight = pd.DataFrame(weight_list, columns=["weight"])

# merge weight list to df_eq
df_eq = pd.concat([df_eq, df_weight], axis=1)

# sum weight by (groupby) county  
county_severity = (
    df_eq.groupby("NAME")["weight"]
    .mean()
    .reset_index(name="severity")
)

county_metrics = df_county_summary[["NAME", "total_event_count",  
    "annualized_frequency"]].merge(
     county_severity, on="NAME", how="left"
)

# Normalize each county's severity
severity_norm = []
smin = county_metrics["severity"].min()
smax = county_metrics["severity"].max()
if smin == smax:
    print("smax - smin = 0")
    severity_norm = [0.0] * len(county_metrics)   
else:
    for s in county_metrics['severity']: 
        sc = (s - smin) / (smax - smin)
        severity_norm.append(sc)
df_severity_norm = pd.DataFrame(severity_norm, columns=["severity_norm"])

# Normalize annulaized earthquake frequency
frequency_norm = []
fmin = county_metrics["annualized_frequency"].min()
fmax = county_metrics["annualized_frequency"].max()
if fmin == fmax:
    print("fmax - fmin = 0")
    frequency_norm = [0.0] * len(county_metrics)   
else:
    for af in county_metrics["annualized_frequency"]: 
        afc = (af - fmin) / (fmax - fmin)
        frequency_norm.append(afc)
df_frequency_norm = pd.DataFrame(frequency_norm, columns=["frequency_norm"])

hazard_score = np.array(severity_norm) + np.array(frequency_norm)
df_hazard_score = pd.DataFrame(hazard_score, columns=["hazard_score"])



severity_summary = pd.concat(
    [county_metrics,
    df_severity_norm,
    df_frequency_norm,
    df_hazard_score],
    axis=1
)

severity_summary.to_csv(output_file, index=False)
print(f"Saved: {output_file}")
