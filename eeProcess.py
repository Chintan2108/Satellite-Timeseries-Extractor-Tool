from tkinter import Image
import ee
from ee.imagecollection import ImageCollection
import numpy as np
import geemap as gmap
import geopandas as gpd

ee.Initialize()

BAND_NAMES = {'COPERNICUS/S2_SR': ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12'],
              'COPERNICUS/S3/OLCI': ['Oa01_radiance', 'Oa02_radiance', 'Oa03_radiance', 'Oa04_radiance', 'Oa05_radiance',
                                     'Oa06_radiance', 'Oa07_radiance', 'Oa08_radiance', 'Oa09_radiance', 'Oa10_radiance',
                                     'Oa11_radiance', 'Oa12_radiance', 'Oa13_radiance', 'Oa14_radiance', 'Oa15_radiance',
                                     'Oa16_radiance', 'Oa17_radiance', 'Oa18_radiance', 'Oa19_radiance', 'Oa20_radiance',
                                     'Oa21_radiance']}

CORRECTION_CONSTANTS_MUL = {'COPERNICUS/S2_SR': [0.000031831],
                            'COPERNICUS/S3/OLCI': [0.003246954, 0.002771006, 0.002381239, 0.002249051, 0.002274838, 0.002502631,
                                                   0.002698554, 0.002774391, 0.002818037, 0.002853254, 0.002935211, 0.003210294,
                                                   0.003261249, 0.003282869, 0.003295718, 0.003450315, 0.004166201, 0.004287496,
                                                   0.004461182, 0.004827838, 0.005662301]}

CORRECTION_CONSTANTS_ADD = {'COPERNICUS/S2_SR': [0.194049129, 0.118787228, 0.059274919, 0.046942779, 0.023536142, 0.001667985, 0.001667985],
                            'COPERNICUS/S3/OLCI': [-0.175861231, -0.148593622, -0.107154561, -0.067762278, -0.05655162, -0.038398972,
                                                   -0.025656808, -0.019163534, -0.01813212, -0.017303487, -0.015325608, -0.011184426,
                                                   -0.011026669, -0.01078064, -0.01041702, -0.009728395, -0.006226078, -0.005660511,
                                                   -0.005430749, -0.004607572, -0.003075091]}
class EarthEngine:
    '''
    A class for all tasks earth-engine
    '''

    #constructor
    def __init__(self, sensor, startDatelist, endDatelist, roi, visParams):
        '''
        initializing variables
        '''
        self.ImageCollection = ee.ImageCollection(sensor)
        self.startDates = startDatelist
        self.endDates = endDatelist
        self.fp = roi
        # self.shapeFile = self.shp_to_eeGeometry(roi)
        self.shapeFile = gmap.shp_to_ee(roi)
        self.monthlyMedianImagesCCD = []
        self.TCCFlag = visParams['True Color']
        self.FCCFlag = visParams['False Color']
        self.monthlyMedianImagesTCC = []
        self.monthlyMedianImagesFCC = []

    def shp_to_eeGeometry(self, shapefilePath):
        '''
        This function converts shapefile to earth engine geometry 
        '''
        sf = gpd.read_file(shapefilePath)

        g = [i for i in sf.geometry]
        x,y = g[0].exterior.coords.xy
        cords = np.dstack((x,y)).tolist()

        return ee.Geometry.Polygon(cords)
    
    def createMonthlyImages(self):
        '''
        This function creates a list of monthly median images based on the datelist and region of interest
        '''
        for i in range(len(self.startDates)):
            site = self.ImageCollection.filterBounds(self.shapeFile).filterDate(self.startDates[i], self.endDates[i])
            site = site.median()
            
        
# s3 = ee.ImageCollection('COPERNICUS/S2_SR').filterDate()
# print(s3)