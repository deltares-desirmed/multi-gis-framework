# file: pages/utils_basins.py

import ee

# Make sure Earth Engine is initialized elsewhere (e.g., in utils_ee)


def get_river_basins_layer():
    """
    Loads HydroSHEDS basins dataset filtered to European region.

    Returns:
        tuple: (ee_object, vis_params, name)
    """
    # Load global river basin dataset
    dataset = ee.FeatureCollection("WWF/HydroSHEDS/v1/Basins/hybas_12")

    # Load global region boundaries and filter to Europe
    europe = ee.FeatureCollection("USDOS/LSIB_SIMPLE/2017").filter(
        ee.Filter.eq("wld_rgn", "Europe")
    )

    # Filter river basins that intersect Europe
    european_basins = dataset.filterBounds(europe.geometry())

    # Visualization settings
    vis_params = {
        "color": "808080",
        "strokeWidth": 1
    }

    layer_name = "HydroSHEDS River Basins (Europe)"

    return european_basins, vis_params, layer_name
