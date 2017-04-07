if __name__ == '__main__':

    import rasterio
    import rasterprofiles as rp
    from shapely.geometry import  mapping
    from fiona import collection

    raster_path = 'rasters/seaice.tif'
    ras = rasterio.open(raster_path)
    source = (-2458163.34416485, 1190631.15419372)
    radius = 500000
    profiler = rp.RadialProfiler(ras)
    shapes = []
    for deg in range(0,360,1):
        profile = profiler.profile(source, radius, deg)
        shapes.append((profile.line,deg))
        print(profile)
    print("Creating shapefile of profiles")
    schema = {'geometry': 'LineString', 'properties': {'angle': 'int'}}
    with collection('rp_demo.shp', "w", "ESRI Shapefile", schema, crs=ras._crs) as output:
        for line in shapes:
            output.write({'geometry': mapping(line[0]),
                        'properties': {'angle': line[1]}})
