import numpy as np
import geopandas as gpd
from pathlib import Path
from shapely.geometry import Point



def load_state_boundaries(SHAPEFILE):
    """
    Load US state boundaries from SHAPEFILE
    
    Returns:
        GeoDataFrame: State boundary geometries
    """
    return gpd.read_file(SHAPEFILE)


def get_state_boundary(SHAPEFILE, state_name):
    """
    Get boundary geometry for a specific state
    
    Args:
        state_name (str): Full state name (e.g., 'California', 'Texas')
    
    Returns:
        GeoSeries: State boundary geometry
    """
    gdf = load_state_boundaries(SHAPEFILE)
    gdf = gdf.to_crs("EPSG:4326")

    #return gdf.geometry.iloc[0]
    return gdf[gdf['NAME'] == state_name].geometry.iloc[0]


def get_state_bbox(SHAPEFILE, state_name):
    """
    Get bounding box for a specific state
    
    Args:
        state_name (str): Full state name (e.g., 'California', 'Texas')
    
    Returns:
        dict: Bounding box coordinates (minlon, maxlon, minlat, maxlat)
    """
    geometry = get_state_boundary(SHAPEFILE, state_name)
    bounds = geometry.bounds
    
    return {
        'minlongitude': bounds[0],
        'maxlongitude': bounds[2],
        'minlatitude': bounds[1],
        'maxlatitude': bounds[3]
    }


def get_usgs_location_params(SHAPEFILE, state_name):
    """
    Get location parameters formatted for USGS API
    
    Args:
        state_name (str): Full state name (e.g., 'California', 'Texas')
    
    Returns:
        dict: USGS API location parameters
    """
    bbox = get_state_bbox(SHAPEFILE, state_name)
    
    return {
        'minlatitude': bbox['minlatitude'],
        'maxlatitude': bbox['maxlatitude'],
        'minlongitude': bbox['minlongitude'],
        'maxlongitude': bbox['maxlongitude']
    }


def get_available_states(SHAPEFILE):
    """
    Get list of available state names from SHAPEFILE
    
    Returns:
        list: State names
    """
    gdf = load_state_boundaries(SHAPEFILE )
    return gdf['NAME'].sort_values().tolist()


def filter_earthquakes_by_state(SHAPEFILE, earthquake_df, state_name, lat_col='latitude', lon_col='longitude'):
    """
    Filter earthquake data to only include earthquakes within actual state boundary
    
    Args:
        earthquake_df (DataFrame): Earthquake data with lat/lon columns
        state_name (str): Full state name (e.g., 'California', 'Texas')
        lat_col (str): Name of latitude column
        lon_col (str): Name of longitude column
    
    Returns:
        DataFrame: Filtered earthquake data within state boundary
    """
    geometry = get_state_boundary(SHAPEFILE, state_name)
    
    # Create Point geometries from earthquake coordinates
    points = [Point(lon, lat) for lon, lat in zip(earthquake_df[lon_col], earthquake_df[lat_col])]
    
    # Check which points are within the state boundary
    within_state = [point.within(geometry) for point in points]
    
    # Filter DataFrame
    filtered_df = earthquake_df[within_state].copy()
    
    return filtered_df


def _append_geom_coords(geom, x_all, y_all):
    if geom.geom_type == "Polygon":
        x, y = geom.exterior.xy
        x_all.extend(x)
        y_all.extend(y)
        x_all.append(np.nan)
        y_all.append(np.nan)

    elif geom.geom_type == "MultiPolygon":
        for poly in geom.geoms:
            x, y = poly.exterior.xy
            x_all.extend(x)
            y_all.extend(y)
            x_all.append(np.nan)
            y_all.append(np.nan)


def extract_boundary_coordinates(boundary_data):
    x_all = []
    y_all = []

    if hasattr(boundary_data, "iterrows"):
        for _, row in boundary_data.iterrows():
            _append_geom_coords(row.geometry, x_all, y_all) 

    else:
        _append_geom_coords(boundary_data, x_all, y_all) 

    return x_all, y_all
