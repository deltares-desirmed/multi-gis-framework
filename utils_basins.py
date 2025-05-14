import ee

# Make sure Earth Engine is initialized elsewhere (e.g., in utils_ee)

def get_basins():
    """
    Loads HydroSHEDS basins dataset filtered to the European region.

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
        "width": 1
    }


    layer_name = "EU River Basins"


  # utils_basins.py should return this:
    return european_basins, {"color": "808080", "width": 1}, "European River Basins"


