# rasterprofiles
Python 3.5


Extract raster cell values along linear transects.

Rasters should be loaded using rasterio.read().

`rasterprofiles.Profiler(raster).profile(start, end)` - raster cell values between start point and end point.

`rasterprofiles.RadialProfiler(raster).profile(start,distance,degrees)` - raster cell values from start point along line of 
length `distance` at angle `degrees`.

For indicies of cells (rather than values) use `.profile_indicies(args)`


