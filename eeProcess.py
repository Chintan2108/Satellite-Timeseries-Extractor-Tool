import ee
import geemap as gmap

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
        self.ccdImages = './local/utah/'
        self.ccdValues = './local/utah/ccd.csv'
        self.shapeFile = gmap.shp_to_ee(roi)
        self.monthlyMedianImagesCCD = []
        self.TCCFlag = visParams['True Color']
        self.FCCFlag = visParams['False Color']
    
    def createMonthlyImages(self):
        '''
        This function creates a list of monthly median images based on the datelist and region of interest
        '''
        for i in range(len(self.startDates)):
            site = self.ImageCollection.filterBounds(self.shapeFile).filterDate(self.startDates[i], self.endDates[i]).select(BAND_NAMES[self.sensor])
            site = site.median()

            if self.sensor == SENTINEL_3:
                bandCast = {}
                for key in BAND_NAMES[self.sensor]:
                    bandCast[key] = 'int'
                site = site.cast(bandCast, BAND_NAMES[self.sensor])

            # atmospheric correction 
            bands = []
            for i2 in range(len(BAND_NAMES[self.sensor])):
                band = site.select(BAND_NAMES[self.sensor][i2]).multiply(CORRECTION_CONSTANTS_MUL[self.sensor][i2]).add(CORRECTION_CONSTANTS_ADD[self.sensor][i2])
                bands.append(band)
            # have a boa surface reflectance image
            image = ee.Image(bands)

            # calculate ccd 
            ccd = None
            if self.sensor == SENTINEL_2:
                ndci = image.normalizedDifference(['B5','B4']).select(['nd'],['ndvi'])
                chla = ndci.expression('14.039 + (86.115*ndci) + (194.325 * (ndci*ndci))', {'ndci': ndci}).select(['constant'],['chla'])
                ccd = chla.expression('(4989.55*chla) - 131742', {'chla':chla}).select(['constant'],['ccd'])
            elif self.sensor == SENTINEL_3:
                ss_681 = bands[4].expression('b10 - b8 - (b11 - b8)*0.3636', {'b10': bands[4], 'b8': bands[3], 'b11':bands[5]})
                ci_681 = ss_681.expression('-1*ss_681', {'ss_681':ss_681}).select(['constant'],['CyanoIndex'])
                ss_665 = bands[4].expression('b8 - b7 - (b7 - b10)*0.7377', {'b8': bands[3], 'b7': bands[2], 'b10': bands[4]})
                ci_665 = ss_665.expression('-1*ss_665', {'ss_665':ss_665}).select(['constant'],['CIFlag'])
                pc_mask = ci_665.gt(0)
                ccd = ci_681.expression('1.0*100000000*ci', {'ci':ci_681}).select(['constant'],['ccd'])
                ccd = ccd.multiply(pc_mask)

            self.monthlyMedianImagesCCD.append(ccd)