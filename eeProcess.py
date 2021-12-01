from tkinter import Image
import ee
from ee.imagecollection import ImageCollection
import numpy as np
import geemap as gmap
import geopandas as gpd

ee.Initialize()

SENTINEL_2 = 'COPERNICUS/S2_SR'
SENTINEL_3 = 'COPERNICUS/S3/OLCI'

BAND_NAMES = {SENTINEL_2 : ['B2', 'B3', 'B4', 'B5', 'B8', 'B11', 'B12'],
              SENTINEL_3 : ['Oa04_radiance','Oa06_radiance', 'Oa07_radiance', 'Oa08_radiance', 
                            'Oa10_radiance','Oa11_radiance', 'Oa17_radiance']}

CORRECTION_CONSTANTS_MUL = {SENTINEL_2 : [0.000031831, 0.000031831, 0.000031831, 0.000031831, 0.000031831, 0.000031831, 0.000031831],
                            SENTINEL_3 : [0.002249051, 0.002502631, 0.002698554, 0.002774391, 0.002853254, 0.002935211, 0.004166201]}

CORRECTION_CONSTANTS_ADD = {SENTINEL_2 : [-0.194049129, -0.118787228, -0.059274919, -0.046942779, -0.023536142, 
                                         -0.001667985, -0.001667985],
                            SENTINEL_3 : [-0.067762278, -0.038398972, -0.025656808, -0.019163534, -0.017303487, -0.015325608, -0.006226078]}
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
        self.sensor = sensor
        self.startDates = startDatelist
        self.endDates = endDatelist
        self.fp = roi
        self.shapeFile = gmap.shp_to_ee(roi)
        self.monthlyMedianImagesCCD = []
        self.TCCFlag = visParams['True Color']
        self.FCCFlag = visParams['False Color']
        self.monthlyMedianImagesTCC = []
        self.monthlyMedianImagesFCC = []
    
    def createMonthlyImages(self):
        '''
        This function creates a list of monthly median images based on the datelist and region of interest
        '''
        for i in range(len(self.startDates)):
            site = self.ImageCollection.filterBounds(self.shapeFile).filterDate(self.startDates[i], self.endDates[i])
            site = site.median()

            # atmospheric correction 
            bands = []
            for i in range(len(BAND_NAMES[self.sensor])):
                band = site.select(BAND_NAMES[self.sensor][i]).multiply(CORRECTION_CONSTANTS_MUL[self.sensor][i]).add(CORRECTION_CONSTANTS_ADD[self.sensor][i])
                bands.append(band)
            print(bands)

            image = ee.Image(bands)
            ccd = None
            if self.sensor == SENTINEL_2:
                ndci = image.normalizedDifference(['B5','B4']).select(['nd'],['ndvi'])
                chla = ndci.expression('14.039 + (86.115*ndci) + (194.325 * (ndci*ndci))', {'ndci': ndci}).select(['constant'],['chla'])
                ccd = chla.expression('(4989.55*chla) - 131742', {'chla':chla}).select(['constant'],['ccd'])
                print(ccd)
            elif self.sensor == SENTINEL_3:
                ss_681 = 
                

            
        
# s3 = ee.ImageCollection('COPERNICUS/S2_SR').filterDate()
# print(s3)