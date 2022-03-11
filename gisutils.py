import rasterio as rio
from rasterio.windows import from_bounds
from rasterio import features
import geopandas as gpd
import numpy as np


def read_raster(path,bands=1,crs=False,bounds=False,bbox=None):
    # From rasterio docs with modifications
    with rio.open(path) as dst:
        profile = dst.profile
        crs_val = dst.crs
        bounds_val = dst.bounds
        
        if bbox:
            window = from_bounds(bbox[0],bbox[1],bbox[2],bbox[3],profile['transform'])
            array = dst.read(bands,window=window)
            profile['height'], profile['width'] = array.shape
            profile['transform'] = rio.windows.transform(window,profile['transform'])
        else:
            array = dst.read(bands)
        # array = np.moveaxis(array,0,-1)
    
    result = [array, profile]

    if crs:
        result.append(crs_val)
    
    if bounds:
        result.append(bounds_val)

    return result

def get_raster_info(path,bbox=None):
    # From rasterio docs with modifications
    with rio.open(path) as dst:
        profile = dst.profile
        crs_val = dst.crs
        bounds_val = dst.bounds
        
        if bbox:
            window = from_bounds(bbox[0],bbox[1],bbox[2],bbox[3],profile['transform'])
            profile['height'], profile['width'] = array.shape
            profile['transform'] = rio.windows.transform(window,profile['transform'])

    return profile,crs_val,bounds_val


def write_raster(array,profile,out_path,nodata,dtype):
    # From rasterio docs:
    # Register GDAL format drivers and configuration options with a
    # context manager.
    with rio.Env():
        # And then change the band count to 1, set the
        # dtype to uint8, and specify LZW compression.
        profile.update(
            dtype=dtype,
            count=1,
            nodata=nodata,
            compress='lzw')

        with rio.open(out_path, 'w', **profile) as dst:
            dst.write(array.astype(dtype), 1)

    return out_path


def polygon_to_raster(gdf,template,value=1,crs=False):

    if isinstance(gdf,str):
        pol = gpd.read_file(gdf)
    else:
        pol = gdf
    
    if isinstance(gdf,str):
        with rio.open(template) as dst:
            template = dst.profile
            template_crs = dst.crs
            template_transform = template['transform']
            template_shape = dst.shape
    else:
        template_crs = template['crs']
        template_transform = template['transform']
        template_shape = (template['height'], template['width'])

    # if crs != pol.crs:
    #   raise Exception('CRSs do not match!')

    geojsons = [x['geometry'] for x in pol.geometry.__geo_interface__['features']]
    if isinstance(value,str):
        shapes = [tuple(x) for x in zip(geojsons,pol[value])]
    else:
        shapes = [(x,value) for x in geojsons]

    array = features.rasterize(shapes, out_shape=template_shape, transform=template_transform)
    
    result = [array, template]
    if crs:
        result.append(template_crs)

    return result