import geopandas as gpd
from pathlib import Path
from shapely.geometry import Point



def load_state_boundaries(shapefile):
    """
    Load US state boundaries from shapefile
    
    Returns:
        GeoDataFrame: State boundary geometries
    """
    SHAPEFILE_PATH = shapefile
    return gpd.read_file(SHAPEFILE_PATH)


def get_state_boundary(shapefile_path, state_name):
    """
    Get boundary geometry for a specific state
    
    Args:
        state_name (str): Full state name (e.g., 'California', 'Texas')
    
    Returns:
        GeoSeries: State boundary geometry
    """
    gdf = load_state_boundaries(shapefile)
    #gdf = gdf.to_crs(epsg=4326) 

    #return gdf.geometry.iloc[0]
    return gdf[gdf['NAME'] == state_name].geometry.iloc[0]


def get_state_bbox(shapefile, state_name):
    """
    Get bounding box for a specific state
    
    Args:
        state_name (str): Full state name (e.g., 'California', 'Texas')
    
    Returns:
        dict: Bounding box coordinates (minlon, maxlon, minlat, maxlat)
    """
    geometry = get_state_boundary(shapefile, state_name)
    bounds = geometry.bounds
    
    return {
        'minlongitude': bounds[0],
        'maxlongitude': bounds[2],
        'minlatitude': bounds[1],
        'maxlatitude': bounds[3]
    }


def get_usgs_location_params(shapefile, state_name):
    """
    Get location parameters formatted for USGS API
    
    Args:
        state_name (str): Full state name (e.g., 'California', 'Texas')
    
    Returns:
        dict: USGS API location parameters
    """
    bbox = get_state_bbox(shapefile, state_name)
    
    return {
        'minlatitude': bbox['minlatitude'],
        'maxlatitude': bbox['maxlatitude'],
        'minlongitude': bbox['minlongitude'],
        'maxlongitude': bbox['maxlongitude']
    }


def get_available_states(shapefile):
    """
    Get list of available state names from shapefile
    
    Returns:
        list: State names
    """
    gdf = load_state_boundaries(shapefile )
    #gdf = gdf.to_crs(epsg=4326)
    return gdf['NAME'].sort_values().tolist()


def filter_earthquakes_by_state(shapefile, earthquake_df, state_name, lat_col='latitude', lon_col='longitude'):
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
    geometry = get_state_boundary(shapefile, state_name)
    
    # Create Point geometries from earthquake coordinates
    points = [Point(lon, lat) for lon, lat in zip(earthquake_df[lon_col], earthquake_df[lat_col])]
    
    # Check which points are within the state boundary
    within_state = [point.within(geometry) for point in points]
    
    # Filter DataFrame
    filtered_df = earthquake_df[within_state].copy()
    
    return filtered_df
