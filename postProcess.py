from PIL import Image, ImageDraw, ImageFont
import os
import pandas as pd

class PostProcess:
    '''
    A class for all local tasks 
    '''
    # constructor 
    def __init__(self, ccdImages, ccdValues, GIFSpeed, outputDir):
        self.outpath = outputDir
        self.ccdImagesDir = ccdImages
        self.ccdValues = ccdValues
        self.fps = GIFSpeed
    
    def createGIF(self):
        '''
        This function: 1. adds text label of image date to individial ccd image; 2. stitches them together into a gif
        '''
        # reading the images
        img_names = os.listdir(self.ccdImagesDir)
        img_names = list(filter(lambda x: x.endswith('png'), img_names))
        img_names = sorted(img_names, key = lambda x: int(x.split('_')[0]))

        images = []
        for img_name in img_names:
            # read the image
            img = Image.open(os.path.join(self.ccdImagesDir, img_name))

            # add the label
            d = ImageDraw.Draw(img)
            fontParams = ImageFont.truetype('C:/Windows/Fonts/ARLRDBD.ttf', size=50)
            label = img_name.split('_')[1] + ' ' + img_name.split('_')[-1].split('.')[0]
            d.text((200,600), label, font=fontParams, fill=(0,0,0))

            # append the labelled image
            images.append(img)
        
        # save all labelled images as GIF
        images[0].save(fp = os.path.join(self.outpath, 'TSE_Animation.gif'), format = 'GIF', append_images = images, 
                       save_all = True, duration = self.fps*1000)
        
    def createTSPlot(self):
        '''
        Reads the ccd values and saves a timeseries plot 
        '''
        # read ccd values
        df = pd.read(self.ccdValues)

        # plot the timeseries
        ax = df.plot(df.keys()[0], df.keys()[1])
        ax.set_ylabel('Cyano_Cells/L')
        TSE_plot = ax.get_figure()

        # save the timeseries on local disk
        TSE_plot.savefig(os.path.join(self.outpath, 'TSE_Timeseries_Plot.png'))