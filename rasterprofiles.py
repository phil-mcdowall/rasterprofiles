import math
import numpy as np
from shapely.geometry import LineString, mapping
from fiona import collection
from collections import OrderedDict

#TODO switch lines for great circles

def to_pix(xy, transform):
    return ~transform * xy


def to_world(xy, transform):
    return transform * xy


class Profile:
    def __init__(self, raster, start, end, values):
        self.start = start
        self.end = end
        self.values = values
        self.raster = raster
        self.line = LineString([self.start, self.end])
        # TODO self.distances (list of distances for vals)

    def to_shapefile(self, path):
        schema = {'geometry': 'LineString', 'properties': {'len': 'int'}}
        with collection(path, "w", "ESRI Shapefile", schema, crs=self.raster._crs) as output:
            output.write({'geometry': mapping(self.line),
                          'properties': {'len': len(self.values)}})


    def __repr__(self):
        return "Raster Profile ({} to {}). {} values".format(self.start, self.end, len(self.values))


class Profiler:
    def __init__(self, raster):
        self.transform = raster.affine
        self.raster = raster
        self.data = raster.read()[0]

    def profile_indices(self, start, end, coordtype='world'):
        '''
        :param start: tuple of x,y of start point in world or pix coords
        :param end: tuple of x, y of end point in world or pix coords
        :param coordtype: str, 'world' geographic coords (in same crs) or 'pix' coords in image space
        :return: tuple x,y coords of cells between start and end
        '''

        # Convert coords to pix space
        if coordtype == 'world':
            start = to_pix(start, self.transform)
            end = to_pix(end, self.transform)
        source_x, source_y = start
        target_x, target_y = end

        # Sampling frequency along line start->end
        freq = 10000
        #TODO estimate suitable sampling frequency (too small -missed pix,too large - slow)

        # Get pixel index along line
        x, y = np.linspace(source_x, target_x, freq), np.linspace(source_y, target_y, freq)

        # Remove duplicates while keeping order
        output = list(OrderedDict.fromkeys(zip(x.astype(np.int),y.astype(np.int))))
        x = np.array([xy[0] for xy in output])
        y = np.array([xy[1] for xy in output])

        return x, y

    # TODO return distance to each cell

    def profile(self, start, end, coordtype='world'):
        '''
        :param start: tuple of x,y of start point in world or pix coords
        :param end: tuple of x, y of end point in world or pix coords
        :param coordtype: str, 'world' geographic coords (in same crs) or 'pix' coords in image space
        :return: Profile object
        '''
        inds = self.profile_indices(start, end, coordtype)
        return Profile(raster=self.raster, start=start, end=end, values=self.data[inds])


class RadialProfiler(Profiler):
    def __init__(self, raster):
        super().__init__(raster=raster)

    def profile_indices(self, start, distance, degrees, coordtype='world'):

        # Calculate end point
        theta = math.radians(degrees)
        self.source_x, self.source_y = start
        self.target_x = self.source_x + distance * math.cos(theta)
        self.target_y = self.source_y + distance * math.sin(theta)

        return super(RadialProfiler, self).profile_indices((self.source_x, self.source_y), (self.target_x, self.target_y), coordtype)

    def profile(self, start, distance, degrees, coordtype='world'):
        inds = self.profile_indices(start, distance, degrees, coordtype)
        return Profile(raster=self.raster, start=start, end=(self.target_x,self.target_y), values=self.data[inds])




