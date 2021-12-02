from PIL import Image, ImageDraw, ImageFont
import os

class PostProcess:
    '''
    A class for all local tasks 
    '''
    # constructor 
    def __init__(self, ccdImages, ccdValues, GIFSpeed, outputDir):
        self.outpath = outputDir
        self.ccdImages = ccdImages
        self.ccdValues = ccdValues
        self.fps = GIFSpeed
    
    def createGIF(self):
        '''
        This function: 1. adds text label of image date to individial ccd image; 2. stitches them together into a gif
        '''
        