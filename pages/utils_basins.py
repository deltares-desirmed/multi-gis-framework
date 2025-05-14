# file: pages/utils_basins.py

import ee
from utils_ee import add_ee_layer

def get_european_basins_layer():
    """
    Returns a Google Earth Engine FeatureCollection layer of HydroSHEDS river basins filtered to Europe.
    """
    # Load HydroSHEDS Level 12 basins
    basins = ee.FeatureCollection("WWF/HydroSHEDS/v1/Basins/hybas_12")

    # Load country boundaries and filter to Europe
    europe = ee.FeatureCollection("USDOS/LSIB_SIMPLE/2017") \
        .filter(ee.Filter.eq("wld_rgn", "Europe"))

    # Filter basins to European region
    europe_basins = basins.filterBounds(europe)

    # Style visualization parameters
    vis_params = {
        "color": "808080",
        "strokeWidth": 1
    }

    return {
        "ee_object": europe_basins,
        "vis_params": vis_params,
        "name": "European River Basins"
    }
